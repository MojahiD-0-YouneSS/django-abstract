
import unittest
from unittest.mock import MagicMock

from django_abstract.registry import (
    GLOBAL_REGISTRY,
    SELECTOR_REGISTRY,
    CREATOR_REGISTRY,
    SERVICE_REGISTRY,
    OPERATOR_REGISTRY,
    GLOBAL_OPERATOR_REGISTRY,
    SYSTEM_REGISTRY,
    creator_selector,
    register_selector,
    register_creator,
    register_service,
    register_operator,
    register_system,
    get_app_dependency,
    get_service,
    get_operator,
    get_system
)
from django_abstract.base.base_dependency import BaseDependency
from django_abstract.base.base_model_service import BaseModelService
from django_abstract.base.base_model_system import BaseModelSystem

class MockDependency(BaseDependency):
    app_name = 'test_app'
    domain = 'test_domain'

class TestRegistry(unittest.TestCase):
    def setUp(self):
        # Clear out the registries to prevent test pollution
        GLOBAL_REGISTRY.clear()
        SELECTOR_REGISTRY.clear()
        CREATOR_REGISTRY.clear()
        SERVICE_REGISTRY["MODEL_SERVICE"].clear()
        SERVICE_REGISTRY["BARE_SERVICE"].clear()
        OPERATOR_REGISTRY.clear()
        GLOBAL_OPERATOR_REGISTRY.clear()
        SYSTEM_REGISTRY["MODEL_SYSTEM"].clear()
        SYSTEM_REGISTRY["BARE_SYSTEM"].clear()
        
        self.dependency = MockDependency()

    def test_creator_selector_decorator(self):
        @creator_selector(dependency=self.dependency)
        class DummyModel:
            pass
            
        # Verify dependency registered in global
        self.assertIn('test_app', GLOBAL_REGISTRY)
        
        # Verify dynamic creation of selector and creator
        self.assertIn('select_dummy_model', self.dependency.selectors)
        self.assertIn('create_dummy_model', self.dependency.creators)
        
        # Verify naming of dynamically created classes
        selector_class = self.dependency.selectors['select_dummy_model']
        creator_class = self.dependency.creators['create_dummy_model']
        
        self.assertEqual(selector_class.__name__, 'DummyModelSelector')
        self.assertEqual(creator_class.__name__, 'DummyModelCreator')
        
    def test_register_service(self):
        @register_service()
        class DummyModelService(BaseModelService):
            pass
            
        @register_service()
        class DummyBareService:
            pass
            
        self.assertIn('dummy_model_service', SERVICE_REGISTRY["MODEL_SERVICE"])
        self.assertIn('dummy_bare_service', SERVICE_REGISTRY["BARE_SERVICE"])
        
        self.assertEqual(get_service('dummy_model_service'), DummyModelService)

    def test_register_operator(self):
        @register_operator()
        class DummyOperator:
            app_name = 'test_app'
            
        self.assertIn('dummy_operator', OPERATOR_REGISTRY)
        self.assertEqual(get_operator('dummy_operator'), DummyOperator)
        
    def test_register_system(self):
        @register_system()
        class DummySystem:
            pass
            
        @register_system()
        class DummyModelSystem(BaseModelSystem):
            pass
            
        self.assertIn('dummy_system', SYSTEM_REGISTRY["BARE_SYSTEM"])
        self.assertIn('dummy_model_system', SYSTEM_REGISTRY["MODEL_SYSTEM"])
