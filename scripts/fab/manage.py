from fabric.operations import *
from fabric.context_managers import *
from fabric.api import *
import os

env.use_ssh_config=True
env.hosts = ['mapstory.dev.opengeo.org']
env.deploy_user = 'geonode'
env.activate = 'source ~geonode/geonode/bin/activate'

mapstory = os.path.dirname(__file__) + "/../.."
user_home = '/home/%s' % env.deploy_user

#
# helpers
#
def lscript(name):
    with lcd(mapstory):
        local('PYTHONPATH=.. python scripts/%s' % name)
        
def script(name):
    virtualenv('python mapstory/scripts/%s' % name)

def virtualenv(command):
    with cd(user_home):
        sudo('%s && %s' % (env.activate, command), user = env.deploy_user)
        
#
# tasks
#
def update_geonode_client():
    virtualenv('JAVA_HOME=/usr/lib/jvm/java-6-sun ./do_update.sh')
    
def get_layer(layer):
    script('export_layer.py %s' % layer)
    pkg = '%s-extract.zip' % layer
    rpkg = '%s/%s' % (user_home,pkg)
    get(rpkg,'.')
    lscript('import_layer.py -d ../geonode/gs-data %s' % pkg)
    sudo('rm %s' % rpkg,user = env.deploy_user)