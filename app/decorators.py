from django.shortcuts import redirect
from django.contrib import messages


def date_time_selected_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if 'date' not in request.session or 'time' not in request.session:
            messages.error(request, 'Please select a date and time before creating an appointment.', extra_tags='session_message')
            return redirect('appointment1')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

