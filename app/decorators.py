from django.shortcuts import redirect
from django.http import HttpResponse, Http404


def date_time_selected_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if 'date' not in request.session or 'time' not in request.session:
             raise Http404("Page not found")
        return view_func(request, *args, **kwargs)
    return _wrapped_view

