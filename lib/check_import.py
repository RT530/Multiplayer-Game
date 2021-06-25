from multiprocessing.pool import ThreadPool
from subprocess import run, PIPE, STDOUT


def install_package(name):
    run(
        ['pip3', 'install', name],
        shell=False,
        stdout=PIPE,
        stderr=STDOUT
    )


def check_import(*args):
    missing = []
    for name in args:
        try:
            __import__(name.lower())
        except:
            missing.append(name)

    if len(missing) != 0:
        ThreadPool(len(missing)).map(install_package, missing)
