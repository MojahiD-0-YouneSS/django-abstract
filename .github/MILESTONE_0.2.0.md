# 🎯 Milestone: 0.2.0 Release

**Target Release Version:** `0.2.0`
**Current Version:** `0.1.3`

**Description:** The primary focus of the `0.2.0` milestone is to improve the type safety, expand the generic utility classes, and make the Redis queueing system optional so that smaller projects can use `django-abstract` without a Redis dependency.

---

## 📊 Kanban Board

| 📥 Inbox / Backlog | 🎯 To Do (Ready for Dev) | 🚧 In Progress | 👀 In Review | ✅ Done |
| :--- | :--- | :--- | :--- | :--- |
| **[#5]** Add comprehensive Pytest fixtures | **[#2]** Make Redis Dependency Optional | **[#1]** Implement Strict Type Hinting | | |
| **[#6]** Add Django Ninja / FastAPI View Mixins | **[#4]** Add `BaseValidator` Layer | | | |
| | **[#3]** Expand Generic Selectors (`get_or_create` logic) | | | |

---

## 📝 Issues List for 0.2.0

### 🚧 In Progress
* **[#1] Implement Strict Type Hinting across core architecture**
  * **Type**: `enhancement`, `core`
  * **Description**: Ensure that `BaseModel`, `BaseSelector`, `BaseCreator`, `BaseService`, and `BaseSystem` have robust Python `typing` support. This includes adding `Generic[T]` parameters where appropriate so that IDEs can infer the return types of dynamically injected dependencies.

### 🎯 To Do
* **[#2] Make Redis Dependency Optional**
  * **Type**: `enhancement`, `log-system`
  * **Description**: Currently, the `log` app and high-throughput buffering rely on Redis. For smaller deployments, this should fall back to direct PostgreSQL inserts or a simpler cache backend if Redis is not configured.
* **[#3] Expand Generic Selectors & Creators**
  * **Type**: `feature`, `generic`
  * **Description**: Add reusable generic methods like `get_or_create`, `update_or_create`, and `bulk_update` to the base Generic classes so developers don't have to rewrite them for every model.
* **[#4] Add `BaseValidator` Layer**
  * **Type**: `feature`, `architecture`
  * **Description**: Introduce a new layer to the Clean Architecture: `Validators`. These should sit between `EntryBindingMixin` and `BaseSystem` to sanitize payloads before business logic execution.

### 📥 Inbox / Backlog
* **[#5] Add comprehensive Pytest fixtures**
  * **Type**: `testing`, `chore`
  * **Description**: Create a suite of pytest fixtures that automatically patch the Global Registry. This will allow developers to easily mock `Selectors` and `Creators` with a single decorator during unit testing.
* **[#6] Add Django Ninja / FastAPI View Mixins**
  * **Type**: `enhancement`, `utilities`
  * **Description**: Expand `EntryBindingMixin` (which targets standard Django views) to support Django Ninja routers or FastAPI endpoints, extracting payload data seamlessly from Pydantic schemas.
