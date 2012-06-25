from django.core.management.base import BaseCommand
from mapstory.watchdog.core import _run_watchdog_suites
from mapstory.watchdog.core import list_suites
from mapstory.watchdog.logs import set_log_state_to_end_of_file
import sys


class Command(BaseCommand):
    help = 'Watchdog functions'
    args = 'mark_log_ok | list | [suite...]'

    def handle(self, *args, **opts):
        if not args:
            print 'need one or more suites to run, or "mark_log_ok" or "list"'
            sys.exit(1)
        if args[0] == 'mark_log_ok':
            set_log_state_to_end_of_file()
        elif args[0] == 'list':
            list_suites()
        else:
            _run_watchdog_suites(*args)