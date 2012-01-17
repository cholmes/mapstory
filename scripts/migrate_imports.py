from django.conf import settings
import psycopg2
import os

"""
Migrate spatial data out of a postgis database into another.

Almost a throw away process, but not quite.

This must be run as the postgres user, though this could be fixed
"""

src_db = "geonode"
dest_db = settings.DB_DATASTORE_DATABASE
user = settings.DB_DATASTORE_USER
drop_tables = False 
dump = False

if not any(dump,drop_tables):
    import sys
    print 'manually set one of dump or drop_tables'
    sys.exit(1)

src = psycopg2.connect("dbname='" + src_db + "' user='" + settings.DB_DATASTORE_USER + "'  password='" + settings.DB_DATASTORE_PASSWORD + "' port=" + settings.DB_DATASTORE_PORT + " host='" + settings.DB_DATASTORE_HOST + "'")

dest = psycopg2.connect("dbname='" + settings.DB_DATASTORE_DATABASE + "' user='" + settings.DB_DATASTORE_USER + "'  password='" + settings.DB_DATASTORE_PASSWORD + "' port=" + settings.DB_DATASTORE_PORT + " host='" + settings.DB_DATASTORE_HOST + "'")

src_cursor = src.cursor()
dest_cursor = dest.cursor()

query = lambda sql: src_cursor.execute(sql) or set( t[0] for t in src_cursor.fetchall())

# get a list of all tables
all_tables = query("select tablename from pg_tables where schemaname = 'public'")

# then a list of those listed as geom_tables
geom_tables = query("select f_table_name from geometry_columns;")

# the result should be those that existing in both sets
existing = all_tables & geom_tables

# run geometry columns first as current user
if dump:
    cmd = 'pg_dump --format=c --create --table=%s --username=%s %s | pg_restore --dbname=%s --clean' % ('geometry_columns',user,src_db,dest_db)
    os.system(cmd)

# then dump and load all geometry tables
# note: the builtin funtions copyto/copyfrom provided in psycopg could have been used
#  though this is slightly more efficient since we are piping
for e in existing:
    if drop_tables:
        print "dropping %s" % e
        src_cursor.execute('DROP TABLE "%s"'% e)
        src.commit()
    if dump:
        print 'dumping %s' % e
        cmd = 'pg_dump --format=c --create --table=%s --username=%s %s | pg_restore --dbname=%s --clean --username=%s ' % (e,user,src_db,dest_db,user)
        os.system(cmd)



