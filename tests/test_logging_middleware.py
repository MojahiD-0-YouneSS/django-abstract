import pytest
from django.test import RequestFactory, override_settings
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse
from django_abstract.log.middleware import RequestLoggingMiddleware
from django_abstract.log.models import GenericActivityLog

# --- SETUP ---

@pytest.fixture
def middleware():
    """Returns an instance of the middleware with a dummy get_response."""
    def get_response(request):
        return HttpResponse("OK")
    return RequestLoggingMiddleware(get_response)

@pytest.fixture
def factory():
    return RequestFactory()

# --- TESTS ---

@pytest.mark.django_db
def test_logging_middleware_creates_log(middleware, factory):
    """
    Scenario: Standard GET request.
    Expected: A new GenericActivityLog row is created.
    """
    request = factory.get('/home/')
    request.user = AnonymousUser()
    request.session = {} # Simulating session dict
    
    # Run Middleware
    middleware(request)
    
    # Assertions
    assert GenericActivityLog.objects.count() == 1
    log = GenericActivityLog.objects.first()
    assert log.path == '/home/'
    assert log.method == 'GET'
    assert log.status_code == 200

@pytest.mark.django_db
def test_logging_middleware_excludes_admin(middleware, factory):
    """
    Scenario: Request to /admin/.
    Expected: No log created (ignored).
    """
    request = factory.get('/admin/login/')
    request.user = AnonymousUser()
    request.session = {}
    
    middleware(request)
    
    assert GenericActivityLog.objects.count() == 0

@pytest.mark.django_db
def test_logging_middleware_captures_guest_id(middleware, factory):
    """
    Scenario: Request has 'request.guest' attached (by GuestMiddleware).
    Expected: Log entry contains the guest_id.
    """
    request = factory.get('/shop/')
    request.user = AnonymousUser()
    request.session = {}
    
    # Simulate GuestMiddleware having run previously
    class MockGuest:
        id = "guest-uuid-123"
    request.guest = MockGuest()
    
    middleware(request)
    
    log = GenericActivityLog.objects.first()
    assert log.guest_id == "guest-uuid-123"

@pytest.mark.django_db
def test_logging_middleware_silent_fail_on_error(middleware, factory):
    """
    Scenario: Database write fails (simulated).
    Expected: Middleware proceeds, returns response, does NOT crash.
    """
    request = factory.get('/error/')
    request.user = AnonymousUser()
    request.session = {}
    
    # Mock log_request to raise an exception
    # (Simulating a DB connection error or bug)
    def broken_logger(*args):
        raise ValueError("DB Exploded")
    
    # Patch the instance method
    middleware.log_request = broken_logger
    
    # Should NOT raise exception
    response = middleware(request)
    
    assert response.status_code == 200
    # No logs created obviously