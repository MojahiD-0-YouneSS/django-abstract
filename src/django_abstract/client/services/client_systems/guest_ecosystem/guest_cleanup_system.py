from django_abstract.client.dependencies import get_dependency_manager
from django_abstract.utilities import Entry
from django.contrib.sessions.models import Session
from dataclasses import dataclass
from datetime import timedelta
from django.utils import timezone

CDM = get_dependency_manager()

class GuestCleanupSystem:

    """
    Clean up Guest entries that are expired and unconverted.
    """
    def __init__(self,entry, inactivity_days: int = 3):
        self.cutoff = timezone.now() - timedelta(days=inactivity_days)
        self.entry = entry
        
        
    def get_expired_session_keys(self,):
        expired_sessions = Session.objects.filter(expire_date__lt=self.cutoff)
        return [s.session_key for s in expired_sessions]

    def gather_guest_objects(self,sessions_list):
        print('x',self.entry.session_key)

        users = CDM.select_abstract_guest_identity().access_db.filter(session_key__in=self.entry.session_key)
        return CDM.select_abstract_guest_mode_regestry().access_db.filter(
            user__in=users,
        )
        
    @staticmethod
    def to_entry(guest) -> Entry:
        return Entry(
            session_key=self.entry.session_key,
          
        ).entry_data(
            domain=self.entry.entry_data.domain,
            timestamp=guest.last_active_at.isoformat(),
            user_id=guest.user.id,
            status='expired'
        )
        
  
    def cleanup_guests(self,):
        expired_sessions_list = self.get_expired_session_keys()
        expired_guests = self.gather_guest_objects(sessions_list=expired_sessions_list)
        deleted = 0
        skipped = 0

        for guest in expired_guests:

            guest.is_deactivated=True
            guest.deactivated_by= self.__class__.__name__
            guest.deactivated_at= timezone.now()
            guest.save()
            
            deleted += 1


        cleanup_entry = self.entry.make_entry(
            session_key=self.entry.session_key,
            entry_data={
                'domain':'guest-clean-up',
                'status':'deleted',
                }, service_data={
                    'model_name':'GuestModeSystem',
                    'obj_id':None,
                    'service_data':{
                        "deleted": deleted,
                        "skipped_converted": skipped,
                        "total_checked": expired_guests.count()
        },
        }, control_data={},)
        cleanup_entry.service_entry_data.service_data.update(self.entry.service_entry_data.service_data)
        cleanup_entry.control_entry_data = self.entry.control_entry_data
        return cleanup_entry