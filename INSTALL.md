
##Git Installation

**Please note:** These instructions are not exactly plug-and-play and may require some tinkering from your side to adapt them to your specific system. 

**Assumptions:**

- A Ghost instance is installed and running on GNU/Linux server host and you have read and write access to the parent directory. For example, Ghost is installed in /home/ghost/myblog belonging to the user ghost and you have full access to /home/ghost and all its subdirectories. 

- This solution has been tested on a Debian 8 (jessie) server with Python 2.7.9

- The following Python modules are also installed:

  ​	sqlite3

  ​	codecs

  ​	hashlib

  ​	sh

  ​	os

  ​	smtplib

  ​	string

  ​	sys

  ​	configobj

**Preliminary steps:**

1) Git repository setup.

If it does not exist, create a git repository on a service like GitLab or GitHub or similar to store all your blog's posts as markdown files. Let's say that this repository will be called MyBlogPosts. To do this log into, say, GitLab, create a new project, name it e.g. MyBlogPosts and then follow the instructions. If you do not need or want to have a remote git repository you may just create a local one:

```bash
cd
mkdir MyBlogPosts
cd MyBlogPosts
git init
```

2) Gather the necessary information needed for the configuration file. 

In particular regarding the SMTP server, considering that the credentials will be stored in a plaintext file, it is strongly advised that you use either a local SMTP service that does not require authentication, or set up an external SMTP service dedicated to the Ghost blog, perhaps the same one that you have already configured in Ghost's config.js file. Please *do not* use the credentials of your personal email account as exposing the password in plaintext always presents a security hazard.

```bash
# The root directory of your installation, e.g. /home/ghost
rootdir="ROOT DIRECTORY"

# The directory where the Ghost blog is installed, relative path
blogslug="myblog"

# The Ghost original SQLite database filename, using here the default value
ghostoriginaldb="ghost.db"

# The git repository where to store the blog posts
gitreponame="MyBlogPosts"

# Ghost blog parameters
blogurl="THE PUBLIC URL OF YOUR BLOG"
blogtitle="THE BLOG TITLE"

# An SMTP server you have access to for sending emails
server="SMTP SERVER WITH PORT"
username="SMTP username"
password="SMTP password"

# The email address from which to send notifications
from_addr="NOTIFICATIONS FROM ADDRESS"

# A system email address to notify the administrator and/or editors
sysemail="A SYSTEM EMAIL ADDRESS"
```

As user *ghost* run the following commands:

```bash
# Start from ghost home dir
cd

# Create private directory for storing the configuration file and local copies of the Ghost database
cd
mkdir GGprivate
chmod 0600 GGprivate

# Clone the repository
git clone https://github.com/mariusepi/Ghost2Git.git

# Change dir into downloaded repository
cd Ghost2Git

# Edit configuration file specifying all parameters and restrict the access to it
chmod 0600 ../GGprivate/GGconfig.txt
vi ../GGprivate/GGconfig.txt

# Copy an empty instance of the auxiliary database 
# to the directory containing your private data
cp GGlink.db ../GGprivate/

# Make the shell script executable
chmod u+x GGlink.sh

# Manually execute the script for the first time
bash GGlink.sh
```
At the first run it will:

-  make a copy (with rsync) of the Ghost SQLite database to avoid accessing the original even if in read only mode;

-  populate the repository creating a markdown file for each post especially if you have many posts already archived the first execution may take some time;

To avoid spamming authors and editors with notifications about old posts that are being addedd to the git repository just now, the sending of emails to users and editors is disabled in the python script by default. You can enable the email notification service uncommenting the 

```
#send_email(...)
```

lines in the python script.

If everything goes well, you may run the shell script periodically as an hourly cronjob

```bash
crontab -e
```

Alternatively, and arguably more elegantly and efficiently, one could setup a filesystem event monitoring with programs like *watch* or *inotify* that triggers the execution of the script when the original Ghost database is modified. 

