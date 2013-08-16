from fabric.api import *
from fabric.contrib.files import exists
from fabric.contrib.files import sed
from fabric.contrib.files import append
import json

from utils import extract_host


@task
@roles('db')
@parallel
def install():
    if not exists('/etc/apt/sources.list.d/mongodb.list'):
        run('apt-key adv --keyserver keyserver.ubuntu.com --recv 7F0CEB10')
        run('apt-get update')
        append('/etc/apt/sources.list.d/mongodb.list',
               'deb http://downloads-distro.mongodb.org/repo/debian-sysvinit dist 10gen')

    run('aptitude install mongodb-10gen --assume-yes')
    tune()
    configure_cluster()
    


@task
@roles('db')
@parallel
def remove():
    stop()
    run('aptitude purge mongodb-10gen --assume-yes')
    run('rm -rf /var/lib/mongodb/*')

@task
@roles('db')
@parallel
def restart():
    run('service mongodb restart')


@task
@roles('db')
@parallel
@with_settings(warn_only=True)
def stop():
    run('service mongodb stop')

@task
@roles('db')
@parallel
def start():
    run('service mongodb start')


def configure_cluster():

    sed('/etc/mongodb.conf', '.*replSet =.*', 'replSet = eventually')
    run('service mongodb restart')

    # the cluster has to be configured on only one node
    if env.host == extract_host(env.roledefs['db'][0]):
        rsconf = {
            "_id": "eventually",
            "version": 1,
            "members": []
        }
        id = 0
        for machine in env.roledefs['db']:
            host = extract_host(machine)
            host_conf = {"_id": id, "host": host}
            rsconf['members'].append(host_conf)
            id += 1
        if exists('/tmp/init_repl_set.js'):
            run('rm /tmp/init_repl_set.js')
        append('/tmp/init_repl_set.js', 'rs.initiate();')
        append('/tmp/init_repl_set.js', 'rsconf = ' + json.dumps(rsconf))
        append('/tmp/init_repl_set.js', 'rs.reconfig(rsconf, {force:true});')
        append('/tmp/init_repl_set.js', 'rs.status();')
        run('mongo < /tmp/init_repl_set.js')


def tune():
    # tune mongodb
    # disable unused service
    sed('/etc/mongodb.conf', '.*nohttpinterface=.*', 'nohttpinterface=true')

    restart()

