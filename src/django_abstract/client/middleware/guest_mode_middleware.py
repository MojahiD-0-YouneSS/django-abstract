import uuid
from django.utils.deprecation import MiddlewareMixin
from django_abstract.client.services.client_systems.guest_ecosystem.guestmode import GuestModeManager
from django_abstract.client.services.client_systems.session_ecosystem.request_services import UrlMapper
from django_abstract.client.services.client_systems.session_ecosystem.session_filter import SessionFilterSystem
from django.conf import settings
from django.utils.functional import SimpleLazyObject
from django_abstract.utilities import GuestRequestObject
from django_abstract.base_abstract_view import ABSTRACT_VIEW_REGESTRY

class GuestModeMiddleware(MiddlewareMixin):
    """
    The Gatekeeper of the Guest Mode Ecosystem (GMES).
    
    Responsibilities:
    1. Identification: Retrieves or generates a unique Guest UUID.
    2. Context: Attaches a lazy GuestModeManager to request.guest.
    3. Persistence: Ensures the guest cookie is set/refreshed on the response.
    """

    COOKIE_NAME = getattr(settings, 'GUEST_COOKIE_NAME', 'guest_device_id')
    COOKIE_AGE = getattr(settings, 'GUEST_COOKIE_AGE', 60 * 60 * 24 * 365) # 1 Year
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # 1. SETUP PHASE
        print('GuestModeMiddleware is running !!')
        if not hasattr(request,'GMS_OBJECT'):
            self._setup_guest_context(request)
            
        
        response = self.get_response(request)

        response = self._handle_response_cookie(request, response)
        
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # 1. Get the Unique Identifier (URL Name)
        url_name = request.resolver_match.url_name
    
        if url_name in ABSTRACT_VIEW_REGESTRY:
            bind_func = ABSTRACT_VIEW_REGESTRY[url_name]
            bind_func(request=request)
        if hasattr(request.GMS_OBJECT.VIEW,'view_info'):
        # 2. EXECUTION PHASE
            URL_MAPPER_OBJECT = UrlMapper(request)
            # 3. TEARDOWN PHASE (Cookie Management)

            SESSION_FILTER_SYSTEM_OBJECT = SessionFilterSystem(URL_MAPPER_OBJECT.get_entry_version())

            SFSO_ENTRY = SESSION_FILTER_SYSTEM_OBJECT.run()

            request.GMS_OBJECT.guest_response=SFSO_ENTRY.return_value
            request.GMS_OBJECT.entry=SFSO_ENTRY
    def _get_guest_id_from_request(self, request):
        """Extracts the UUID from cookies or headers."""
        return request.COOKIES.get(self.COOKIE_NAME)

    def _setup_guest_context(self, request):
        """
        Attaches the GuestModeManager to the request.
        Using SimpleLazyObject ensures we don't hit the DB/Cache 
        unless the view actually asks for 'request.guest'.
        """
        def get_guest_manager():
            guest_id = self._get_guest_id_from_request(request)
            is_new = False
            
            if not guest_id:
                guest_id = str(uuid.uuid4())
                is_new = True
            
            # Store ID on request for the response cycle to access later
            request._guest_id_cache = guest_id
            request._guest_is_new = is_new
            # Get the view function or class closure

            {"id": guest_id, "is_new": is_new}
            # Mocking the return for this snippet as I don't have the GMM class code
            GRO =  GuestRequestObject(empty=True,)
            GRO.entry.session_key = request.session.session_key

            return GRO

        # Lazy attachment
        request.GMS_OBJECT = SimpleLazyObject(get_guest_manager)



    def _handle_response_cookie(self, request, response):
        """
        Ensures the Guest Cookie is persistent and secure.
        """
        # Check if the guest system was actually touched/initialized
        if not hasattr(request, '_guest_id_cache'):
            # If SimpleLazyObject wasn't evaluated, check if we need to preserve existing cookie
            return response

        guest_id = request._guest_id_cache
        should_set_cookie = getattr(request, '_guest_is_new', False)

        # Logic: Always refresh the cookie expiration on activity, 
        # or set it if it's new.
        if should_set_cookie or self.COOKIE_NAME in request.COOKIES:
            response.set_cookie(
                self.COOKIE_NAME,
                guest_id,
                max_age=self.COOKIE_AGE,
                httponly=True,   # Security: JS cannot read this
                samesite='Lax',  # Security: CSRF mitigation
                secure=not settings.DEBUG # Enforce HTTPS in production
            )
        
        return response