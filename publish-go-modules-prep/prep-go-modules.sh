#!/bin/bash
ORIGDIR=$PWD
MODPATH=$1
if [ -z $MODPATH ]
then
    echo "Path to the mod directory must be set"
    exit 1
fi

# run python script which goes through the entire pkg/mod subtree
# and changes every instance of "![a-z]" to [A-Z]. This is required
# to be able to use the modules properly after they are pushed to Artifactory
python3 ./change_dir.py $MODPATH

# run go mod init on directories where it's needed
cd $MODPATH
sudo chmod -R 777 .

FOLDER=$PWD
find . -type d -print | grep -v '@.*/' | grep -v 'cache' | grep '@.*' > modules-dir
for i in $(cat modules-dir); do echo "$i"; cd $i; go mod init $(pwd | rev | cut -d '/' -f1-3 | rev | cut -d '@' -f1); cd $FOLDER; done

# push cache modules
cp -r cache $ORIGDIR
cd $ORIGDIR/cache/download
