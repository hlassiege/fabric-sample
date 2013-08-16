from fabric.api import run, env, task, roles, parallel, execute
from fabric.contrib.files import exists
from fabric.contrib.files import sed
from fabric.contrib.files import append

from utils import extract_host

CASSANDRA_CONFIG_FILE = '/etc/cassandra/cassandra.yaml'

@task
@roles('db')
@parallel
def install():
    install_package()
    configure()


@task
@roles('db')
@parallel
def uninstall():
    purge_package()
    clean()


def purge_package():
    run('aptitude purge cassandra --assume-yes')


def install_package():
    import_repository_gpg_key()
    fill_repository_settings()
    run('aptitude install cassandra --assume-yes')


def import_repository_gpg_key():
    KEY = '4BD736A82B5C1B00'
    run('gpg --keyserver pgp.mit.edu --recv-keys ' + KEY)
    run('gpg --export --armor ' + KEY + ' | apt-key add -')


def fill_repository_settings():
    append('/etc/apt/sources.list.d/cassandra.list', 'deb http://www.apache.org/dist/cassandra/debian 11x main')
    append('/etc/apt/sources.list.d/cassandra.list', 'deb-src http://www.apache.org/dist/cassandra/debian 11x main')
    run('apt-get update')


def configure_rpc_timeout():
    sed(CASSANDRA_CONFIG_FILE, 'rpc_timeout_in_ms: .*', 'rpc_timeout_in_ms: 20000')


@task
@roles('db')
@parallel
def configure():
    stop()
    configure_rpc_timeout()
    configure_endpoint_snitch()
    configure_seeds()
    configure_listen_address()

    configure_topology()

    start()
    configure_token()


def clean():
    run('rm -rf /{etc,var/{log,lib}}/cassandra/*')


@task
@roles('db')
@parallel
def stop():
    run('service cassandra stop')


@task
@roles('db')
@parallel
def start():
    run('service cassandra start')


@task
@roles('db')
@parallel
def restart():
    run('service cassandra restart')

def configure_token():
    CASSANDRA_MAX_TOKEN = 170141183460469231731687303715884105728
    token_step = CASSANDRA_MAX_TOKEN / len(env.roledefs['db'])

    # Get host number
    host_number = 0
    for host in env.all_hosts:
        if env.host in host:
            break
        host_number += 1

    token = host_number * token_step
    sed(CASSANDRA_CONFIG_FILE,
        'initial_token:.*',
        'initial_token: ' + str(token))

    run('nodetool move ' + str(token))


def configure_endpoint_snitch():
    sed(CASSANDRA_CONFIG_FILE,
        'endpoint_snitch: .*',
        'endpoint_snitch: PropertyFileSnitch')


def configure_seeds():
    sed(CASSANDRA_CONFIG_FILE,
        '- seeds: ".*"',
        '- seeds: "' + extract_host(env.all_hosts[0]) + '"')


def configure_listen_address():
    sed(CASSANDRA_CONFIG_FILE,
        'listen_address: .*',
        'listen_address: ' + env.host)
    sed(CASSANDRA_CONFIG_FILE,
        'rpc_address: .*',
        'rpc_address: ' + env.host)


def configure_topology():
    CASSANDRA_CONFIG_TOPOLOGY = '/etc/cassandra/cassandra-topology.properties'
    if exists(CASSANDRA_CONFIG_TOPOLOGY):
        run('rm ' + CASSANDRA_CONFIG_TOPOLOGY)

    for host in env.all_hosts:
        append(CASSANDRA_CONFIG_TOPOLOGY,
               extract_host(host) + '=DC1:RAC1')

