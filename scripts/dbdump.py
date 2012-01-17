from django.conf import settings
from subprocess import Popen 
from subprocess import PIPE 

"""
Dump mapstory databases - originally a shell script and mostly uses shell commands instead of psycopg2,
but takes advantage of using django settings

"""

def dump(db, user):
    args = ['psql',
        '--host=localhost',
        '--tuples-only',
        '--username=%s' % user,
        '--command=SELECT table_name FROM information_schema.tables WHERE table_schema=\'public\';',
        db
    ] 
    proc = Popen(args,stdout=PIPE)
    proc.wait()
    table_names = map(lambda s: s.strip(), proc.stdout.readlines())
   
    args = ['pg_dump',
        '--no-owner',
        '--host=localhost',
        '--username=%s' % user,
        '--create',
        '--format=c',
        '--file=%s.dump' % db]
    for t in table_names:
        if t:
            args.append('--table="%s"' % t)
    args.append(db)
    proc = Popen(args)
    proc.wait()

dump(settings.DATABASE_NAME,settings.DATABASE_USER)
dump(settings.DB_DATASTORE_DATABASE,settings.DB_DATASTORE_USER)




