from django.core.management.base import BaseCommand
from mapstory.watchdog.core import _run_watchdog_suites
import sys

class Command(BaseCommand):
    help = 'Watchdog functions'
    args = '[suite...]'

    def handle(self, *args, **opts):
        if not args:
            print 'need one or more suites to run'
            sys.exit(1)
        _run_watchdog_suites(*args)
