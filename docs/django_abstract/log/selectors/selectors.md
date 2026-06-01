# Logging Selectors

## Overview
Read-only selectors for querying logging data from the database. Each selector inherits from `BaseSelector` and is registered to `AbstractLogSelectDependency`.

## Classes
- `SystemErrorLogSelector`: Queries the `SystemErrorLog` model.
- `FeatureToggleSelector`: Queries the `FeatureToggle` model.
- `AdminActionLogSelector`: Queries the `AdminActionLog` model.
- `GenericActivityLogSelector`: Queries the `GenericActivityLog` model.
