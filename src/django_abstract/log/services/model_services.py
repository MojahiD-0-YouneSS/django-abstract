from django.core.cache import cache
from django.utils import timezone

from django_abstract.base.base_model_service import BaseModelService
from django_abstract.registry import (
    service_settings,
    ServiceSettings,
    action_method_fields,
    register_service
)
from django_abstract.log.dependencies import AbstractLoggingDependency


@register_service()
class ErrorLogModelService(BaseModelService):
    """
    Built-in Framework Service for managing SystemErrorLog.
    Handles high-throughput logging by caching logs in Redis
    and flushing to the DB in bulk.
    """

    model_dependency = AbstractLoggingDependency()
    model_slug = "system_error_log"

    def __init__(self, session_key=None, *args, **db_fields):
        # Logs don't inherently require a session_key to exist in the DB,
        # but we track who caused the error.
        super().__init__(
            session_key=session_key, *args, include_session=False, **db_fields
        )
        self.cache_key = "dja_system_error_logs"
        self.init_state_hook()

    class LogValidator(BaseModelService.BaseServiceValidator):

        @service_settings(
            settings=ServiceSettings(
                VALID_FIELDS_PER_ACTION={
                    "log_error": [
                        "method_name",
                        "error_message",
                        "severity",
                        "actor_id",
                    ],
                    "flush_logs": [],
                }
            )
        )
        def meta_hook(self, settings):
            self.proxy_register()

        def proxy_register(self):
            self.regester_method("log_error", self.log_error)
            self.regester_method("flush_logs", self.flush_logs)

        @action_method_fields("method_name", "error_message", "severity", "actor_id")
        def log_error(self, method_name, error_message, severity, actor_id):
            """Queues a log in cache, flushing to DB if the queue gets too large."""

            log_entry = {
                "method_name": method_name,
                "message": str(error_message),
                "severity": severity,
                "reported_by_id": actor_id,  # Extracted from Entry.control by the Operator
            }

            # 1. Fetch current queue from Cache
            current_logs = cache.get(self.parent_service.cache_key, [])
            current_logs.append(log_entry)

            # 2. Smart routing (Cache vs DB)
            if len(current_logs) >= 50 or severity == "CRITICAL":
                # Flush immediately if queue is full or error is critical
                self.parent_service.access_db_objects.bulk_create(
                    [self.parent_service.model_class(**log) for log in current_logs]
                )
                cache.delete(self.parent_service.cache_key)
            else:
                # Otherwise, just update the cache
                cache.set(self.parent_service.cache_key, current_logs, timeout=3600)

            self.behavior.service_data.update({"log_queued": True})

        def flush_logs(self):
            """Forces a write of all cached logs to the database."""
            current_logs = cache.get(self.parent_service.cache_key, [])
            if current_logs:
                self.parent_service.access_db_objects.bulk_create(
                    [self.parent_service.model_class(**log) for log in current_logs]
                )
                cache.delete(self.parent_service.cache_key)

            self.behavior.service_data.update({"flushed_count": len(current_logs)})

@register_service()
class SystemErrorLogModelService(BaseModelService):
    """Handles high-throughput application error logging with Redis queuing."""

    model_dependency = AbstractLoggingDependency()
    model_slug = "system_error_log"

    def __init__(self, session_key=None, *args, **db_fields):
        super().__init__(
            session_key=session_key, *args, include_session=False, **db_fields
        )
        self.cache_key = "dja_system_error_logs"
        self.init_state_hook()

    class LogValidator(BaseModelService.BaseServiceValidator):
        @service_settings(
            settings=ServiceSettings(
                VALID_FIELDS_PER_ACTION={
                    "log_error": [
                        "method_name",
                        "error_message",
                        "severity",
                        "actor_id",
                    ],
                    "flush_logs": [],
                }
            )
        )
        def meta_hook(self, settings):
            self.proxy_register()

        def proxy_register(self):
            self.regester_method("log_error", self.log_error)
            self.regester_method("flush_logs", self.flush_logs)

        @action_method_fields("method_name", "error_message", "severity", "actor_id")
        def log_error(self, method_name, error_message, severity, actor_id):
            log_entry = {
                "method_name": method_name,
                "message": str(error_message),
                "severity": severity,
                "reported_by_id": actor_id,
            }

            current_logs = cache.get(self.parent_service.cache_key, [])
            current_logs.append(log_entry)

            if len(current_logs) >= 50 or severity == "CRITICAL":
                self.parent_service.access_db_objects.bulk_create(
                    [self.parent_service.model_class(**log) for log in current_logs]
                )
                cache.delete(self.parent_service.cache_key)
            else:
                cache.set(self.parent_service.cache_key, current_logs, timeout=3600)

            self.behavior.service_data.update(
                {"log_status": "queued" if len(current_logs) < 50 else "flushed"}
            )

        def flush_logs(self):
            current_logs = cache.get(self.parent_service.cache_key, [])
            if current_logs:
                self.parent_service.access_db_objects.bulk_create(
                    [self.parent_service.model_class(**log) for log in current_logs]
                )
                cache.delete(self.parent_service.cache_key)
            self.behavior.service_data.update({"flushed_count": len(current_logs)})

