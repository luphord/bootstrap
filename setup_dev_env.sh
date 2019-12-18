#!/bin/sh

ROOT=${LUPHORD_ROOT:-~/root}
REPOS=${LUPHORD_REPOS:-~/repos}
REPOS_ENVS_FILE=$(readlink -f repos_envs.txt)
CONDA=${LUPHORD_CONDA:-conda}

dry_run() {
    if [ "$LUPHORD_DRY_RUN" = true ]; then
        echo "Dry run; skipping action."
        return 0
    else
        return 1
    fi
}

parallel_run() {
    if [ "$LUPHORD_PARALLEL" = true ]; then
        return 0
    else
        return 1
    fi
}

error_echo() {
    echo "$@" 1>&2;
}

setup_conda() {
    echo
    echo "Checking for $CONDA..."
    command -v $CONDA >/dev/null 2>&1 \
        || { error_echo "$CONDA is required, but not installed (or not in path). Aborting."; return 1; }
    echo "$CONDA is available"
    $CONDA --version
    echo

    echo 'Available conda environments:'
    AVAILABLE_ENVS=$(conda env list | tail -n +3 | awk '{ print $1 }')
    echo $AVAILABLE_ENVS
    export $AVAILABLE_ENVS
    echo
}

clone_update_repo() {
    local start_pwd=$(pwd)
    local repo=$1
    local repo_folder=$REPOS/$(basename -s .git $repo)
    echo "----"
    echo "Checking for repository $repo in $repo_folder..."
    if [ ! -d $repo_folder ]; then
        echo "Folder $repo_folder does not exist, cloning repository..."
        cd $REPOS
        dry_run || git clone $repo
    fi
    cd $repo_folder
    if [ -d .git ] || git rev-parse --git-dir > /dev/null 2>&1; then
        local remote_url=$(git remote get-url origin)
        if [ "$repo" = "$remote_url" ]; then
            echo "Folder $repo_folder is a repository and remote url is correct; pulling..."
            dry_run || git pull
        else
            error_echo "Folder $repo_folder is a repository, but remote url is $remote_url, not $repo, please check!"
        fi
    else
        error_echo "Folder $repo_folder is not a repository, please check!"
        return 1
    fi
    cd $start_pwd
}

clone_update_repos() {
    echo
    for repo in $(awk '{print $1}' $REPOS_ENVS_FILE); do
        parallel_run && clone_update_repo $repo &
        parallel_run || clone_update_repo $repo || exit 1
    done
    wait
    echo
    echo "All repositories available and up-to-date."
    echo
}

create_update_conda_env() {
    local start_pwd=$(pwd)
    local repo=$1
    local env_name=$2
    local repo_folder=$REPOS/$(basename -s .git $repo)
    echo "----"
    echo "Checking for conda env $env_name for repo $repo..."
    case "$AVAILABLE_ENVS" in
        *"$env_name"*)
            echo "$env_name already exists" ;;
        *) echo
            echo "$env_name does not yet exist; creating..." ;;	
    esac
}

create_update_conda_envs() {
    echo
    echo "Creating and updating conda environments..."
    cat $REPOS_ENVS_FILE | while read line 
    do
        create_update_conda_env $line
    done
    echo
    echo "All conda environments available and up-to-date."
    echo
}

echo "Installation base folder will be $ROOT"
echo "Repositories will be cloned into $REPOS"
echo "Reading repositories and environment names from $REPOS_ENVS_FILE"

setup_conda
clone_update_repos
create_update_conda_envs
