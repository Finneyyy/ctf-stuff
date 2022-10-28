from pathlib import Path
from tempfile import TemporaryDirectory
from subprocess import run, PIPE, DEVNULL, TimeoutExpired

ALLOWED_FLAGS = ['--show-name', '--show-number']
ALLOWED_PARAMS = [
    '--date',     # --date <format>
    '--encoding', # --encoding <encoding>
]

def valid_opts(flags, params):
    def wrapper(f):
        def validate(*args, **kwargs):
            skip = False
            for opt in kwargs['opts']:
                if skip:
                    skip = False
                elif opt in flags:
                    continue
                elif opt in params:
                    skip = True
                else:
                    raise GitError(f'invalid option: {opt}')
            return f(*args, **kwargs)
        return validate
    return wrapper

class GitError(Exception):
    pass

class GitRepo:
    def from_clone(url):
        repo = GitRepo(url)
        repo.clone()
        return repo

    def __init__(self, url):
        self.url = url
        self.tmpdir = TemporaryDirectory()
        self.path = Path(self.tmpdir.name)

    def __enter__(self):
        return self

    def __exit__(self, _exc_type, _exc_value, _traceback):
        self.tmpdir.cleanup()

    def _git(self, cmd, args):
        try:
            proc = run(['git', cmd, *args], stdout=PIPE, stderr=DEVNULL, cwd=self.path.as_posix(), timeout=5)
        except TimeoutExpired:
            raise GitError(f'git {cmd} took too long!')
        if proc.returncode != 0:
            print(f'[git] [{self.path.as_posix()}] git {cmd} failed with {proc.returncode}')
            raise GitError(f'git {cmd} failed!')
        return proc.stdout.decode().strip()

    def clone(self):
        print(f'[git] [{self.path.as_posix()}] Cloning {self.url}')
        return self._git('clone', ['--', self.url, self.path.as_posix()])

    def files(self):
        return self._git('ls-tree', ['--name-only', 'HEAD']).split('\n')

    @valid_opts(ALLOWED_FLAGS, ALLOWED_PARAMS)
    def blame(self, file, opts=[]):
        print(f'[git] [{self.path.as_posix()}] Blaming {file} with {opts}')
        return self._git('blame', [*opts, '--', file])

    def blame_all(self, opts=[]):
        for file in self.files()[:2]: # should be enough :P
            yield self.blame(file, opts=opts)
