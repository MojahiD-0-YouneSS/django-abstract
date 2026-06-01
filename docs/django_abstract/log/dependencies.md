# AbstractLoggingDependency

## Overview
A `BaseDependency` subclass that acts as the container for all logging-related selectors and creators.

## Attributes
- `app_name`: `django_abstract_log`
- `domain`: `logging`
- `description`: "Logs events to database"

## Usage
Used as the central dependency injection token for `SystemErrorLogCreator`, `SystemErrorLogSelector`, etc.
