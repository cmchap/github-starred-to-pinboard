Github Starred Repos to Pinboard Bookmarks
==========================================

It turns recently starred repos from a Github account into bookmarks in Pinboard.

It makes the bookmark like this:

![example bookmark](https://raw.github.com/cmchap/github-starred-to-pinboard/master/screenshot.png)

That is, it sets the bookmark title to the repo name followed by the short, one-liner repo description. It lists the languages used in the repo in order of bytes, too. Just for you. Because I like you. It also lists the beginnings of the readme file.

Usage
-----

Get your Github OAuth token from [here](https://github.com/settings/applications).

Get your Pinboard API token from [here](https://pinboard.in/settings/password).

If you already have some of these repos bookmarked, this script will not replace them. If you wish to change this, set the ```replace``` variable to "yes"

The bookmarks will be tagged with the terms in the ```tags``` variable.

Run the script and follow the directions.


Requirements
------------

python 2.6 - 2.7.5

[Requests](http://docs.python-requests.org/en/latest/)

Limitations
-----------

<del>It only works for the 100 most recently starred repos.</del> It works for any number of repos. Thanks, [jdherg](https://github.com/jdherg)!

API calls are limited to 4103 characters which really cuts down on how much of the readme file is included in the description.

TODO
----

* <del>Make it work for folks who have more than 100 starred repos.</del>
* Make it fail more gracefully
	* Pinboard rate limit failure (once every 3 seconds)
	* Github rate limit failure (60 per hour unauthenticated <del> or 5000 authenticated</del>). The authenticated limit isn't a problem because the pinboard rate limit is already significantly lower: 3/second, or 1200/hour
* Add an option to replace existing bookmarks with the original datetime
* check to ensure the entered github username exists.