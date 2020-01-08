from pathlib import Path

user = 'luphord'
user_email = 'luphord@protonmail.com'
repos_envs_txt = Path(__file__).parent / 'repos_envs.txt'

def get_repos_envs():
    '''Load repository and environment names from config file'''
    with open(repos_envs_txt) as f:
        for line in f:
            parts = line.split()
            repo = parts[0]
            env = parts[1] if len(parts) > 1 else None
            yield repo, env

def task_configure_git():
    '''Configure git user and email address'''
    return {
        'actions': [
            'echo configuring git user {}'.format(user),
            'echo configuring git email {}'.format(user_email)
        ]
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