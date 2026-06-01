
import unittest

from django_abstract.base.base_dependency import BaseDependency, BaseGlobalDependency

class MockSelector:
    pass

class MockCreator:
    pass

class TestDependency(BaseDependency):
    app_name = "test_app"

class TestBaseDependency(unittest.TestCase):
    def setUp(self):
        # We need a clean subclass for isolation
        class LocalDependency(BaseDependency):
            app_name = "local_app"
        self.DepClass = LocalDependency

    def test_init_subclass_isolation(self):
        class DepA(BaseDependency): pass
        class DepB(BaseDependency): pass
        
        DepA.selectors['a'] = 1
        self.assertNotIn('a', DepB.selectors)
        self.assertNotEqual(id(DepA.selectors), id(DepB.selectors))
        
    def test_getattr_dynamic_resolution(self):
        # Register directly to the class
        self.DepClass.register_selector('select_mock', MockSelector)
        self.DepClass.register_creator('create_mock', MockCreator)
        
        dep = self.DepClass()
        
        # When we access dep.select_mock, it should instantiate MockSelector
        selector_instance = dep.select_mock
        self.assertIsInstance(selector_instance, MockSelector)
        
        creator_instance = dep.create_mock
        self.assertIsInstance(creator_instance, MockCreator)
        
    def test_getattr_raises_attribute_error(self):
        dep = self.DepClass()
        with self.assertRaises(AttributeError):
            _ = dep.select_non_existent

class TestBaseGlobalDependency(unittest.TestCase):
    def test_global_resolution(self):
        mock_registry = {
            'test_app': self
        }
        global_dep = BaseGlobalDependency(registry=mock_registry)
        self.assertEqual(global_dep.test_app, self)
        
        with self.assertRaises(AttributeError):
            _ = global_dep.missing_app
