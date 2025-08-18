# accounts/decorators.py
from django.core.exceptions import PermissionDenied

def role_required(allowed_roles=[]):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if request.user.role in allowed_roles or request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied
        return wrapper
    return decorator
