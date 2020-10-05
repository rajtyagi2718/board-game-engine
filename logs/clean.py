from pathlib import Path

"""Remove log files created at runtime."""

KEEP = ('log.py', 'clean.py')
LOGDIR = Path('logs/')

if __name__ == '__main__':

    print('cleaning started.')

    for path in LOGDIR.iterdir():
        if path.is_file() and all(name not in str(path) for name in KEEP):
            # path.unlink()
            print('remove\t{}'.format(path))
        else:
            print('keep\t{}'.format(path))

    print('log files removed!')
