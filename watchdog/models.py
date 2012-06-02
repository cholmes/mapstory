from django.db import models
import os


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


class Logfile(models.Model):
    filepath = models.TextField(null=False, unique=True)
    offset_start = models.IntegerField(null=False)
    offset_end = models.IntegerField(null=False)
    checksum = models.TextField(null=False)

    def __unicode__(self):
        return u'%s (%s, %s) -> %s' % (
            self.filepath, self.offset_start, self.offset_end, self.checksum)


def format_datestring(dateobject):
    # trim milliseconds off date
    return str(dateobject)[:19]


def create_initial_state():
    state = CurrentState()
    state.save()
    return state


def create_logfile_model(filepath):
    return Logfile(
        filepath=filepath, offset_start=0, offset_end=0, checksum='')


def get_current_state():
    states = CurrentState.objects.all().order_by('id')[:1]
    return states[0] if states else create_initial_state()


def get_logfile_model(filepath):
    if not os.path.isfile(filepath):
        raise Exception('Invalid log path: %s' % filepath)
    logfiles = Logfile.objects.filter(filepath=filepath)
    return logfiles[0] if logfiles else create_logfile_model(filepath)
