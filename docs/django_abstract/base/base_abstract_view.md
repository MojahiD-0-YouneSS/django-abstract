# GMES View Bindings

## Overview
While the framework operates abstractly, `EntryBindingMixin` (located in `utilities.py` but representing the View layer) automatically binds an incoming Django HTTP Request to a framework `Entry`.

## Workflow
1. The View Mixin intercepts the request.
2. It extracts the `session_key`, `ip_address`, `user_agent`, and payload (POST/GET parameters) via `ExtractRequestDataUtilities`.
3. It creates a master `Entry` object.
4. It attaches the `Entry` to the `request` object (e.g., `request.GMS_OBJECT.entry`).

This allows `BaseSystem` to receive a fully hydrated context without caring if the request came from an API, an HTMX call, or a standard form submission.
