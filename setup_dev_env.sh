#!/bin/sh

ROOT=${LUPHORD_ROOT:-~/root}
REPOS=${LUPHORD_REPOS:-~/repos}
REPOS_ENVS_FILE=$(readlink -f repos_envs.txt)

clone_update_repo() {
    echo "Checking for repository $1"
}

echo "Installation base folder will be $ROOT"
echo "Repositories will be cloned into $REPOS"
echo "Reading repositories and environment names from $REPOS_ENVS_FILE"

for repo in $(awk '{print $1}' $REPOS_ENVS_FILE); do
    clone_update_repo $repo
done