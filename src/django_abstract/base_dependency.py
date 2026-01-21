from django_abstract.registry import GLOBAL_REGISTRY


class BaseDependency:
    def __init__(self, registry=None):
        # Directly assign to __dict__ to avoid triggering __getattr__
        self._registry = registry or GLOBAL_REGISTRY
    def __init_subclass__(cls, **kwargs):
        """
        Runs automatically when a subclass is defined.
        Ensures every Dependency class gets its OWN separate storage buckets.
        """
        super().__init_subclass__(**kwargs)
        cls._selectors = {}
        cls._creators = {}
        
    @classmethod
    def register_selector(cls, name, selector_cls):
        """Helper to register a selector to this dependency."""
        cls._selectors[name] = selector_cls

    @classmethod
    def register_creator(cls, name, creator_cls):
        """Helper to register a creator to this dependency."""
        cls._creators[name] = creator_cls
    
    def normalize_dependency(self,):
        self._selectors = self._registry[self.app_name]._selectors
        self._creators = self._registry[self.app_name]._creators
        return self
    
    def __getattr__(self, item):
        """
        Called when you access DomainDependency.item
        """
        # A. Local Domain Lookup (Selectors/Creators)
        # Used by: ProductDependency.select_product
        if hasattr(self, '_selectors') and item in self._selectors:
            return self._selectors[item]
        
        if hasattr(self, '_creators') and item in self._creators:
            return self._creators[item]

        # B. Global Registry Lookup (Apps)
        # Used by: GlobalDependency.client_app
        # We only look here if the item wasn't found locally
        if item in self._registry:
            return self._registry[item]
            raise AttributeError(f'no dependency found did you forget to regester {item}')
