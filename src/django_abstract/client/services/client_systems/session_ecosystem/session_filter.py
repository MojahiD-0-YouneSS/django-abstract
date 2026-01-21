from django_abstract.utilities import ClassInfoProvider
from django_abstract.client.utilities import ServiceEntryData
from django_abstract.client.services.client_systems.operators.operator_regestry import SYSTEM_REGISTRY
from django_abstract.client.services.client_services import (
    IdentityCheckService,
    )
from django_abstract.client.services.session_service import (
    BannedUserService,
    SessionMetricsService,
    SessionLinkService,
    )
from django_abstract.client.dependencies import get_dependency_manager

CMD = get_dependency_manager()

class SessionFilterSystem(ClassInfoProvider):
    """
    This class is responsible for filtering sessions based on various criteria.
    It provides methods to filter sessions by user ID, session ID, and other attributes.
    """

    def __init__(self, entry):
        super().__init__()
        self.entry = entry # Placeholder for session data
        self.filtered_sessions = {}  # Placeholder for filtered sessions
        self.processed_sessions = []  # Placeholder for filtered sessions
        # self.BUS=SYSTEM_REGISTRY.get(BannedUserService.domain,None)
        # self.SMS=SYSTEM_REGISTRY.get(SessionMetricsService.domain,None)
        # self.SLS=SYSTEM_REGISTRY.get(SessionLinkService.domain,None)

    def run(self,):
        identity = self.identity_check()
        identity.add_to_history
        identity.service_data.update(self.entry.service_entry_data.service_data)
        link_entry = self.link_session(identity)
        # self.entry.service_entry_data = link_entry
        self.session_metrics(link_entry=link_entry)
        if not self.entry.control_entry_data.request_path_object_mapper.flags['unique']:
            self.banned_sessions()
        return self.entry

    def link_session(self,identity_entry):
        if identity_entry.errors and not identity_entry.errors['record_exists']:
            return identity_entry
        else:
            identity_id = identity_entry.obj_id
            user_id = self.entry.entry_data.user_id
            if SessionLinkService.SessionLinkServiceValidator(abstract_guest_user_id=identity_id,user=user_id).can_run(dry_run=True):
                link = SessionLinkService(session_key=self.entry.session_key,abstract_guest_user_id=identity_id,user=user_id)
                if link.entry:
                    return link.entry
                return link.hook(identity_entry,)       
            else:
                return identity_entry

    def session_metrics(self, link_entry):

        if SessionMetricsService.SessionMetricsValidator(**link_entry.service_data).can_run(dry_run=True):
            metrics = SessionMetricsService(session_key = self.entry.session_key,**link_entry.service_data)
            print('here is the probele')
            if metrics.can_run(model_name='AbstractSessionMetrics',**link_entry.service_data):
                
                print('i guess it"s fixxed')
                
                link_metrics = metrics.access_db.filter(**self.entry.service_entry_data.service_data['session_data'])
                if link_metrics:
                    sessions_list = [lm.session_key for lm in link_metrics]
                    self.entry.control_entry_data.request_path_object_mapper.flags['unique']=False
                    self.filtered_sessions[self.entry.session_key] = sessions_list
                    self.entry.control_entry_data.request_path_object_mapper.flags['pervious_keys'] = self.filtered_sessions[self.entry.session_key]
                else:
                    self.entry.control_entry_data.request_path_object_mapper.flags['unique']=True
                    self.entry.control_entry_data.request_path_object_mapper.flags['banned'] = False
                    self.entry.control_entry_data.request_path_object_mapper.flags['pervious_keys'] = None
                    # crud (create_data=True) operation key_word
                    metrics.hook(link_entry,)
                    return link_entry
            self.processed_sessions.append(metrics.session_key)
        return link_entry

    def banned_sessions(self,):
        banned = BannedUserService(session_key=self.entry.session_key)
        if self.entry.control_entry_data.request_path_object_mapper.flags['pervious_keys']:
            banned_entries = banned.access_db.filter(session_key__in=self.entry.control_entry_data.request_path_object_mapper.flags['pervious_keys'])
            if banned_entries:
                self.entry.control_entry_data.request_path_object_mapper.flags['banned'] = True
        return banned.entry

    def identity_check(self,):
        identity = IdentityCheckService(session_key=self.entry.session_key,include_session=True)
        identity.run(**self.entry.service_entry_data.service_data)
        return  identity.entry

