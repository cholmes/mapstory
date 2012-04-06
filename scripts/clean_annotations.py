"""
Cleanup orphaned annotations layers
"""

import sys
import re
from geonode.maps.models import Map
from geonode.maps.models import Layer

prog = sys.argv[0]
args = sys.argv[1:]

if 'help' in args:
    print "%s [options]" % prog
    print '\t-n dryrun'
    sys.exit(0)
    
matcher = re.compile('_map_(\d+)_annotations')
# find those matching our convention
results = ( (matcher.search(l.name),l) for l in Layer.objects.all() )
# put into dict of mapid -> Layer
results = dict( (int(r[0].group(1)), r[1]) for r in results if r[0] )
# get all the maps by id
existing = Map.objects.in_bulk(results.keys())
# get only the layers that aren't in the map results
delete = [ results[k] for k in results if k not in existing ]

print 'delete layers:'
print '\n'.join(map(lambda d: '\t%s' % d,delete))
if not '-n' in args:
    map(lambda l: l.delete(), delete)

