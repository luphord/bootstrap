from pathlib import Path

user = 'luphord'
user_email = 'luphord@protonmail.com'
repos_base_folder = Path.home() / 'repos'
sys_packages_txt = Path(__file__).parent / 'sys_pkgs.txt'
repos_envs_txt = Path(__file__).parent / 'repos_envs.txt'


def get_sys_packages():
    with open(sys_packages_txt) as f:
        for line in f:
            line = line.strip()
            if line:
                yield line


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
    
    def __str__(self):
        return self.url


def get_repos_envs():
    '''Load repository and environment names from config file'''
    with open(repos_envs_txt) as f:
        for line in f:
            parts = line.split()
            if parts:
                repo = parts[0]
                env = parts[1] if len(parts) > 1 else None
                yield RepoInfo(repo, env)


### TASKS ###


def task_install_system_packages():
    '''Install required system packages via apt'''
    pkg_string = ' '.join(get_sys_packages())
    return {
        'actions': [
            'sudo apt update',
            'sudo apt install -y {}'.format(pkg_string)
        ]
    }


def task_configure_git():
    '''Configure git user and email address'''
    return {
        'actions': [
            'git config --global user.name "{}"'.format(user),
            'git config --global user.email "{}"'.format(user_email)
        ]
    }


def task_clone_repository():
    '''Clone a repository into the specified base folder'''
    for repo_info in get_repos_envs():
        yield {
            'name': repo_info.name,
            'actions': ['git clone {} {}'.format(repo_info.url, repo_info.folder)],
            'targets': [repo_info.dot_git_folder],
            'uptodate': [True] # up to date if target exists
        }


def task_update_repository():
    '''Pull changes of the repository from remote source'''
    for repo_info in get_repos_envs():
        yield {
            'name': repo_info.name,
            'actions': ['git -C {} pull'.format(repo_info.folder)],
            # 'file_dep': [repo_info.dot_git_folder],
            'uptodate': [False] # always pull as we don't know anything about remote source
        }


def task_clone_update_repository():
    '''Clone and/or update a git repository'''
    for repo_info in get_repos_envs():
        yield {
            'name': repo_info.name,
            'actions': ['echo {}'.format(repo_info)]
        }


def task_create_update_conda_env():
    '''Create and/or update a conda environment'''
    for repo_info in get_repos_envs():
        yield {
            'name': repo_info.name,
            'actions': ['echo {} {}'.format(repo_info.url, repo_info.env)]
        }