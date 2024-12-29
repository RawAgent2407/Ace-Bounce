from django.contrib.sessions.exceptions import SessionInterrupted
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse

class SessionValidityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.session.session_key:
            if request.is_ajax():
                return JsonResponse({'error': 'Session has expired. Please log in again.'}, status=401)
            else:
                return HttpResponseRedirect(reverse('login'))
        
        response = self.get_response(request)
        return response

