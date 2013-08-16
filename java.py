from fabric.api import *


@task
@parallel
@roles('db')
def java():
    run('apt-get install openjdk-7-jdk --assume-yes')
