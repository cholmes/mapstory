from django.core.management.base import BaseCommand
import logging
from optparse import make_option
import traceback
from mapstory.watchdog.core import *
import sys

class Command(BaseCommand):
    help = 'Watchdog functions'
    args = '[suite...]'
#    option_list = BaseCommand.option_list + (
#        make_option('--update', dest="update", default=False, action="store_true",
#            help="Update any existing entries"),
#    )

    def handle(self, *args, **opts):
        if not args:
            print 'need one or more suites to run'
            sys.exit(1)
        run_watchdog_suites(*args)
    