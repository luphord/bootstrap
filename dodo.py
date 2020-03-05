from pathlib import Path
import subprocess
import os
import json
import urllib.request

user = 'luphord'
user_email = 'luphord@protonmail.com'
repos_base_folder = Path.home() / 'repos'
local_install_base_folder = Path.home() / 'root'
miniconda_install_folder = local_install_base_folder / 'miniconda3'
sys_packages_txt = Path(__file__).parent / 'sys_pkgs.txt'
repos_envs_txt = Path(__file__).parent / 'repos_envs.txt'
repos_url = 'https://api.github.com/users/luphord/repos'
conda_env_python_version = '3.7'
vscode_command = 'code'
conda_command = 'conda'
miniconda_setup = Path.home() / 'Downloads' / 'miniconda.sh'


def get_sys_packages():
    with sys_packages_txt.open() as f:
        for line in f:
            line = line.strip()
            if line:
                yield line


def get_installed_sys_packages():
    dpkg_out = subprocess.run(['dpkg', '--list'],
                               stdout=subprocess.PIPE).stdout.decode('utf8')
    for line in dpkg_out.splitlines():
        parts = line.split()
        if len(parts) > 1:
            yield parts[1]


def all_sys_packages_installed():
    '''Check if all required sys packages are already installed'''
    required_pkgs = set(get_sys_packages())
    available_pkgs = set(get_installed_sys_packages())
    return required_pkgs.issubset(available_pkgs)


def get_git_config_iter():
    git_out = subprocess.run(['git', 'config', '--list'],
                             stdout=subprocess.PIPE).stdout.decode('utf8')
    for line in git_out.splitlines():
        parts = line.split('=')
        if len(parts) > 1:
            yield parts[:2]


def get_git_config():
    return dict(get_git_config_iter())


def is_git_config_uptodate():
    cfg = get_git_config()
    return cfg.get('user.email') == user_email \
        and cfg.get('user.name') == user


class RepoInfo:
    '''Meta information about a git repository and its local file paths'''
    def __init__(self, repo_url, env, repos_base_folder=repos_base_folder):
        self.url = repo_url
        self.env = env
        self.repos_base_folder = Path(repos_base_folder)

    @property
    def name(self):
        return Path(self.url).name
    
    @property
    def folder(self):
        return self.repos_base_folder / Path(self.url).stem
    
    @property
    def dot_git_folder(self):
        return self.folder / '.git'
    
    @property
    def requirements_dev(self):
        return self.folder / 'requirements_dev.txt'
    
    @property
    def conda_run(self):
        return '{} run -n {}'.format(conda_command, self.env)
    
    def __str__(self):
        return self.url


def get_repos_envs():
    '''Load repository and environment names from config file'''
    with repos_envs_txt.open() as f:
        for line in f:
            parts = line.split()
            if parts:
                repo = parts[0]
                env = parts[1] if len(parts) > 1 else None
                yield RepoInfo(repo, env)


def update_repo_env_list():
    '''Update config file containing repositories by querying github API
       for new projects.'''
    repos_envs_dict = {repo_info.url: repo_info for repo_info in get_repos_envs()}
    with urllib.request.urlopen(repos_url) as f:
        repos = json.loads((f.read().decode('utf-8')))

        for repo in repos:
            repo_url = repo['clone_url']
            if not repo_url in repos_envs_dict:
                print('Adding {} to {}...'.format(repo_url, repos_envs_txt))
                repos_envs_dict[repo_url] = None

        with repos_envs_txt.open('w') as f:
            for repo, repo_info in sorted(repos_envs_dict.items()):
                if repo_info and repo_info.env:
                    line = '{}\t{}'.format(repo, repo_info.env)
                else:
                    line = repo
                f.write(line + os.linesep)


def get_existing_envs():
    '''Get existing conda environments with their path'''
    conda_out = subprocess.run([conda_command, 'env', 'list'],
                               stdout=subprocess.PIPE).stdout.decode('utf8')
    for line in conda_out.splitlines():
        if not line or line.startswith('#') or line.startswith(' '):
            continue
        parts = line.split()
        if len(line) < 2:
            continue
        yield (parts[0], parts[-1])


def env_exists(env):
    envs = dict(get_existing_envs())
    return env in envs


### TASKS ###


