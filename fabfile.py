from fabric.api import *
from fabric.context_managers import cd
from subprocess import *
import os
import tempfile

# globals
env.local_path = os.path.abspath(os.path.dirname(__file__))
env.project_name = 'nlp'
env.project_repo = "https://github.com/jordanorc/nlp.git"

def _paths():
    env.project_path = os.path.join(env.path, env.project_name)
    env.temp_path = tempfile.gettempdir()
    #virtualenv 
    env.virtualenv_root = os.path.join(env.project_path, 'env')
    env.virtualenv_activate = os.path.join(env.virtualenv_root, 'bin', 'activate')
    #project deps
    env.requirements = os.path.join(env.project_path, 'requirements.txt')

def production():
    """
    Use the production webserver
    """
    env.domain = 'localhost'  # domain name
    env.hosts = ['127.0.0.1']
    #env.user = 'www-data'
    env.apache_user = 'www-data'
    env.path = "/var/www"
    env.deployment = 'production'
    _paths()

def staging():
    """
    Use the staging webserver
    """
    env.domain = 'localhost'  # domain name
    env.hosts = ['127.0.0.1']
    env.path = os.path.join(os.path.dirname(__file__), '../')
    env.deployment = 'staging'
    _paths()

def command_exists(command):
    """
    Returns true if a command with the given name exists.
    """
    path = Popen(["which", command], stdout=PIPE, stderr=open(os.devnull, "w")).communicate()[0].strip()
    if path != "":
        return path
    else:
        return False

def apt_install(*args):
    """
    Install packages on the remote server with Apt.
    """
    sudo('apt-get install %s' % " ".join(args))

def easy_install(*args, **kwargs):
    """
    Install packages on the remote server with easy_install.
    """
    params = []
    if kwargs.get('force_upgrade', False):
        params = ['-U']
    sudo('easy_install %s %s' % (" ".join(params), " ".join(args)))

def pip_install(*args):
    """
    Install packages on the remote server with pip.
    """
    run("pip -v install -E %(virtualhost_path)s %s" % (env, " ".join(args)))

def install_requirements():
    """
    Install the required packages from the requirements file using pip.
    """

    require('virtualenv_activate', provided_by=('staging', 'production'))

    with prefix('source %s' % env.virtualenv_activate):
        command = ('pip install -r %(requirements)s')

        run(command % {
            'requirements': env.requirements,
        })

def create_virtualenv():
    """
    Active project's virtual environment.
    """
    run('virtualenv %s' % env.virtualenv_root)

def package():
    local('tar zcf %s/%s.tar.gz --exclude=env .' % (tempfile.gettempdir(), env.project_name))

def deploy():
    require('apache_user', provided_by=('production'))

    package()
    run('mkdir -p %s' % env.project_path)
    put('%s/%s.tar.gz' % (tempfile.gettempdir(), env.project_name), env.project_path)
    with cd(env.project_path):
        run('tar zxf %s.tar.gz' % env.project_name)
        run('rm -rf %s.tar.gz' % env.project_name)

        # configure python
        setup()

        # configure aplication
        with prefix('source %s' % env.virtualenv_activate):
            command = ('python manage.py pynltk --download')
            run(command)

        sudo("chown -R %s ." % (env.apache_user, ))

def setup():
    """
    Install project requirements, create a fresh virtualenv, and make
    required directories.
    """

    #install setup tools
    if not command_exists('easy_install'):
        apt_install('python-setuptools')

    #verify virtual_env
    if not command_exists('virtualenv'):
        easy_install('virtualenv')

    # check last version of distribute
    easy_install('distribute')

    #verify pip
    if not command_exists('pip'):
        easy_install('pip')   

    #active environment
    create_virtualenv()

    #install deps
    install_requirements()

def clean():
    """
    Remove the cruft created by virtualenv and pip
    """
    with cd(env.path):
        run("rm -rf %(virtualhost_path)s" % env)


