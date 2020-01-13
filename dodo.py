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

def get_repos_envs():
    '''Load repository and environment names from config file'''
    with open(repos_envs_txt) as f:
        for line in f:
            parts = line.split()
            if parts:
                repo = parts[0]
                env = parts[1] if len(parts) > 1 else None
                yield repo, env

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
    for repo_url, _ in get_repos_envs():
        repo_folder = repos_base_folder / Path(repo_url).stem
        yield {
            'name': Path(repo_url).name,
            'actions': ['git clone {} {}'.format(repo_url, repo_folder)],
            'targets': [repo_folder / '.git'],
            'uptodate': [True] # up to date if target exists
        }

def task_clone_update_repository():
    '''Clone and/or update a git repository'''
    for repo, _ in get_repos_envs():
        yield {
            'name': Path(repo).name,
            'actions': ['echo {}'.format(repo)]
        }

def task_create_update_conda_env():
    '''Create and/or update a conda environment'''
    for repo, env in get_repos_envs():
        yield {
            'name': Path(repo).name,
            'actions': ['echo {} {}'.format(repo, env)]
        }