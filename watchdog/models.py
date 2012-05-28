from django.db import models


class CurrentState(models.Model):
    lastrun = models.DateTimeField(auto_now=True)
    geoserver_restarting = models.BooleanField(default=False)
    is_error = models.BooleanField(default=False)

    def __unicode__(self):
        restarting = (u'Geoserver Restarting' if self.geoserver_restarting
                      else u'Geoserver Up')
        error = (u'Last Check Failed' if self.is_error
                 else u'Last Check Passed')

        return u'%s - %s - %s' % (restarting, error,
                                  format_datestring(self.lastrun))


class Run(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    suites = models.TextField(null=False)
    log = models.TextField(null=False)
    is_error = models.BooleanField(default=False)
    errors = models.TextField(null=True)

    def __unicode__(self):
        error_state = self.is_error and u'Faliure' or u'Success'
        return u'%s - %s' % (error_state, format_datestring(self.time))


def format_datestring(dateobject):
    # trim milliseconds off date
    return str(dateobject)[:19]


def create_initial_state():
    state = CurrentState()
    state.save()
    return state


def get_current_state():
    states = CurrentState.objects.all().order_by('id')[:1]
    return states[0] if states else create_initial_state()
