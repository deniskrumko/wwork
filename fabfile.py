from fabric.api import local, task


@task
def isort():
    """Fix imports formatting."""
    local('isort wwork -y -rc')


@task
def pep8(path='wwork'):
    """Check PEP8 errors."""
    return local('flake8 --config=.flake8 {}'.format(path))


@task
def lock():
    """Lock dependencies."""
    return local('pipenv lock')


@task
def install_dev():
    """Install packages for local development."""
    return local('pipenv install --dev')
