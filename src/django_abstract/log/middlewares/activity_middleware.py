import uuid
from datetime import datetime
from django.utils.timezone import now
from django_abstract.log.services.creators_dependency import get_creator_manager
from django_abstract.utilities import ClassInfoProvider
from django_abstract.log.utilities import ErrorSuccessLogger

logger=ErrorSuccessLogger()

class RequestLoggingMiddleware(ClassInfoProvider):
    """
    Middleware that captures every request and logs it to the 
    django_abstract.GenericActivityLog table.
    
    Replaces the old 'log_manager' system with direct DB writes.
    """
    
    _EXCLUDED_PATHS = ['/admin', '/static', '/media', '/favicon.ico']
    
    def __init__(self, get_response):
        super().__init__()
        self.get_response=get_response
        self.log_manager = get_creator_manager()
        # self.info = .resolve_class_info(obj=self)
    def __call__(self, request, *args, **kwargs):
        response = self.get_response(request)
        session_key = request.session.session_key or self.insure_session(request.session)
        print("RequestLoggingMiddleware is running!")
        if not any(request.path.startswith(path) for path in self._EXCLUDED_PATHS):
            try:
                # raise Exception()
                self.log_request(request, response)
            except Exception as e:
                logger.logging_check(
                    service_data=self.get_class_info(),
                    operation='Visited page',
                    error_message=f"middleware logging error or user with session : {session_key}",
                    )
                print(f"Logging Failed: {e}")
        return response
    
    def insure_session(self,session):
        if not session.session_key:
            try:
                session.save()
            except Exception:
                pass # Session engine might not be configured

    def anonymize_ip(self, ip):
        """
        Masks the last octet of an IPv4 address to protect user privacy.
        Example: 192.168.1.50 -> 192.168.1.0
        """
        if not ip: return None
        if "." in ip: # IPv4
            return ".".join(ip.split(".")[:-1]) + ".0"
        return ip # IPv6 is harder, often just truncated

    def log_request(self, request, response):
        """
        Maps request data to the GenericActivityLog model.
        """
        # A. Resolve User
        user = None
        if hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user
        print('(ovo)')
        # B. Resolve IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')

        # C. Resolve JSON Details
        # Instead of 20 separate columns (product_id, cart_id...), we dump 
        # context into the JSON field. This makes the logger generic.
        details = {
            'session_key': request.session.session_key,
            'referrer': request.META.get('HTTP_REFERER', ''),
            'query_params': dict(request.GET),
            'status_code': response.status_code
        }
        
        # D. Write to DB
        self.log_manager.create_generic_activity_log.model_class.objects.create(
            user=user,
            ip_address=self.anonymize_ip(ip_address),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],
            path=request.path,
            method=request.method,
            activity_type='page_visit',
            details=details
        )
