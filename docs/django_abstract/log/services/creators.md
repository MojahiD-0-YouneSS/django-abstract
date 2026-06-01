# Logging Creators

## Overview
Write-only creators for instantiating logging models. Each creator inherits from `BaseCreator` and is registered to `AbstractLoggingDependency`.

## Classes
- `SystemErrorLogCreator`: Creates instances of `SystemErrorLog`.
- `FeatureToggleCreator`: Creates instances of `FeatureToggle`.
- `AdminActionLogCreator`: Creates instances of `AdminActionLog`.
- `GenericActivityLogCreator`: Creates instances of `GenericActivityLog`.
