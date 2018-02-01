Github Starred Repos to Pinboard Bookmarks
==========================================

It turns recently starred repos from a Github account into bookmarks in Pinboard.

It makes the bookmark like this:

![example bookmark](https://raw.github.com/cmchap/github-starred-to-pinboard/master/screenshot.png)

That is, it sets the bookmark title to the repo name followed by the short, one-liner repo description. It lists the languages used in the repo in order of bytes, too. Just for you. Because I like you. It also lists the as much of the readme file as will fit in Pinboard's description field. 

Usage
-----

Get your Github OAuth token from [here](https://github.com/settings/applications).

Get your Pinboard API token from [here](https://pinboard.in/settings/password).

By default, if you have an existing bookmark with the same URl as a starred repo, this script will change that bookmark to match the above styling. If you wish to change this, set the ```replace``` variable to ```no```. Note that even if ```replace``` is ```yes```, the datetime on existing bookmarks will not be altered by this script.

The bookmarks will be tagged with the terms in the ```tags``` variable.

On first run, it creates a config file with the same base filename as you named this script. (If you didn't rename the script, it'll be called ```exporter.config```)
You can uncomment and fill in ```gh_username```, ```gh_token```, and ```pb_token``` if you do not want to create a config file. 

Otherwise, run the script and follow the directions.


Requirements
------------

python 2.6 - 2.7.5

[Requests](http://docs.python-requests.org/en/latest/)

Limitations
-----------

<del>It only works for the 100 most recently starred repos.</del> It works for any number of repos. Thanks, [jdherg](https://github.com/jdherg)!

API calls are limited to 4103 characters which really cuts down on how much of the readme file is included in the description. If anybody has a good workaround for this, please submit a pull request. 

TODO
----

* <del>Make it work for folks who have more than 100 starred repos.</del> done.
* Make it fail more gracefully
	* <del>Pinboard rate limit failure (once every 3 seconds)<del> done. 
	* Github rate limit failure (60 per hour unauthenticated <del> or 5000 authenticated</del>). The authenticated limit isn't a problem because the pinboard rate limit is already significantly lower: 3/second, or 1200/hour
	* <del>Add an option to replace existing bookmarks with the original datetime</del> done.
* Check to ensure the entered github username exists.

LICENSE
----

This project is licensed under the terms of the MIT license.
