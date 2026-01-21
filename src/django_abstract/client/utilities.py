from django_abstract.client.dependencies import get_dependency_manager
from django_abstract.utilities import ServiceEntryData
from django.utils.text import slugify
from django.utils import timezone

CDM = get_dependency_manager()

class SessionMetaDataRegistry:
    def __init__(self, session_key, ip_address, device_hash, ):
        super().__init__()
        self._exists_flag = CDM.select_abstract_session_link.filter_by_guest(ip_address=ip_address,shared_device_hash=device_hash,).exist()
        self._session_exists_flag = CDM.select_abstract_session_link.filter(current_session_key=session_key).exist()
        self.session_key = session_key
        self.ip_address = ip_address
        self.device_hash = device_hash
        
    def linkable(self):
        return self._exists_flag and not self._session_exists_flag
    
    def link_session(self,):
        if self.linkable():
            link = CDM.select_abstract_session_link.filter(ip_address=self.ip_address,shared_device_hash=self.device_hash,).ordered_by('-session_count')[-1]
            link.previous_session_key = f'{link.previous_session_key}, {link.current_session_key}'
            link.current_session_key = self.session_key
            link.session_count =+ 1
            link.save()
        else:
            link = CDM.create_abstract_session_link.create(
            current_session_key = self.session_key,
            shared_device_hash = self.device_hash,
            ip_address = self.ip_address,
            )
        link_rep = ServiceEntryData.load_obj_data(obj=link, data=link.__dict__)
        return link_rep
