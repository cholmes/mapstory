# logfile parsing routines

from mapstory.watchdog.core import _config
from mapstory.watchdog.core import set_config
from mapstory.watchdog.models import get_logfile_model
import hashlib

LEVELS = set(['INFO', 'WARN', 'DEBUG', 'ERROR'])


def is_logger_line(line):
    return any([(' %s ' % level) in line
                for level in LEVELS])


def log_sections(fileobj):
    sections = []
    next_section = []
    for line in fileobj:
        if is_logger_line(line):
            if next_section:
                sections.append(next_section)
            next_section = [line]
        else:
            next_section.append(line)
    if next_section:
        sections.append(next_section)
    return sections


def checksum(data, start, end):
    if isinstance(data, basestring):
        combined = '%s%s%s' % (start, end, data)
        return hashlib.md5(combined).hexdigest()
    elif isinstance(data, list):
        return checksum(
            ''.join([''.join(section) for section in data]),
            start, end)
    else:
        assert False, "Taking checksum of unknown type: %s" % type(data)


def is_valid(fileobj, logfile_model):
    """verify that the offset is still valid for the file. This may
    not be valid if the log file was truncted or rotated in between
    runs."""
    cur = fileobj.tell()
    start = logfile_model.offset_start
    end = logfile_model.offset_end
    try:
        # check if the logfile_model has a previous offset
        if logfile_model.offset_end == 0:
            return False
        # check that the end offset on the file is greater
        fileobj.seek(0, 2)
        fileend = fileobj.tell()
        if end > fileend:
            return False
        # verify the checksum
        n = end - start
        fileobj.seek(start)
        data = fileobj.read(n)
        if checksum(data, start, end) != logfile_model.checksum:
            return False
        return True
    finally:
        fileobj.seek(cur)


def read_next_sections(fileobj, logfile_model):
    offset = (is_valid(fileobj, logfile_model)
              and logfile_model.offset_end
              or 0)
    fileobj.seek(offset)
    sections = log_sections(fileobj)
    offset_end = fileobj.tell()
    return dict(
        offset_start=offset,
        offset_end=offset_end,
        sections=sections,
        )


def set_log_state_to_end_of_file():
    """Useful to reset the state of a logfile to the end, to pick up only new errors"""
    set_config()
    logpath = _config['GEOSERVER_LOG']
    logfile_model = get_logfile_model(logpath)
    with open(logpath) as fileobj:
        fileobj.seek(0, 2)
        end = fileobj.tell()
    new_checksum = checksum('', end, end)
    logfile_model.checksum = new_checksum
    logfile_model.offset_start = end
    logfile_model.offset_end = end
    logfile_model.save()
