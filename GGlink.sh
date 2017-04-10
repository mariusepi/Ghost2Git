#!/bin/bash

#################################################################################
# I assume here that:
#     you have a ghost instance installed in /home/ghost/yourblogtitle
#     you will keep the script and the git local repository in /home/ghost/$backupdir
#     you have created a git repository in /home/ghost/$backupdir/$gitrepo
#         ideally cloning a remote repository on a service like GitHub or GitLab
# This script is run hourly as a cronjob for user ghost
##################################################################################
### Read configuration parameters ###
cd $HOME
source GGprivate/GGconfig.txt

ghostdbpath=$rootdir/$blogslug"/content/data"

#echo $ghostdbpath/$ghostoriginaldb
#echo $rootdir/GGprivate/ghost-backup.db

if [[ $(find $ghostdbpath -mmin -60 -type f -name $ghostoriginaldb  2>/dev/null) ]]
   then
      rsync -av $ghostdbpath/$ghostoriginaldb $rootdir/GGprivate/ghost-backup.db
      python $rootdir/Ghost2Git/GGlink.py
      cd $rootdir/$gitreponame
      git push
fi
