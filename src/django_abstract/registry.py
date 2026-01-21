# core regestry.py
from dataclasses import dataclass
from django_abstract.base_selector import BaseSelector
from django_abstract.base_creator import BaseCreator
from django_abstract.utilities import to_snake_case
from functools import wraps


GLOBAL_REGISTRY = {
    
}
# GLOBAL_REGISTRY => {'app':dependency['_selectors':{'name':class},'_creators':{'name':class}]}

def creator_selector(name=None, dependency=None,):
    """
    used in case registing from a model
    """
    # @wraps
    
    def wrapper(cls):

        select_key = name or f"select_{to_snake_case(cls.__name__)}"
        create_key = name or f"create_{to_snake_case(cls.__name__)}"
        select_name = f"{cls.__name__}Selector"
        create_name = f"{cls.__name__}Creator"
        
        if not dependency:
            raise NotImplementedError(f"Dependency for ''{dependency.__name__}'' service must be provided")
        
        if not hasattr(dependency, "_selectors") or not hasattr(dependency, "_creators"):
            raise NotImplementedError(f"Dependency ''{dependency.__name__}'' does not have _selectors or _creators")

        def dynamic_init(self, ):
            BaseSelector.__init__(self, model_class=cls)

        
        class_attrs = {
            "__module__": __name__,
            '__init__': dynamic_init,
        }
        if dependency.app_name in GLOBAL_REGISTRY:
            selector_class = type(select_name, (BaseSelector,), class_attrs)
            creator_class = type(create_name, (BaseCreator,), class_attrs)
            
            GLOBAL_REGISTRY[dependency.app_name]._selectors.update({select_key: selector_class})
            GLOBAL_REGISTRY[dependency.app_name]._creators.update({create_key: creator_class})
        else:
            selector_class = type(select_name, (BaseSelector,), class_attrs)
            creator_class = type(create_name, (BaseCreator,), class_attrs)
            dependency._selectors = {select_key: selector_class}
            dependency._creators = {create_key: creator_class}
            GLOBAL_REGISTRY[dependency.app_name] = dependency
        return cls
    return wrapper

SELECTOR_REGISTRY = {}
CREATOR_REGISTRY = {}

def register_selector(name=None, dependency=None):
    """
    used in case registing from a selector
    """
    def wrapper(cls):
        key = name or cls.__name__.replace("Selector", "").lower()

        if dependency.app_name in SELECTOR_REGISTRY:
            SELECTOR_REGISTRY[dependency.app_name]._selectors[key] = cls
        if not dependency.app_name in SELECTOR_REGISTRY:
            dependency._selectors={key:cls}
            SELECTOR_REGISTRY[dependency.app_name] = dependency
        return cls
    return wrapper


def register_creator(name=None, dependency=None):
    """
    used in case registing from a creator
    """
    def wrapper(cls):
        key = name or cls.__name__.replace("Creator", "").lower()
        if dependency.app_name in CREATOR_REGISTRY:
            CREATOR_REGISTRY[dependency.app_name]._creators[key] = cls
        if not dependency.app_name in CREATOR_REGISTRY:
            dependency._creators={key:cls}
            CREATOR_REGISTRY[dependency.app_name] = dependency
        return cls
    return wrapper


