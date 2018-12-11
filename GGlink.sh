#!/bin/bash

#################################################################################
# I assume here that:
#     you have a ghost instance installed in /$rootdir
#     you will keep the script and the git local repository in /home/$user/backup
#     you have created a git repository in /home/$user/backup/$gitrepo
#         ideally cloning a remote repository on a service like GitHub or GitLab
# This script is run hourly as a cronjob for user ghost
##################################################################################

### Read configuration parameters ###
cd $HOME
source $HOME/GGprivate/GGconfig.txt

#echo $ghostdbpath/$ghostoriginaldb
#echo $rootdir/GGprivate/ghost-backup.db

if [[ $(find $ghostdbpath -mmin -60 -type f -name $ghostoriginaldb  2>/dev/null) ]]
   then
      rsync -av $ghostdbpath/$ghostoriginaldb $HOME/GGprivate/ghost-backup.db
      python $HOME/Ghost2Git/GGlink1.py
      cd $rootdir/$gitreponame
      git push
fi
