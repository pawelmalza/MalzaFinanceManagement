from django.utils import timezone


def my_context_processor(request):
    version = "0.5"
    time = timezone.now()
    user = request.user

    return {"version": version, "time": time, "user": user}