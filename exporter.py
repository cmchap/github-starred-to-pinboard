# Requires python 2.6 - 2.7.5

# Copyright Cory Chapman, 2013

# Distributed under the WTF Public License (www.wtfpl.net)

##############
## Settings ##
##############

replace = "no" #change to "yes" if you want it to replace previously bookmarked repos
tags = "github programming" #max of 100 tags, separated by spaces

###############
## Functions ##
###############


import json, requests, time

def postToPinboard(pb_token, url, title, long_description, tags, replace):

    payload = {
        'auth_token': pb_token,
        'url': url,
        'description': title,
        'extended': long_description,
        'tags': tags,
        'replace': replace
    }
    r = requests.get('https://api.pinboard.in/v1/posts/add', params=payload)
    rStatus = r.status_code
    if rStatus == 200:
    	print "Added " + title
    	return 1
    elif rStatus == 403:
    	print "Your token didn't seem to work. It should look sorta like this: username:XXXXXXXXXXXXXXXXXXXX"
    	return 0
    elif rStatus == 429:
    	print "Whoa, Nellie! We're goin' too fast! Hold on, and we'll try again in a moment."
    	time.sleep(3) # Pinboard API mandates 1 call every 3 seconds per user.
    	postToPinboard(pb_token, url, title, long_description, tags)
    	return 1
    elif rStatus != 200 and rStatus != 403 and rStatus != 429:
    	print "Something went wrong. I don't know what, but the http status code was " + rStatus
    	return 0

def getLangs(langs_url, gh_token):
	langs = ""
	l = requests.get("%s?access_token=%s" % (langs_url, gh_token))
	if l == "{}":
		return langs
	else:
		l = json.loads(l.text)
		langs_sorted = sorted(l.iteritems(), key=lambda bytes: -bytes[1]) #sort the languages into a list by most bytes.
		for x in langs_sorted:
		 	langs += "%s = %s bytes\n" % (x[0], x[1])
		return langs


##############
## Get info ##
##############
#
print "Enter a Github username to get their starred repos:"
gh_username = raw_input()
print "Now go to https://github.com/settings/applications, and create a new token, and paste it here."
gh_token = raw_input()
url = 'https://api.github.com/users/' + gh_username + '/starred?page=1&per_page=100' # Only works on the first 100 starred repos.
r = requests.get(url + "&access_token=" + gh_token)
stars = json.loads(r.content)
print "Enter your Pinboard api token in the form username:XXXXXXXXXXXXXXXXXXXX\nYou can get it from here: https://pinboard.in/settings/password"
pb_token = raw_input()

###############
## Main loop ##
###############

print "Adding your starred repos to Pinboard..."

count = 0
for item in range(len(stars)):
	url = stars[item]['html_url']
	name = stars[item]['name']
	tagline = stars[item]['description']

	#make title
	title = name + ": " + tagline #max 255 characters according to the pinboard api.

	# See if the homepage is listed.
	page = stars[item]['homepage']
	if page == False or page == None or page == "None" or page == "none" or page == "":
		homepage = "none listed"
	else:
		homepage = str(page)

	#Make the programming languages of the repo in order of most bytes.
	langs_url = stars[item]['languages_url']
	langs = getLangs(langs_url, gh_token)

	#Make the description
	long_description = "This is a github repo. \nName: " + name
	long_description += "\nTagline: " + tagline
	if homepage != "none listed":
	    long_description += "\nHomepage: " + homepage
	if langs != []:
	    long_description+= "\nLanguages:\n" + langs #max 65536 characters according to pinboard api.

	pAdd = postToPinboard(pb_token, url, title, long_description, tags, replace)
	if pAdd == 1:
		count +=1
print "You're all done. All " + str(count) + " repos above have been added to pinboard!"