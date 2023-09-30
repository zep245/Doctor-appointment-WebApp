from django.shortcuts import render


def date_time_selected_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if 'date' not in request.session or 'time' not in request.session:
            return render(request, '404.html', status=404)
        return view_func(request, *args, **kwargs)
    return _wrapped_view

