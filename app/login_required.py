from django.shortcuts import redirect


def patient_login_required(login_url=None):
    def decorator(view_func):
        def _wrapped_func(request , *args , **kwargs):
            if not request.session.get("patient"):
                return redirect(login_url)
            return view_func(request , *args , **kwargs)
        return _wrapped_func
    return decorator