from mapstory.watchdog.core import RestartRequired
from mapstory.watchdog.core import _config
from mapstory.watchdog.core import check_many
from mapstory.watchdog.core import subcheck
from mapstory.watchdog.logs import checksum
from mapstory.watchdog.logs import get_logfile_model
from mapstory.watchdog.logs import read_next_sections


def suite():
    return (
        check_geoserver_log,
        )


@check_many
def check_geoserver_log():
    logpath = _config['GEOSERVER_LOG']
    logfile_model = get_logfile_model(logpath)
    with open(logpath) as f:
        result = read_next_sections(f, logfile_model)
        sections = result['sections']
        logfile_model.offset_start = start = result['offset_start']
        logfile_model.offset_end = end = result['offset_end']
        logfile_model.checksum = checksum(sections, start, end)
        logfile_model.save()
    return [subcheck(fn, name, sections)
            for fn, name in [(_out_of_memory, 'Out of Memory')]]


def _out_of_memory(sections):
    for section in sections:
        for line in section:
            if 'java.lang.OutOfMemoryError: PermGen space' in line:
                raise RestartRequired('Out Of Memory')
