#!/bin/sh

ROOT=${LUPHORD_ROOT:-~/root}
REPOS=${LUPHORD_REPOS:-~/repos}
REPOS_ENVS_FILE=$(readlink -f repos_envs.txt)

setup_conda() {
    echo
    echo 'Checking for conda...'
    command -v conda >/dev/null 2>&1 \
        || { echo >&2 "conda is required, but not installed (or not in path). Aborting."; exit 1; }
    echo 'Conda is available'
    conda --version
    echo

    echo 'Available conda environments'
    conda env list
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
        git clone $repo
    fi
    cd $repo_folder
    if [ -d .git ] || git rev-parse --git-dir > /dev/null 2>&1; then
        local remote_url=$(git remote get-url origin)
        if [ "$repo" = "$remote_url" ]; then
            echo "Folder $repo_folder is a repository and remote url is correct; pulling..."
            git pull
        else
            echo "Folder $repo_folder is a repository, but remote url is $remote_url, not $repo, please check!"
        fi
    else
        echo "Folder $repo_folder is not a repository, please check!"
        exit 1
    fi
    cd $start_pwd
}

clone_update_repos() {
    echo
    for repo in $(awk '{print $1}' $REPOS_ENVS_FILE); do
        clone_update_repo $repo
    done
    echo
    echo "All repositories available and up-to-date."
    echo
}

echo "Installation base folder will be $ROOT"
echo "Repositories will be cloned into $REPOS"
echo "Reading repositories and environment names from $REPOS_ENVS_FILE"

setup_conda
clone_update_repos