#!/bin/bash

#################################################################################
# I assume here that:
#     you have a ghost instance installed in /home/ghost/yourblogtitle
#     you will keep the script and the git local repository in /home/ghost/$backupdir
#     you have created a git repository in /home/ghost/$backupdir/$gitrepo
#         ideally cloning a remote repository on a service like GitHub or GitLab
# This script is run hourly as a cronjob for user ghost
##################################################################################
### Setup ###
blogtitle="your-blog-slug-here"
pathtowatch="/home/ghost/$blogtitle/content/data"
filetowatch="ghost.db" 
backupdir="backup"
# using the default Ghost database name here but in case modify accordingly
gitrepo="your-git-repo-here"
cd /home/ghost/$backupdir

if [[ $(find $pathtowatch -mmin -60 -type f -name $filetowatch  2>/dev/null) ]]
   then
      rsync -av $pathtowatch/$filetowatch /home/ghost/$backupdir/ghost-backup.db
      python ~/$backupdir/GGlink.py
      cd ~/$backupdir/$gitrepo
      git push
fi
