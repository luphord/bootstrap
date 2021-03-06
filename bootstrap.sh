#!/bin/sh

echo "Bootstrapping luphord's dev environment..."

sudo apt update
sudo apt install -y git python3-doit

start_pwd=$(pwd)
tmp_folder=$(echo "/tmp/luphord$RANDOM")
mkdir $tmp_folder
cd $tmp_folder
echo "Working in $tmp_folder"

git clone https://github.com/luphord/bootstrap.git
cd bootstrap
doit -v 2

echo "Setup of luphord's dev environment done; deleting temp folder..."
cd $start_pwd
rm -rf $tmp_folder
echo "Setup completed."
