# basic data sanity checks

from mapstory.watchdog.core import CheckFailed
from mapstory.watchdog.core import check
from mapstory.watchdog.core import _config
import os


def suite():
    return (
        check_for_empty_slds,
        check_for_missing_latlng,
        )


def scan_geoserver_data_dir(fn):
    data_dir = _config['GEOSERVER_DATA_DIR']
    assert os.path.exists(data_dir), "data dir does not exist: %s" % data_dir
    result = []
    for root, dirs, files in os.walk(data_dir):
        for f in files:
            full_path = os.path.join(root, f)
            if fn(full_path):
                result.append(full_path)
    return result


def extension(f):
    return os.path.splitext(f)[1]


def files_matching_extension(ext):
    return scan_geoserver_data_dir(lambda x: extension(x) == ext)


@check(email_on_error=True)
def check_for_empty_slds():
    for f in files_matching_extension('.sld'):
        if os.stat(f).st_size == 0:
            raise CheckFailed('Empty sld: %s' % f)


@check(email_on_error=True)
def check_for_missing_latlng():
    for f in scan_geoserver_data_dir(lambda x: x.endswith('featuretype.xml')):
        with open(f) as f:
            if 'latLonBoundingBox' not in f.read():
                raise CheckFailed('Missing latLonBoundingBox in %s' % f.name)
