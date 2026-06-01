from django_abstract.registry import GLOBAL_REGISTRY, SELECTOR_REGISTRY, CREATOR_REGISTRY


class BaseDependency:
    """Base class for managing and injecting dependencies like selectors and creators.

    Attributes:
        _registry (dict): The registry to pull dependencies from.
        selectors (dict): Local mapping of selector dependencies.
        creators (dict): Local mapping of creator dependencies.
        model_class (Type[Model], optional): Associated model class.
    """
    def __init__(self, registry=None):
        """Initialize the BaseDependency.

        Args:
            registry (dict, optional): The global or domain-specific registry. Defaults to GLOBAL_REGISTRY.
        """
        # Directly assign to __dict__ to avoid triggering __getattr__
        self._registry = registry or GLOBAL_REGISTRY
    def __init_subclass__(cls, **kwargs):
        """
        Runs automatically when a subclass is defined.
        Ensures every Dependency class gets its OWN separate storage buckets.
        """
        super().__init_subclass__(**kwargs)
        cls.selectors = {}
        cls.creators = {}
        cls.model_class = None
        
    @classmethod
    def register_selector(cls, name, selector_cls):
        """Helper to register a selector to this dependency."""
        cls.selectors[name] = selector_cls

    @classmethod
    def register_creator(cls, name, creator_cls):
        """Helper to register a creator to this dependency."""
        cls.creators[name] = creator_cls
    
    def normalize_dependency(self,):
        self.selectors = self._registry[self.app_name].selectors
        self.creators = self._registry[self.app_name].creators
        return self
    def get_model_class(self,):
        
        return self._registry[self.app_name].model_class
    def __getattr__(self, item):
        """
        Called when you access DomainDependency.item
        """
        # A. Local Domain Lookup (Selectors/Creators)
        # Used by: ProductDependency.select_product
        if hasattr(self, 'selectors') and item in self.selectors:
            return self.selectors[item]()
        
        if hasattr(self, 'creators') and item in self.creators:
            return self.creators[item]()

        # B. Global Registry Lookup (Apps)
        # Used by: GlobalDependency.client_app
        # We only look here if the item wasn't found locally
        if item in self._registry:
            return self._registry[item]()
        raise AttributeError(f'no dependency found did you forget to regester {item}')

class BaseCreateDependency(BaseDependency):
    def __init__(self,):
        self._registry = CREATOR_REGISTRY

class BaseSelectDependency(BaseDependency):
    def __init__(self,):
        self._registry = SELECTOR_REGISTRY

class BaseGlobalDependency:
    def __init__(self, registry=None):

        self._registry = registry or GLOBAL_REGISTRY
        
    def __getattr__(self, item):
        if item in self._registry:
            return self._registry[item]
        raise AttributeError(f'attribute {item} not found in {list(self._registry.keys())}')        
