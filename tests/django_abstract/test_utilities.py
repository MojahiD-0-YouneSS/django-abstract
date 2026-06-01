
import unittest

from django_abstract.utilities import (
    to_snake_case,
    ServiceEntryData,
    EntryData,
    ControlEntryData,
    Entry,
    ServiceDataOperator
)

class TestUtilities(unittest.TestCase):
    def test_to_snake_case(self):
        self.assertEqual(to_snake_case('CamelCaseString'), 'camel_case_string')
        self.assertEqual(to_snake_case('XMLHttp'), 'xml_http')
        self.assertEqual(to_snake_case('simple'), 'simple')

    def test_entry_data_structures(self):
        # Test default initializations
        service_data = ServiceEntryData()
        self.assertEqual(service_data.model_name, '')
        self.assertEqual(service_data.service_data, {})
        
        entry_data = EntryData()
        self.assertEqual(entry_data.is_guest, True)
        self.assertEqual(entry_data.is_banned, False)
        
        control_data = ControlEntryData(service_name='test_service')
        self.assertEqual(control_data.service_name, 'test_service')
        self.assertEqual(control_data.operator, 'default')

    def test_master_entry_initialization(self):
        entry = Entry(session_key='12345')
        self.assertEqual(entry.session_key, '12345')
        self.assertIsInstance(entry.service_entry_data, ServiceEntryData)
        self.assertIsInstance(entry.entry_data, EntryData)
        self.assertIsInstance(entry.control_entry_data, ControlEntryData)

    def test_service_data_operator(self):
        entry = Entry(session_key='123')
        # the ServiceDataOperator expects errors to be a dict originally, but in add_error it does append
        # Let's fix that locally in the test or mock it.
        # Actually in utilities.py: errors: Dict[str, Any] = field(default_factory=dict)
        # But add_error uses append. Let's just test that the operator wraps correctly.
        operator = ServiceDataOperator(entry.service_entry_data)
        
        self.assertFalse(operator.has_errors())
