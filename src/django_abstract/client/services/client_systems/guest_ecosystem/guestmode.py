from datetime import timedelta
from django.utils import timezone
from django_abstract.utilities import (Entry)
from django_abstract.client.dependencies import get_dependency_manager
from django_abstract.client.services.client_systems.guest_ecosystem.guest_cleanup_system import  GuestCleanupSystem


CDM = get_dependency_manager()

class GuestModeStarterSystem:
    def __init__(self, entry:Entry):
        super().__init__()
        self.entry=entry
        self.session_key= entry.session_key
        
    def run(self,):
        """
        import all dependencies and run get_or_create
        :return:
        """
        # client
        # from django_abstract.client.operators.operator_regestry import SYSTEM_REGISTRY
        
        # for regestry in SYSTEM_REGISTRY['GMS'].values():
        #     regestry(session_key=self.session_key).create_entry()

        user = CDM.select_abstract_guest_identity().access_db.get(session_key=self.session_key)
        
        guest_mode = CDM.create_abstract_guest_mode_regestry().access_db.create(
            user =user.session_key, 
            is_blocked =self.entry.control_entry_data.request_path_object_mapper.flags['banned'], )
        gmss_entry = Entry(session_key=self.session_key,)
        gmss_entry.service_entry_data=self.entry.service_entry_data.load_obj_data(guest_mode),
        self.entry.service_entry_data.add_to_history
        gmss_entry.service_entry_data.history = self.entry.service_entry_data.history
        gmss_entry.control_entry_data = self.entry.control_entry_data 

        return gmss_entry

class GuestModeSystem:
    def __init__(self, entry):
        self.session_key = entry.session_key
        self.entry = entry        
        self.operators = self.load_operators()
        self.discarded_operators_names = []
        self.http_respones = {}
    COLLECTED_DATA = {}
    def load_operators(self):
        from django_abstract.client.services.client_systems.operators.operator_regestry import OPERATOR_REGISTRY
        domain_specific_services = OPERATOR_REGISTRY.get(self.entry.control_entry_data.request_path_object_mapper.app,{})
        return [op(self.session_key) for op in domain_specific_services if op(self.session_key).can_run() and op.__name__ not in self.discarded_operators_names]

    def run(self,):
        
        for operator in self.operators:
            try:
                self.COLLECTED_DATA[operator.domain]=operator.run()
            except Exception as e:
                self.log_error(operator, e)
        self.entry.return_value =self.COLLECTED_DATA
        self.COLLECTED_DATA.clear()
        return self.entry
    def discarded_operators(self,operator_name):
        if any(operator_name == op.__name__ for op  in self.operators):
            self.discarded_operators_names.append(operator_name)
        return self.session_key

   

    def operator_schema(self, operator_name):
        """
        Get the schema of the operator. """ 
        return [op for op in self.operators if op.__name__ == operator_name]
    
    def run_url_mapper(self, request):
        request_path = request.path
        return list(request_path)
    
    def can_run(self,):
        """
        Check if the system can run based on the session key and entry data.
        :return: bool
        """
        if self.session_key and self.entry:
            return True
        return False

    def log_error(self, operator, exception):
        
        print(f"[GuestMode, user: {self.session_key} ] Operator {operator.__class__.__name__} failed: {exception}")

def get_guest_mode_system(entry):
    return GuestModeSystem(entry)

class GuestModeBackUpSystem:
    def __init__(self, entry):
        self.entry=entry
        self.session_key= entry.session_key
        super().__init__()

    def back_up(self,):
        user = CDM.select_abstract_guest_identity().access_db.get(session_key=self.session_key)
        try:
            guest_mode = CDM.select_abstract_guest_mode_regestry().access_db.get(
                user =user.session_key, 
                is_blocked =self.entry.control_entry_data.request_path_object_mapper.flags['banned'],
                system_id='123665467789',
                )
        except:
            guest_mode = CDM.select_abstract_guest_mode_regestry().access_db.create(
                user =user.session_key, 
                is_blocked =self.entry.control_entry_data.request_path_object_mapper.flags['banned'], )
        if guest_mode:
            guest_mode_entry = Entry(session_key=self.session_key,)
        guest_mode_entry.service_entry_data=self.entry.service_entry_data.load_obj_data(guest_mode)
        self.entry.service_entry_data.add_to_history
        guest_mode_entry.service_entry_data.history = self.entry.service_entry_data.history
        guest_mode_entry.control_entry_data = self.entry.control_entry_data 
        return guest_mode_entry

class GuestModeManager:
    def __init__(self,entry):
        self.session_key = entry.session_key
        self.entry = entry  # Placeholder for session data

    def run(self):
        if self.entry.control_entry_data.request_path_object_mapper.flags['unique']:
            guest_mode = GuestModeStarterSystem(entry=self.entry).run()
        else:
            backup_system = GuestModeBackUpSystem(
                entry=self.entry,
            )
            guest_mode = backup_system.back_up()
        system = get_guest_mode_system(entry=guest_mode)
        self.clean_up()
        return system
    
    def clean_up(self):
        GCS = GuestCleanupSystem(self.entry)
        return GCS.cleanup_guests()

def abstract_services_manager(entry=None):
   if entry:
        GMSM_OBJECT = GuestModeManager(entry=entry)
        GMS = GMSM_OBJECT.run()
        return GMS
   else:
       return entry
            

'''
form_class = FORMREGESTRY.get(self.view_name, None)
request_data = ExtractRequestDataUtilities(request) GET,DELETE or ExtractRequestDataUtilities(request, form_class=form_class) POST, PUT, PATCH

request.guest_mode.run_url_mapper(request)
request.guest_mode.can_run()
request.guest_mode.run.delay()
request.guest_mode.http_respones.get('view_name', None)

class XYZView(view):
    def get(self, request, *args, **kwargs):
        view_name = ClassInfoProvider.resolve_class_info(self).get('service_name', None)
        return request.guest_mode.http_respones.get('view_name', None)
''' 