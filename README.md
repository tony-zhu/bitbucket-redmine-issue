bitbucket-redmine-issue
=======================

Transfer bitbucket issues to redmine


BitBucket authentication
------------------------
Follow
https://confluence.atlassian.com/display/BITBUCKET/OAuth+on+Bitbucket#OAuthonBitbucket-Step1.CreateanOAuthkeyandsecret

Create a consumer key and secret pair for this script.


Redmine authentication
----------------------
Enable the API-style authentication, you have to check Enable REST API in Administration -> Settings -> Authentication.

You can find your API key on your account page ( /my/account ) when logged in, on the right-hand pane of the default layout.


Configuration
-------------
Copy the migrate.ini.example to migrate.ini and fill all the parameters.

If you do not know the Redmine project id, leave it empty and save the migrate.ini first. Then run the list_redmine_projects.py helper script to find it.

Migrate the issues
------------------
Run the migrate.py

Customization
-------------
The BitBucket issue's original reporter and comments are all complied into the description of the Redmine issue.

The original status are also mapped to the default Redmine issue status.

Customize this behavior if you want. They are all in the handle_issues function.


Problems
--------
BitBucket attachments are not being transferred yet. 
