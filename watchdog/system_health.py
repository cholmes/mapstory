# basic system checks

from mapstory.watchdog.core import CheckFailed
from mapstory.watchdog.core import check
from mapstory.watchdog.core import check_many
from mapstory.watchdog.core import logger
from mapstory.watchdog.core import subcheck
import multiprocessing
import os


def suite():
    return (
        disk_space,
        system_load,
        )

MEGABYTE = 1024 * 1000
LOWSPACE_THRESHOLD = 50 * MEGABYTE
N_CPUS = multiprocessing.cpu_count()
LOAD_THRESHOLD = 2 * N_CPUS


@check_many(email_on_error=True)
def disk_space():
    return [subcheck(check_space_for_path, path, path)
            for path in ('/', '/raid')]


def check_space_for_path(path):
    if not os.path.exists(path):
        logger.warn('%s does not exist for disk space check' % path)
    else:
        disk_stats = os.statvfs(path)
        bytes_available = disk_stats.f_bsize * disk_stats.f_bavail
        if bytes_available < LOWSPACE_THRESHOLD:
            msg = '%s is low on disk space'  % path
            raise CheckFailed(msg)


@check(email_on_error=True)
def system_load():
    """check load average for last 15 minutes"""

    with open('/proc/loadavg') as f:
        loadavg_line = f.read()

    avg = float(loadavg_line.split()[2])
    if avg > LOAD_THRESHOLD:
        raise CheckFailed('Heavy load for last 15 minutes: %s' % avg)
