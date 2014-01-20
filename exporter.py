# Requires python 2.6 - 2.7.5

# Copyright Cory Chapman, 2013

# Distributed under the WTF Public License (www.wtfpl.net)

##############
## Settings ##
##############

replace = "no" #change to "yes" if you want it to replace previously bookmarked repos
tags = "github programming github-starred-to-pinboard" #max of 100 tags, separated by spaces

###############
## Functions ##
###############

import requests, time, sys, re, base64, urllib

def post_to_pinboard(pb_token, url, title, long_description, tags, replace, name, length=4103):
    payload = [
        ('auth_token', pb_token),
        ('url', url),
        ('description', title),
        ('tags', tags),
        ('replace', replace),
        ('extended', long_description)
    ]
    r = requests.get('https://api.pinboard.in/v1/posts/add', params=payload)
    r_status = r.status_code
    if r_status == 200:
        print "Added " + name
        return 1
    elif r_status == 403:
        print "Your Pinboard token didn't seem to work.\nYou should go get it from here: https://pinboard.in/settings/password"
        print "And paste it below.\nIt should look sorta like this: username:XXXXXXXXXXXXXXXXXXXX"
        pb_token = raw_input()
        return post_to_pinboard(pb_token, url, title, long_description, tags, replace, name)
    elif r_status == 429:
        print "Whoa, Nellie! We're goin' too fast! Hold on, and we'll try again in a moment."
        time.sleep(3) # Pinboard API allows for 1 call every 3 seconds per user.
        return post_to_pinboard(pb_token, url, title, long_description, tags, replace, name)
    elif r_status == 414:
        print "The api request for " + name + " was " + str(len(r.url)-length) + " characters too long."
        print "Shortening..."
        shortened_description = truncate_long_description(r.url, length, long_description)
        return post_to_pinboard(pb_token, url, title, shortened_description, tags, replace, name)
    else:
        print "Something went wrong while trying to bookmark " + title + ". I don't know what, but the http status code was " + str(r_status)
        return 0

def get_langs(langs_url, gh_token):
    langs = ""
    lang_data = requests.get("%s?access_token=%s" % (langs_url, gh_token))
    if lang_data == "{}":
        return langs
    else:
        lang_data = lang_data.json()
        langs_sorted = sorted(lang_data.iteritems(), key=lambda bytes: -bytes[1]) #sort the languages into a list by most bytes.
        for x in langs_sorted:
            langs += "%s = %s bytes\n" % (x[0], x[1])
        return langs

def get_readme(api_url, gh_token):
#def get_readme(gh_username, name):
    r = requests.get(api_url + "/readme?access_token=" + gh_token)
    readme_b64 = r.json()['content']
    readme = base64.b64decode(readme_b64)
    #readme = readme.encode(encoding='ascii', errors='ignore')
    #r = requests.get("https://raw.github.com/" + gh_username + "/" + name + "/master/readme.md")
    if 300 > r.status_code >=200:
        # print r.content
        # return r.content
        #print readme
        return readme
    else:
        return "none listed"

def test_token(url, token):
    auth = {'auth_token': token}
    r = requests.get(url, params=auth)
    if r.status_code == 403:
        return 0
    else:
        return 1

def smart_truncate(content, length, suffix):
    if len(content) <= length:
        return content
    else:
        return content[:length+1-len(suffix)].rsplit(' ',1)[0] + suffix

def truncate_long_description(url, length, description):
    if len(url) <= length:
        return description
    else:
        length = length-3 #take into account adding the ellipsis.
        new_url = url[0:length]
        new_url = re.sub(r'\+[^\+]*$', "...", new_url) # puts an ellipsis after the last word that will fit within the length requirement
        new_long_description = re.sub(r'^.*extended=', "", new_url) #Gets the url-encoded long description
        new_long_description = urllib.unquote_plus(new_long_description.encode('ascii')) #hopefully puts the url into utf-8 without the url encoding.
        return new_long_description

##############
## Get info ##
##############

#Github
print "Enter a Github username to get their starred repos:"
gh_username = raw_input()
print "Now go to https://github.com/settings/applications, and create a new token, and paste it here."
gh_token = raw_input()
url = 'https://api.github.com/users/' + gh_username + '/starred?page=1&per_page=100' # Fetches 100 starred repos per page

#Test Github token
token_tests = 3
while test_token(url, gh_token) == 0:
    if token_tests > 0:
        token_tests  = token_tests - 1
        print "Your Github token didn't seem to work. Can you try entering it in again?"
        gh_token = raw_input()
    else:
        print "It seems like your token isn't working.\nYou can try running this script again, but the Github API may be down."
        sys.exit()

r = requests.get(url + "&access_token=" + gh_token)
stars = r.json()
while r.links: # iterate through the pages of github starred repos
    if 'next' in r.links:
        url = r.links['next']['url']
        r = requests.get(url + "&access_token=" + gh_token)
        stars.extend(r.json())
    else:
        break

#Pinboard
print "Enter your Pinboard api token in the form username:XXXXXXXXXXXXXXXXXXXX\nYou can get it from here: https://pinboard.in/settings/password"
pb_token = raw_input()

#Test Pinboard token
token_tests = 3
while test_token(url, pb_token) == 0:
    if token_tests > 0:
        token_tests  = token_tests - 1
        print "Your Pinboard API token didn't seem to work. Can you try entering it in again?"
        gh_token = raw_input()
    else:
        print "It seems like your token isn't working.\nYou can try running this script again, but the Pinboard API may be down."
        sys.exit()


###############
## Main loop ##
###############

print "Adding your starred repos to Pinboard..."

count = 0
for item in range(len(stars)):
    repo_url = stars[item]['html_url']
    name = stars[item]['name']
    tagline = stars[item]['description']
    repo_api_url = stars[item]['url']

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
    langs = get_langs(langs_url, gh_token) + "\n\n"

    #Make readme
    readme = get_readme(gh_username, name)

    #Make the description.
    long_description = "Github repo \nName: " + name
    long_description += "\nTagline: " + tagline
    if homepage != "none listed":
        long_description += "\nHomepage: " + homepage
    if langs != []:
        long_description += "\nLanguages:\n" + langs
    if readme != "none listed":
        long_description = long_description.encode(encoding='UTF-8', errors='ignore')
        long_description += readme

    #test string lengths.
    #Max description =  65536 characters according to the docs.
    #in reality, the entire get cannot be longer than 4103 characters
    long_description = smart_truncate(long_description, 65536, '...')
    # max title is 255
    title = smart_truncate(title, 255, '...')

    pinboard_add = post_to_pinboard(pb_token, repo_url, title, long_description, tags, replace, name)
    if pinboard_add == 1:
        count +=1
if count == 0:
    print "Whoopsh. Something went wrong, so we didn't add anything to your Pinboard."
elif count == 1:
    print "You're all done. You only had one starred repo, so we added that to Pinboard. Go star more repos!"
elif count > 1:
    print "You're all done. All " + str(count) + " repos above have been added to pinboard!"