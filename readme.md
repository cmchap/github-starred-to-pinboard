Github Starred Repos to Pinboard Bookmarks
==========================================

It adds the first 100 starred repos from a Github account into bookmarks in Pinboard.

It makes the bookmark like this:
![example bookmark](https://dl.dropbox.com/s/n3tpzmlo8k13fxd/example.png)

That is, it sets the bookmark title to the repo name followed by the short, one-liner repo description. It fleshes out the description with pertinent info. It even lists the languages used in the repo in order of bytes. Just for you. Because I like you.

Usage
-----

Get your Github OAuth token from [here](https://github.com/settings/applications).

Get your Pinboard API token from [here](https://pinboard.in/settings/password).

run the script and follow the directions.


Requirements
------------
[Requests](http://docs.python-requests.org/en/latest/)

Limitations
-----------
* Requires python 2.6 - 2.7.5
* It only works for 100 starred repos.

TODO
----
* Make it work for folks who have more than 100 starred repos. (github api)
* Make it fail more gracefully
	* Pinboard rate limit failure (once every 3 seconds)
	* Github rate limit failure (60 per hour unauthenticated or 5000 authenticated)