from django.core.exceptions import PermissionDenied


def manager_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not hasattr(request.user, 'manager_profile'):
            raise PermissionDenied("Доступ разрешен только менеджерам.")
        return view_func(request, *args, **kwargs)

    return _wrapped_view
