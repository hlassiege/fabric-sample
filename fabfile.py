import mongodb, elasticsearch, java, cassandra
from fabric.api import *
from fabric.operations import put

env.roledefs = {
    'test': ['localhost'],
    'db': ['root@192.168.0.1', 'root@192.168.0.2', 'root@192.168.0.3']
}

@task
@roles('db')
@parallel
def system():
    # change system keep alive
    run('echo 300 > /proc/sys/net/ipv4/tcp_keepalive_time')
    run('ulimit -m 65536')
    run('ulimit -n 64000')
    run('ulimit -l unlimited')

