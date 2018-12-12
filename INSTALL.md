
## Ghost2Git Installation and setup

**Please note:** These instructions are not exactly plug-and-play and may require some tinkering from your side to adapt them to your specific system. 

**Assumptions:**

- A Ghost instance -- either verson 0.x or 1.x or 2.x -- is installed and running on GNU/Linux server host and you have read and write access to the parent directory. For example, Ghost is installed in /home/USER/myblog belonging to the user USER and you have full access to /home/USER and all its subdirectories. 

- This solution has been tested on a Debian 8 (jessie) server with Python 2.7.9

- The following Python modules are also installed:

  - sqlite3
  - codecs
  - hashlib
  - sh
  - os
  - smtplib
  - string
  - sys
  - configobj

### Preliminary steps:

**1) Git repository setup**

If it does not exist, create a git repository on a service like GitLab or GitHub or similar to store all your blog's posts as markdown files. Let's say that this repository will be called MyBlogPosts. To do this log into, say, GitLab, create a new project, name it e.g. MyBlogPosts and then follow the instructions. If you do not need or want to have a remote git repository you may just create a local one. We will assume that this is under ~/backup/MyBlogPosts but you can place it wherever you like

```bash
cd ~/backup
mkdir MyBlogPosts
cd MyBlogPosts
git init
```

**2) Gather the necessary information needed for the configuration file** 

In particular regarding the SMTP server, considering that the credentials will be stored in a plaintext file, it is strongly advised that you use either a local SMTP service that does not require authentication, or set up an external SMTP service dedicated to the Ghost blog, perhaps the same one that you have already configured in Ghost's config.js file. Please *do not* use the credentials of your personal email account as exposing the password in plaintext always presents a security hazard.



## Istallation, configuration and first run

As the user *USER* run the following commands:

```bash
# Start from the USER's home dir, or the parent dir of the Ghost blog installation
cd ~

# Clone the Ghost2Git repository
git clone https://github.com/mariusepi/Ghost2Git.git

# Create a private directory for storing the configuration file and local copies of the Ghost database
mkdir GGprivate
chmod 0700 GGprivate

# Copy the template configuration file into the private directory, limit access to it, and edit it:
cp Ghost2Git/GGconfig.txt GGprivate
chmod 0600 GGprivate/GGconfig.txt
vi GGprivate/GGconfig.txt

###### Mail server
server="SERVER NAME"
from_addr="MAIN SENDING ADDRESS"
username="USERNAME"
password="PASSWORD"

###### Original Ghost database
ghostdbpath="MAINDIR/content/data/ghost.db"
ghostoriginaldb="ghost.db"

###### Blog paramenters
blogurl="BLOG EXTERNAL URL"
blogtitle="BLOG TITLE"
sysemail="SYSTEM EMAIL TO SEND NOTIFICAITONS FROM"
blogslug="BLOGSLUG"

##### GG parameters
#dbhash_filename="/home/USER/private/GGlink.db"
rootdir="/home/USER"
privatedir="GGprivate"
GGdir="Ghost2Git"
gitreponame="/backup/BLOG-LOCAL-GIT-REPOSITORY"
# using the default Ghost database name here but in case modify accordingly
emailswitch="OFF"

# Copy an empty instance of the auxiliary database 
# to the directory containing your private data
cp Ghost2Git/GGlink.db GGprivate/

# Change dir into downloaded repository
cd Ghost2Git

# Manually execute the script for the first time
bash GGlink.sh

```

At the first run it will:

-  make a copy (with rsync) of the Ghost SQLite database to avoid accessing the original even if in read only mode;

-  populate the repository creating a plain text and an html file for each post. If you have many posts already archived in your blog, the first execution may take some time.

### Enable email notifications

To avoid spamming authors and editors with notifications about old posts that are being addedd to the git repository just now, the sending of emails to users and editors is disabled in the python script by default. You can enable the email notification service in the configuration file setting the variable  

```bash
emailswitch="ON"
```

### Create cronjob

If everything goes well, at this point you should be able to browse all your posts as markdown files in the repository you set-up at the beginning. Future revisions will be traced using git tools. 

As a final step, you may run the shell script periodically as an hourly cronjob

```bash
crontab -e
```

Alternatively, and arguably more elegantly and efficiently, one could setup a filesystem event monitoring with programs like *watch* or *inotify* that triggers the execution of the script when the original Ghost database is modified. 