@register_service()
class SessionMetricsModelService(BaseModelService):
    """
    Tracks session durations and path hits.
    Crucial for analytics, but highly cached to prevent DB blocking.
    """

    model_dependency = AbstractLoggingDependency()
    model_slug = "session_metrics"

    def __init__(self, session_key=None, *args, **db_fields):
        super().__init__(
            session_key=session_key, *args, include_session=True, **db_fields
        )
        self.init_state_hook()

    class MetricsValidator(BaseModelService.BaseServiceValidator):
        @service_settings(
            settings=ServiceSettings(
                VALID_FIELDS_PER_ACTION={
                    "record_hit": ["path", "ip_address"],
                    "end_session": [],
                }
            )
        )
        def meta_hook(self, settings):
            self.proxy_register()

        def proxy_register(self):
            self.regester_method("record_hit", self.record_hit)
            self.regester_method("end_session", self.end_session)

        @action_method_fields("path", "ip_address")
        def record_hit(self, path, ip_address):
            # 1. Update fast cache metrics (avoids hitting Postgres on every page load)
            cache_key = f"metrics_{self.parent_service.session_key}"
            metrics = cache.get(cache_key, {"hits": 0, "paths": [], "ip": ip_address})

            metrics["hits"] += 1
            if path not in metrics["paths"]:
                metrics["paths"].append(path)

            cache.set(cache_key, metrics, timeout=86400)  # Expire in 24h
            self.behavior.service_data.update({"metrics_updated": True})

        def end_session(self):
            # 2. When the session ends (or daily cron), flush the cache to DB
            cache_key = f"metrics_{self.parent_service.session_key}"
            metrics = cache.get(cache_key)

            if metrics:
                metric_record, created = (
                    self.parent_service.access_db_objects.get_or_create(
                        session_key=self.parent_service.session_key,
                        defaults={
                            "ip_address": metrics["ip"],
                            "start_time": timezone.now(),
                        },
                    )
                )
                metric_record.total_hits += metrics["hits"]
                metric_record.end_time = timezone.now()
                metric_record.save()

                cache.delete(cache_key)
                self.behavior.service_data.update({"session_finalized": True})

@register_service()
class BannedUserModelService(BaseModelService):
    """Manages Security and Access Denial at the database layer."""

    model_dependency = AbstractLoggingDependency()
    model_slug = "banned_user"

    def __init__(self, session_key=None, *args, **db_fields):
        super().__init__(
            session_key=session_key, *args, include_session=False, **db_fields
        )
        self.init_state_hook()

    class BanValidator(BaseModelService.BaseServiceValidator):
        @service_settings(
            settings=ServiceSettings(
                VALID_FIELDS_PER_ACTION={
                    "ban_identity": ["identifier", "reason", "is_ip"],
                    "check_ban": ["identifier"],
                }
            )
        )
        def meta_hook(self, settings):
            self.proxy_register()

        def proxy_register(self):
            self.regester_method("ban_identity", self.ban_identity)
            self.regester_method("check_ban", self.check_ban)

        @action_method_fields("identifier", "reason", "is_ip")
        def ban_identity(self, identifier, reason, is_ip):
            ban_record, created = (
                self.parent_service.access_db_objects.update_or_create(
                    identifier=identifier,  # Could be User ID or IP address
                    defaults={"reason": reason, "is_ip": is_ip, "is_active": True},
                )
            )
            # Instantly update a global cache flag so the Operator doesn't have to query the DB
            cache.set(f"banned_{identifier}", True, timeout=86400)
            self.behavior.service_data.update(
                {"banned": True, "record_id": ban_record.id}
            )

        @action_method_fields("identifier")
        def check_ban(self, identifier):
            # Extremely fast check used by the Security Operator
            is_banned = cache.get(f"banned_{identifier}")

            if is_banned is None:  # Cache miss
                is_banned = self.parent_service.access_db_objects.filter(
                    identifier=identifier, is_active=True
                ).exists()
                cache.set(f"banned_{identifier}", is_banned, timeout=3600)

            self.behavior.service_data.update({"is_banned": is_banned})
