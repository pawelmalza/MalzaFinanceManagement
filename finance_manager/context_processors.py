from django.utils import timezone


def my_context_processor(request):
    version = (0,2)
    time = timezone.now()
    user_name = request.user.username

    return {"version": version, "time": time, "user_name": user_name}