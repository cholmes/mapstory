from functools import wraps
from django.contrib import messages
from avatar import views

class MessageSet(object):
    def __init__(self, req):
        self.req = req
    def create(self, message):
        pass
        # messages.add_message(self.req, messages.INFO, message)

def monkey_patch(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        args[0].user.message_set = MessageSet(args[0])
        return func(*args, **kwargs)
    return wrapper

views.add = monkey_patch(views.add)
views.change = monkey_patch(views.change)
views.delete = monkey_patch(views.delete)