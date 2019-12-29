from pathlib import Path

repos_envs_txt = Path(__file__).parent / 'repos_envs.txt'

def task_clone_update_repository():
    '''Clone and/or update a git repository'''
    with open(repos_envs_txt) as f:
        for line in f:
            parts = line.split()
            repo = parts[0]
            env = parts[1] if len(parts) > 1 else None
            yield {
                'name': Path(repo).name,
                'actions': ['echo {} {}'.format(repo, env)]
            }

def task_create_update_conda_env():
    '''Create and/or update a conda environment'''
    with open(repos_envs_txt) as f:
        for line in f:
            parts = line.split()
            repo = parts[0]
            env = parts[1] if len(parts) > 1 else None
            yield {
                'name': Path(repo).name,
                'actions': ['echo {} {}'.format(repo, env)]
            }