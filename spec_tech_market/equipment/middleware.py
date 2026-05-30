from django.contrib import messages

class VerificationCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.path.startswith('/profile/verify/'):
            if not request.user.profile.email_verified or not request.user.profile.phone_verified:
                messages.warning(request, 'Подтвердите email и телефон для полного доступа к функциям')
        response = self.get_response(request)
        return response