def task_install_system_packages():
    '''Install required system packages via apt'''
    pkg_string = ' '.join(get_sys_packages())
    return {
        'actions': [
            'sudo apt update',
            'sudo apt install -y {}'.format(pkg_string)
        ],
        'uptodate': [all_sys_packages_installed]
    }


def task_install_vscode():
    '''Install Visual Studio Code'''
    return {
        'actions': [
            'curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg',
            'sudo mv microsoft.gpg /etc/apt/trusted.gpg.d/microsoft.gpg',
            'sudo sh -c \'echo "deb [arch=amd64] https://packages.microsoft.com/repos/vscode stable main" > /etc/apt/sources.list.d/vscode.list\'',
            'sudo apt update -y',
            'sudo apt install -y code'
        ],
        'uptodate': ['command -v {}'.format(vscode_command)]
    }


def task_download_miniconda():
    '''Download miniconda'''
    return {
        'actions': ['wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O {}'.format(miniconda_setup)],
        'targets': [miniconda_setup],
        'uptodate': [True]  # up to date if target exists
    }


def task_install_conda():
    '''Install conda'''
    return {
        'actions': [
            'chmod +x {}'.format(miniconda_setup),
            '{} -b -p {}'.format(miniconda_setup, miniconda_install_folder),
            'echo \'PATH="${{PATH}}:{}"; export PATH\' >> ${{HOME}}/.bashrc'.format(miniconda_install_folder / 'bin'),
            'source ${{HOME}}/.bashrc',
            'conda init'
        ],
        'task_dep': ['download_miniconda'],
        'uptodate': ['command -v {}'.format(conda_command)]
    }


def task_configure_git():
    '''Configure git user and email address'''
    return {
        'actions': [
            'git config --global user.name "{}"'.format(user),
            'git config --global user.email "{}"'.format(user_email)
        ],
        'task_dep': ['install_system_packages'],
        'uptodate': [is_git_config_uptodate]
    }

def task_setup_docker():
    '''Setup docker group'''
    return {
        'actions': [
            'sudo groupadd -f docker',
            'sudo usermod -aG docker $USER'
        ],
        'task_dep': ['install_system_packages'],
        'uptodate': [False]
    }


def task_clone_repository():
    '''Clone a repository into the specified base folder'''
    for repo_info in get_repos_envs():
        yield {
            'name': repo_info.name,
            'actions': ['git clone {} {}'.format(repo_info.url, repo_info.folder)],
            'targets': [repo_info.dot_git_folder],
            'task_dep': ['configure_git'],
            'uptodate': [True] # up to date if target exists
        }


def task_update_repository():
    '''Pull changes of the repository from remote source'''
    for repo_info in get_repos_envs():
        yield {
            'name': repo_info.name,
            'actions': ['git -C {} pull'.format(repo_info.folder)],
            'task_dep': ['clone_repository:{}'.format(repo_info.name)],
            'uptodate': [False] # always pull as we don't know anything about remote source
        }


def task_create_conda_env():
    '''Create a conda environment'''
    for repo_info in get_repos_envs():
        if repo_info.env:
            yield {
                'name': repo_info.env,
                'actions': ['{} create -y -n {} python={}'.format(conda_command,
                                                                  repo_info.env,
                                                                  conda_env_python_version)],
                'task_dep': [
                    'install_conda',
                    'clone_repository:{}'.format(repo_info.name)
                ],
                'uptodate': [lambda env=repo_info.env: env_exists(env)]
            }


def task_update_conda_env():
    '''Update a conda environment'''
    for repo_info in get_repos_envs():
        if repo_info.env:
            yield {
                'name': repo_info.env,
                'actions': [
                    '{} pip install -e {} -U'.format(repo_info.conda_run,
                                                     repo_info.folder),
                    '{} pip install -r {} -U'.format(repo_info.conda_run,
                                                     repo_info.requirements_dev)],
                'task_dep': ['create_conda_env:{}'.format(repo_info.env)]
            }

def task_setup_dev_environment():
    '''Meta-task for a complete setup of dev environment'''
    return {
        'actions': ['echo "DEV environment setup complete"'],
        'task_dep': [
            'install_vscode',
            'setup_docker',
            'update_repository',
            'update_conda_env'
        ]
    }


def task_update_repo_env_list():
    '''Update config file containing repositories by querying github API
       for new projects.'''
    return {
        'actions': [update_repo_env_list],
        'uptodate': [False]
    }

DOIT_CONFIG = {'default_tasks': ['setup_dev_environment']}
