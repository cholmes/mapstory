from datetime import datetime
from datetime import timedelta
from django.core.management.base import BaseCommand
from mapstory.watchdog.core import _run_watchdog_suites
from mapstory.watchdog.core import clean_runs
from mapstory.watchdog.core import list_suites
from mapstory.watchdog.core import summarize
from mapstory.watchdog.logs import set_log_state_to_end_of_file
import sys


class Command(BaseCommand):
    help = 'Watchdog functions'
    args = ('mark_log_ok | list | clean_runs [older-than-days] '
            '| summarize (day|week) | [suite...]')

    def handle(self, *args, **opts):
        if not args:
            print ('need one or more suites to run, or "mark_log_ok", '
                   '"list", or "clean_runs <days>"')
            sys.exit(1)
        if args[0] == 'mark_log_ok':
            set_log_state_to_end_of_file()
        elif args[0] == 'list':
            list_suites()
        elif args[0] == 'clean_runs':
            ndays = 14
            if len(args) > 1:
                try:
                    ndays = int(args[1])
                except ValueError:
                    pass
            clean_runs(ndays)
        elif args[0] == 'summarize':
            usage = "must specify 'day' or 'week' to summarize"
            if len(args) == 1:
                print usage
                return
            else:
                period = args[1]
                if period not in ('day', 'week'):
                    print usage
                    return
                days = 1
                if period == 'day':
                    days = 1
                elif period == 'week':
                    days = 7
                now = datetime.now()
                delta = timedelta(days=days)
                plain_day = datetime(now.year, now.month, now.day)
                start_time = plain_day - delta
                end_time = plain_day
                summarize(start_time, end_time)
        else:
            _run_watchdog_suites(*args)
