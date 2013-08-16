from fabric.api import *
from fabric.contrib.files import exists
from fabric.contrib.files import sed

from utils import extract_host


@task
@roles('db')
@parallel
def stop():
    run('service elasticsearch stop')

@task
@roles('db')
@parallel
def start():
    run('service elasticsearch start')

@task
@roles('db')
def restart():
    run('service elasticsearch restart')

@task
@roles('db')
@parallel
def install():
    # download archive
    if not exists('/tmp/elasticsearch-0.90.2.deb'):
        run('wget -P /tmp/ https://download.elasticsearch.org/elasticsearch/elasticsearch/elasticsearch-0.90.2.deb')

    # install elasticsearch
    run('dpkg -i /tmp/elasticsearch-0.90.2.deb')

    # configure cluster name
    sed('/etc/elasticsearch/elasticsearch.yml', '.*cluster.name.*', 'cluster.name: arkoon-bench')
    # disable multicast
    sed('/etc/elasticsearch/elasticsearch.yml', '.*discovery.zen.ping.multicast.enabled.*',
        'discovery.zen.ping.multicast.enabled: false')

    # enable unicast and configure it
    hosts = '['
    hosts += ','.join(map(extract_host, env.roledefs['db']))
    hosts += ']'

    sed('/etc/elasticsearch/elasticsearch.yml', '.*discovery.zen.ping.unicast.hosts.*','discovery.zen.ping.unicast.hosts: ' + hosts)

    tune()
    addplugins()

    # restart service
    run('service elasticsearch restart')


@task
@roles('db')
def tune():
    sed('/etc/init.d/elasticsearch', '.*ES_HEAP_SIZE=.*', 'ES_HEAP_SIZE=2g')
    sed('/etc/elasticsearch/elasticsearch.yml', '.*bootstrap.mlockall:.*', 'bootstrap.mlockall: true')
    sed('/etc/elasticsearch/elasticsearch.yml', '.*indices.memory.index_buffer_size:.*', 'indices.memory.index_buffer_size: 50%')
    sed('/etc/elasticsearch/elasticsearch.yml', '.*index.translog.flush_threshold_ops:.*', 'index.translog.flush_threshold_ops: 50000')


@task
@roles('db')
def addplugins():
    run('/usr/share/elasticsearch/bin/plugin -install karmi/elasticsearch-paramedic')
    run('/usr/share/elasticsearch/bin/plugin -install elasticsearch/elasticsearch-transport-thrift/1.5.0')
    run('/usr/share/elasticsearch/bin/plugin -install mobz/elasticsearch-head')


@task
@roles('db')
def uninstall():
    run('aptitude purge elasticsearch --assume-yes')

