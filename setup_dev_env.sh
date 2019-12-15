#!/bin/sh

ROOT=${LUPHORD_ROOT:-~/root}
REPOS=${LUPHORD_REPOS:-~/repos}
REPOS_ENVS_FILE=$(readlink -f repos_envs.txt)

clone_update_repo() {
    local start_pwd=$(pwd)
    local repo=$1
    local repo_folder=$REPOS/$(basename -s .git $repo)
    echo "----"
    echo "Checking for repository $repo in $repo_folder..."
    if [ ! -d $repo_folder ]; then
        echo "Folder $repo_folder does not exist, cloning repository..."
        cd $REPOS
    fi
    cd $repo_folder
    if [ -d .git ] || git rev-parse --git-dir > /dev/null 2>&1; then
        local remote_url=$(git remote get-url origin)
        if [ "$repo" = "$remote_url" ]; then
            echo "Folder $repo_folder is a repository and remote url is correct; pulling..."
        else
            echo "Folder $repo_folder is a repository, but remote url is $remote_url, not $repo, please check!"
        fi
    else
        echo "Folder $repo_folder is not a repository, please check!"
        exit 1
    fi
    cd $start_pwd
}

echo "Installation base folder will be $ROOT"
echo "Repositories will be cloned into $REPOS"
echo "Reading repositories and environment names from $REPOS_ENVS_FILE"

for repo in $(awk '{print $1}' $REPOS_ENVS_FILE); do
    clone_update_repo $repo
done