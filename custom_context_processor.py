from dz import dz_array
from payapp.models import Notification

'''
A context processor is a function that accepts an argument and returns a dictionary as its output.
In our case, the returning dictionary is added as the context and the biggest advantage is that,
it can be accessed globally i.e, across all templates. 
'''

def dz_static(request):
    # we can send data as {"dz_array":dz_array} than you get all dict, using <h1>{{ dz_array }}</h1>
    return {"dz_array":dz_array}

def notifications_handler(request):
    try:
        notifications = Notification.objects.filter(receiver_id=request.user.id).prefetch_related('sender',
                                                                                                  'invoice').order_by(
            '-id').all()
    except Notification.DoesNotExist:
        notifications = None
    notification_count = notifications.count()
    return {
        'notifications': notifications,
        'notification_count': notification_count,
    }
