#!/bin/bash

ROOT=${LUPHORD_ROOT:-~/root}
REPOS=${LUPHORD_REPOS:-~/repos}
REPOS_ENVS_FILE=$(readlink -f repos_envs.txt)
CONDA=${LUPHORD_CONDA:-conda}
VSCODE=${LUPHORD_VSCODE:-code}

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

install_system_packages() {
    packages=$(cat sys_pkgs.txt)
    echo
    echo "Installing system packages $packages..."
    dry_run || sudo apt update -y
    dry_run || sudo apt install -y $packages
    echo "System package installation completed"
}

install_vscode() {
    echo "Checking for $VSCODE..."
    if command -v $VSCODE >/dev/null 2>&1 ; then
        echo "$VSCODE is available"
    else
        echo "$VSCODE is missing, installing..."
        dry_run || curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg
        dry_run || sudo mv microsoft.gpg /etc/apt/trusted.gpg.d/microsoft.gpg
        dry_run || sudo sh -c 'echo "deb [arch=amd64] https://packages.microsoft.com/repos/vscode stable main" > /etc/apt/sources.list.d/vscode.list'
        dry_run || sudo apt update -y
        dry_run || sudo apt install -y code
        echo  "Installed vscode"
    fi;
}

configure_git() {
    echo
    echo "Configuring git..."
    dry_run || git config --global user.name "luphord"
    dry_run || git config --global user.name "luphord@protonmail.com"
    echo "git configured"
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
    if [ -z $env_name ]; then
        echo "No conda environment name for repo $repo, skipping"
        return 0
    fi;
    echo "Checking for conda env $env_name for repo $repo..."
    case "$AVAILABLE_ENVS" in
        *"$env_name"*)
            echo "$env_name already exists" ;;
        *) echo
            echo "$env_name does not yet exist; creating..."
            dry_run || conda create -y -n $env_name python=3.7 ;;
    esac
    cd $repo_folder
    echo "Activating $env_name..."
    source activate $env_name
    dry_run || pip install -e . -U
    dry_run || pip install -r requirements_dev.txt -U
    conda deactivate
    cd $start_pwd
    echo "Setup of $env_name completed"
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
mkdir -p $ROOT
echo "Repositories will be cloned into $REPOS"
mkdir -p $REPOS
echo "Reading repositories and environment names from $REPOS_ENVS_FILE"

install_system_packages
install_vscode
configure_git
clone_update_repos
setup_conda
create_update_conda_envs
