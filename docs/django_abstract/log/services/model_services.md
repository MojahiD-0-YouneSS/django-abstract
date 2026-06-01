# Logging Model Services

## Overview
High-performance background services for the logging system. They use Redis caching and queued bulk-inserts to prevent database locking during high-volume error tracking or metric gathering.

## ErrorLogModelService
- Handles high-volume system error insertion.
- Pushes error payloads to a Redis list (`error_logs_queue`).
- Automatically flushes to the database via `.bulk_create()` when the queue reaches 50 items.

## SessionMetricsModelService
- Tracks active sessions and metrics in Redis before flushing them.
- Identical high-throughput queue design.

## BannedUserModelService
- Fetches and caches the list of banned users/IPs in Redis for extremely fast permission checking.
