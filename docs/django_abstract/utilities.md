# Core Utilities

## Overview
`utilities.py` contains essential helper classes, mixins, and data structures used to manage state, routing, and metadata extraction.

## Data Structures
- **`ServiceEntryData`**: Encapsulates payload data intended for Services.
- **`EntryData`**: Encapsulates request metadata (IP, user agent, timestamps).
- **`ControlEntryData`**: Encapsulates flow-control flags for Operators.
- **`Entry`**: The master object that groups all three data structures together.

## Helper Classes
- **`ClassInfoProvider`**: Uses Python's `inspect` module to dynamically extract the current app, module, and method name for logging purposes.
- **`ExtractRequestDataUtilities`**: Automatically parses an incoming Django `HttpRequest` and populates an `Entry` object with standard metadata.

## Mixins
- **`EntryBindingMixin`**: A Django View Mixin that intercepts incoming requests and automatically binds a newly hydrated `Entry` object to `request.GMS_OBJECT.entry`.
- **`AdminOrStaffMixin`**: Restricts view access to administrative users.
