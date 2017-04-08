# Ghost2Git — Version control and editorial workflow management for multi-author blogs in Ghost, sort of

Ghost offer a great platform for blogging. It's nimble and neat, a welcome break from WordPress especially if what you want to do is focus on blogging and content and you do not need a general purpose CMS. 

Ghost does blogging very well, but it does not do everything. And that's a good thing. For example, Ghost does not do comments—arguably a very important component of a blog—but this function is outsourced to external specialised services like Disqus that can easily be integrated with Ghost. 

Another function that Ghost does not offer is version control for posts. And for multi-author blogs, it does not provide editorial flow management tools. Again, I think that it is a good thing that Ghost focuses on what it does best. And if you really need these functions, perhaps it is better to develop them outside Ghost. And this project is about offering a first tentative solution to this problem. 

## Why did I neeed version control and editorial workflow management in Ghost?

As that editor of a multi-author, blog https://security-praxis.eu  While authorship is individual (or shared with co-authors), posts are read and commented about by fellow authors and the editors before publication. When we started the blog three years ago and we had to make technical choices, we looked for a blogging platform that at the same time offered some editorial workflow management tools and that at the same time could accommodate the eventual growth of the blog into a full-fledged peer reviewd scientific journal. This overlapping requirement had lead us to opt for a technical solution based on  [Annotum](https://annotum.org), a WordPress theme that allowed for relatively sophisticated editorial workflow management, while complying with the JATS standards for online scientific publications. Plus WP's user friendliness and it's vast ecosystem of plugins. Three years later the blog-journal superposition of states has eventually resolved and Security Praxis is going to be a beautiful blog, perhaps associated with, but definitely not a peer-reviewed journal. This internal evolution was combined with Annotum end of development in November 2016, that did not allow it to run on more recent WP versions with all the security vulnerabilities that this lack of updates entailed. 

## Migrating the blog from WP+Annotum to Ghost

I had followed the story of Ghost development in the technical press and so when it came to move out of a blog-cum-scientific journal to a blog tout court, I decided to switch to Ghost. I have recently supervised the migration of the blog from WordPress+Annotum to Ghost and I'm very happy about the new platform. Still, there are a few functions that are missing: Zotero indexation; version control; editorial flow management; co-authored articles. The first one requires the blog to expose metadata so that [Zotero](https://zotero.org) (a free citation management and bibliography tool with a vast user base among scholars) browser extensions can index them correctly, and was [easily solved](https://www.ragazziconsulting.com/?p=592). 

## Version control

In Ghost architecture blog posts are stored as strings in the SQLite database (table: "posts") in both markdown and html formats. When user drafts a post using the internal editor and saves it, the markdown is updated in the database, while the system automatically generates the html. Upon saving it, the previous version of the post is overwritten and lost. Some users have already [flagged the issue](http://ideas.ghost.org/forums/285309-wishlist/suggestions/11668422-post-revisions), also [here](https://trello.com/c/1wAHv8jZ/34-post-revisions), but to my knowledge there are no extant solutions.

Starting from the assumption that we do not want to modify Ghost itself, and mimicking the way Ghost deals with—rather, how it doesn't—comments, we should look for an external version control service provider and find some way to make it talk to Ghost. Git does this job very well. It is probably an overkill compared with the version control needs of a blog, but it is there, it is tried and tested, well documented, offers ample room for growth of the complexity of a collaborative editorial workflow and, last but not least, it's popularity is growing also among social scientists or at least non-code-developer sorts that nevertheless work and breath by textual material. 

How to connect Ghost and Git? Two aproaches come to mind. The first is writing a [Ghost "app"](https://github.com/TryGhost/Ghost-App), an existing (e.g. there is an app to connect Ghost with Slack) and expanding construct. In this case a hypothetical Ghost-to-Git app (briefly, GG) would do as follows: 

1 — When a user edits and saves a post, GG makes an automatic commit on a designated local git repository on the server. If git is already installed on the server hosting Ghost, this should be achieved with a rather simple script.  

2 — In order for the users to browse the versions and compare differences, in keeping with the no-modifications-to-Ghost approach, they will have to resort to a separate tool. That is, the past versions and differences are not visible within Ghost web interface itself. If the server hosting Ghost does not have a publicly accessible git repo, perhaps is better to push the local repo to a remote one on, say, GitLab that offers free private repositories (assuming that only the final version of a post should be publicly accessible via the blog itself, and not the previous versions).  

3 — If there are more users interacting on the same post draft, they can take advantage of git tools for forking, diffing, merging, accepting a pull request etc. Or even if a single author wants to track back and return to a previous version.

4 — Eventually the GG app, this time from within Ghost web interface, will "sync" the changes on the git repo with the database. This is the perhaps the tricky part. This could be done automatically or perhaps more wisely, the app may signal first to the user that there is a change in the git repo and ask for confirmation about synchronising it with the database. If the user accepts, the app fetches the current version from the git repo, locks the database, copies the new markdown and triggers the internal Ghost "update post" function. The app may

Since the development of a Ghost "app" exceeds my skills, what I'm proposing here is a simpler solution that does 1+2+3 above at a lower, server side level, without touching Ghost, not even by adding an app. It is also unidirectional: posts can be modified only within the Ghost editor, and subsequent versions are stored on the git repo. But potential edits of the files stored in the git repo cannot be reflected in the Ghost database. 

The proposed partial solution for 1+2+3 is implemented with a Python script called by a shell script run periodically as a cronjob. 

— As a preliminary step creates an auxiliary SQLite database.
— If the Ghost database has been modified since the previous run of the script, rsync the Ghost database to a local copy to avoid database lock reading errors (even if the Ghost database is never written onto); otherwise there is nothing to do.
— Extract all posts (markdown field) and calculate their hashes (or just compare the date of each post's last modification).
— For each post compare the hash with the previous one, stored in the auxiliary database.
— If the post is a new one, create a markdown file in the repo and commit. 
— If the post has been modified, update the markdown file in the repo and commit. 

## Editorial workflow management  

The functions associated with the management of the editorial workflow are still in the earliest stages of developemnt. To start with, Ghost itself has very little to offer. At the moment, there are three user profiles in Ghost: author, editor, administrator. Each author in principle can draft and publish a post whithout a green light from the editors. There is a feature request pending in Ghost and its developers announced that in the future versions they will introduce a fourth "contributor" profile that will be able to draft but not to publish a post. In a collective, peer-reviewed blog like ours, it is up to each author self-discipline to remember to save a draft post and then notify the editors that there is a new post waiting for their care, comments and eventual publication. 

If not a real editoral workflow management, the Python script introduces a barebone editorial signalling, sending an email to the author and editor whenever a new post is drafted, published, updated or for some reasons reverted to draft state afterwards.   

## No co-authoring

Where both Ghost and this script fall short is in allowing for multi-author posts, such that co-authors can appear in the post byline and the like. For the time being, if there are more than author, we will have to list the co-authors manually at the beginning of the article.

## Auxiliary database 

The auxiliary SQLite database named GGlink.db in this solution has the following structure:

Table: hashes

Fields: 
    hid (INTEGER)
    hslug (TEXT)
    hash (TEXT)
    status (TEXT)
    
A handy tool to edit SQLite database is a graphical environment is http://sqlitebrowser.org


