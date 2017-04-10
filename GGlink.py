#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3
import codecs
import hashlib
import sh

import os
import smtplib
import string
import sys

from configobj import ConfigObj

#----------------------------------------------------------------------
# Read configuration parameters

base_path = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(base_path, "../GGprivate/GGconfig.txt") 

if os.path.exists(config_path):
    cfg = ConfigObj(config_path)
    cfg_dict = cfg.dict()
else:
    print "Config not found! Exiting!"
    sys.exit(1)

# SMT server paramters
host = cfg_dict["server"]
from_addr = cfg_dict["from_addr"]
username = cfg_dict["username"]
password = cfg_dict["password"]

# Blog and repo paramters
rootdir = cfg_dict["rootdir"]
gitreponame = cfg_dict["gitreponame"]
blogurl = cfg_dict["blogurl"]
blogtitle = cfg_dict["blogtitle"]
sysemail = cfg_dict["sysemail"]

# Set database filenames
dbghost_filename = "%s/GGprivate/ghost-backup.db" % (rootdir)
dbhash_filename = "%s/GGprivate/GGlink.db" % (rootdir)

#----------------------------------------------------------------------
# Function for sending emails from Python through a SMTP server
# Full credit for this function to Mouse vs Python blog
# http://www.blog.pythonlibrary.org/2013/06/26/python-102-how-to-send-an-email-using-smtplib-email/
# 
# hostname, from address, SMTP server username and password 
# have to specified on a separate file config.txt
#----------------------------------------------------------------------

def send_email(subject, body_text, emails):
    """
    Send an email
    """
    base_path = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_path, "../GGprivate/GGconfig.txt")

    if os.path.exists(config_path):
        cfg = ConfigObj(config_path)
        cfg_dict = cfg.dict()
    else:
        print "Config not found! Exiting!"
        sys.exit(1)

    host = cfg_dict["smtp"]["server"]
    from_addr = cfg_dict["smtp"]["from_addr"]
    username = cfg_dict["credentials"]["username"]
    password = cfg_dict["credentials"]["password"]

    BODY = string.join((
            "From: %s" % from_addr,
            "To: %s" % ', '.join(emails),
            "Subject: %s" % subject ,
            "",
            body_text
            ), "\r\n")
    server = smtplib.SMTP(host)
    server.starttls()
    server.login(username,password)
    server.sendmail(from_addr, emails, BODY)
    server.quit()
#----------------------------------------------------------------------
# SMTP test
# if __name__ == "__main__":
#    emails = ["TEST EMAIL ADDRESS 1]", "TEST EMAIL ADDRESS 2"]
#    subject = "Test email from Python"
#    body_text = "Python rules them all!"
#    send_email(subject, body_text, emails)
#----------------------------------------------------------------------

git = sh.git.bake(_cwd=gitreponame)

with sqlite3.connect(dbghost_filename) as ghostdb:
    gdbcursor = ghostdb.cursor()
    
    gdbcursor.execute("""
    select id, title, slug, author_id, markdown, status from posts
    """)

    for row in gdbcursor.fetchall():
        id, title, slug, author_id, markdown, status = row
        h = hashlib.sha1(markdown.encode('utf-8')).hexdigest()
        with sqlite3.connect(dbhash_filename) as hashdb:
            hdbcursor = hashdb.cursor()
            sqlquery = "select hid, hslug, hash from hashes where hid = %i" % (id)
            hdbcursor.execute(sqlquery)
            ###############################################################
            # Here's a first check 
            # if the post is a new one it should first be added to GGhash.db
            # the corresponding md file created
            # and addded to git
            # print git.add('somefile')
            ################################################################
            
            if hdbcursor.fetchone() is None:
                print "New post"
                sqlquery = "INSERT INTO hashes(hid,hslug,hash,hstatus) VALUES(%i,'%s','%s','draft');" % (id,slug,h)
                #print sqlquery
                hdbcursor.execute(sqlquery)
                filename = "%s/%s.md" % (gitreponame,slug)
                file = codecs.open(filename, "w", "utf-8") 
                file.write(markdown) 
                file.close()
                sqlquery = "select email, name from users where id = %i" % (author_id)
                gdbcursor.execute(sqlquery)
                for row in gdbcursor.fetchall():
                    email, name = row
                    emails = [ email, sysemail ]
                    #print emails
                    subject = "New draft on %s" % (blogtitle)
                    body_text = """
 The new draft post <<%s>> has been added on %s
 Edit it after login at %s/ghost/signin
                    """ % (title,blogtitle,blogurl)
                    send_email(subject, body_text, emails)
                gitmodfile = "%s.md" % (slug)
                print git.add(gitmodfile)
                commit_message = "New post: %s" % (title)
                print git.commit(m=commit_message)
            else:
                sqlquery = "select hid, hslug, hash, hstatus from hashes where hid = %i" % (id)
                hdbcursor.execute(sqlquery)
                for row in hdbcursor.fetchall():
                    hid, hslug, hash, hstatus = row
                    #print hash, h
                    if  h == hash:
                        #print "No changes in %s" % (title)
                        if hstatus == "draft" and status == "published":
                            subject = "A new post has been published"
                            sqlquery = "UPDATE hashes SET hstatus='%s' WHERE hid=%i;" % (status,id)
                            hdbcursor.execute(sqlquery)
                            sqlquery = "select email, name from users where id = %i" % (author_id)
                            gdbcursor.execute(sqlquery)
                            for row in gdbcursor.fetchall():
                                email, name = row
                                emails = [ email, sysemail ]
                                #print emails
                                body_text = """
 The post <<%s>> has been published on %s
 Check it out at %s/%s
                                """ % (title,blogtitle,blogurl,slug)
                                send_email(subject, body_text, emails)                             
                        elif hstatus == "published" and status == "draft":
                            subject = "Published post has been reverted to draft"
                            sqlquery = "UPDATE hashes SET hstatus='%s' WHERE hid=%i;" % (status,id)
                            hdbcursor.execute(sqlquery)
                            sqlquery = "select email, name from users where id = %i" % (author_id)
                            gdbcursor.execute(sqlquery)
                            for row in gdbcursor.fetchall():
                                email, name = row
                                emails = [ email, systemail ]
                                body_text = """
 The post <<%s>> has been reverted to draft on %s
 Edit it after login at %s/ghost/signin
                                """ % (title,blogtitle,blogurl)
                                send_email(subject, body_text, emails)        
                    else:
                        print "Changes detected in %s" % (title)
                        sqlquery = "UPDATE hashes SET hash='%s' WHERE hid=%i;" % (h,id)
                        #print sqlquery
                        hdbcursor.execute(sqlquery)
                        filename = "%s/%s.md" % (gitreponame,slug)
                        file = codecs.open(filename, "w", "utf-8") 
                        file.write(markdown) 
                        file.close()
                        gitmodfile = "%s.md" % (slug)
                        print git.add(gitmodfile)
                        commit_message = "Updated post: %s" % (title)
                        print git.commit(m=commit_message)
                    
        hashdb.close()    

ghostdb.close()


