# client tasks.py

from django_abstract.client.services.client_systems.guest_ecosystem.guestmode import GuestModeSystem, GuestModeStarter, GuestModeBackUp
from django_abstract.client.services.client_systems.guest_ecosystem.guest_cleanup_system import GuestCleanupSystem

from celery import shared_task, current_task
from celery.schedules import crontab

cleanup_system = GuestCleanupSystem(inactivity_days=3)

@shared_task
def cleanup_expired_guests_task(dry_run=False):

    def log_entry(entry):
        print(f"[MIGRATE] {entry.session_id}, {entry.email}, {entry.last_active_at}")

    result = cleanup_system.cleanup_guests(
        dry_run=dry_run,
        migrate_callback=log_entry  # You can replace this with real archiving
    )
    return result

@current_task
def guest_mode(session_key, restore):
    start = GuestModeStarter(session_key=session_key).run()
    system = GuestModeSystem(session_key=start)
    system.run_all()
    print(f"guest system has been initialised for user {session_key}")
    return "done"

@current_task
def backup_guest_mode(session_key, user_ip, device_name,os_type):
    system = GuestModeBackUp(session_key=session_key, user_ip=user_ip, device_name= device_name, os_type=os_type,)
    registered = system.is_device_or_ip_registered()
    if registered:
        system.guest_mode_restore(restore=True)
        print(f"guest system has been restored successfully for user {session_key}")
    else:
        system.guest_mode_restore()
        print(f"guest system has not been restored for user {session_key}")

    return "done"

@shared_task
def periodic_guest_cleanup():
    # Example: scan for inactive sessions and clean
    expired = cleanup_system.get_expired_session_keys()

    for guest in expired:
        cleanup_expired_guests_task.delay(guest.session_id)
