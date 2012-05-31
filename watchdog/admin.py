from django.contrib import admin
from mapstory.watchdog.models import CurrentState
from mapstory.watchdog.models import Run

admin.site.register(CurrentState)
admin.site.register(Run)
