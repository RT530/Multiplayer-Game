from subprocess import run, PIPE, STDOUT


# This function will install or upgrade the package
def check_import(*args):
    run(
        ['pip', 'install', '--upgrade', *args],
        shell=False,
        stdout=PIPE,
        stderr=STDOUT
    )
