# Requires python 2.6 - 2.7.5

# Copyright Cory Chapman, 2013

# Distributed under the WTF Public License (www.wtfpl.net)

##############
## Settings ##
##############

replace = "no" #change to "yes" if you want it to replace previously bookmarked repos
tags = "github programming github-starred-to-pinboard" #max of 100 tags, separated by spaces

# Uncomment these lines and fill them in with your info if you don't want to create a config file.
# gh_username = "username"
# gh_token = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
# pb_token = "username:XXXXXXXXXXXXXXXXXXXX"

###############
## Functions ##
###############

import requests, time, sys, re, base64, urllib, ConfigParser, os

def post_to_pinboard(pb_token, url, title, long_description, tags, replace, name, length=4103, sleep=3):
    time.sleep(3) # Pinboard API allows for 1 call every 3 seconds per user
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
        time.sleep(sleep) # Pinboard API allows for 1 call every 3 seconds per user, so we're doubling the wait for each attempt per the docs.
        sleep = sleep*2
        return post_to_pinboard(pb_token, url, title, long_description, tags, replace, name, length, sleep)
    elif r_status == 414:
        print "The api request for " + name + " was " + str(len(r.url)-length) + " characters too long."
        print "Shortening..."
        shortened_description = truncate_long_description(r.url, length, long_description)
        return post_to_pinboard(pb_token, url, title, shortened_description, tags, replace, name)
    else:
        print "Something went wrong while trying to bookmark " + name + ". I don't know what, but the http status code was " + str(r_status)
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
    r = requests.get(api_url + "/readme?access_token=" + gh_token)
    if r.status_code == 200:
        readme_b64 = r.json()['content']
        readme = base64.b64decode(readme_b64)
        return str(readme)
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

def get_github_username(sleep=1):
    if not parser.has_section('github'):
        parser.add_section('github')

    if not parser.has_option('github', 'username'):
        print "Enter a Github username to get their starred repos:"
        gh_username = raw_input()
    else:
        gh_username = parser.get('github', 'username')

    test_url = 'http://github.com/' + gh_username
    if 200 <= requests.get(test_url).status_code < 299:
        parser.set('github', 'username', gh_username)
    else:
        time.sleep(sleep)
        sleep = sleep*2
        print "Your Github token didn't seem to work."
        get_github_username(sleep)

    with open(config_file, 'wb') as configfile:
        parser.write(configfile)
    return gh_username

def get_github_token(gh_username, sleep=1):
    if not parser.has_section('github'):
        parser.add_section('github')

    if not parser.has_option('github', 'token'):
        print "Go to https://github.com/settings/applications, and create a new token, and paste it here."
        gh_token = raw_input()
    else:
        gh_token = parser.get('github', 'token')

    test_url = 'https://api.github.com/users/' + gh_username + '/starred?page=1&per_page=100' # Fetches 100 starred repos per page
    if test_token(test_url, gh_token) == 0:
        time.sleep(sleep)
        sleep = sleep*2
        print "Your Github token didn't seem to work."
        get_pinboard_token(gh_username, sleep)
    else:
        parser.set('github', 'token', gh_token)
        with open(config_file, 'wb') as configfile:
            parser.write(configfile)
        return gh_token

def get_pinboard_token(sleep=1):
    if not parser.has_section('pinboard'):
        parser.add_section('pinboard')

    if not parser.has_option('pinboard', 'token'):
        print "Enter your Pinboard api token in the form username:XXXXXXXXXXXXXXXXXXXX\nYou can get it from here: https://pinboard.in/settings/password"
        pb_token = raw_input()
    else:
        pb_token = parser.get('pinboard', 'token')

    test_url = 'https://api.pinboard.in/v1/posts/recent?count=1'
    if test_token(test_url, pb_token) == 0:
        time.sleep(sleep)
        sleep = sleep*2
        print "Your Pinboard API token didn't seem to work."
        get_pinboard_token(sleep)
    else:
        parser.set('pinboard', 'token', pb_token)
        with open(config_file, 'wb') as configfile:
            parser.write(configfile)
        return pb_token


def get_current_from_pinboard(pb_token, tags):
    payload = {
    'auth_token': pb_token,
    'tag': tags,
    'format': 'json'
    }
    r = requests.get('https://api.pinboard.in/v1/posts/all', params=payload)
    if r.status_code == 200:
        bookmarks = r.json()
        return bookmarks
    else:
        print "Something went wrong while trying to get bookmarks. The status code was " + str(r.status_code)
        sys.exit()

##############
## Get info ##
##############

# defines the config file as having the same filename as this script with an extension of .config
config_file = os.path.splitext(__file__)[0] + ".config"
parser = ConfigParser.SafeConfigParser()
if os.path.exists(config_file):
    parser.read(config_file)

try
    gh_username
except
    gh_username = get_github_username()

try
    gh_token
except
    gh_token = get_github_token(gh_username)

try
    pb_token
except
    pb_token = get_pinboard_token()


###############
## Main loop ##
###############


# get existing bookmarks from pinboard
existing = {}
for bookmark in get_current_from_pinboard(pb_token, tags):
    existing[bookmark['href']] = True
print str(len(existing)) + " existing bookmarks found"


# get stars from github
url = 'https://api.github.com/users/' + gh_username + '/starred?page=1&per_page=100'

r = requests.get(url + "&access_token=" + gh_token)
stars = r.json()
while r.links: # iterate through the pages of github starred repos
    if 'next' in r.links:
        url = r.links['next']['url']
        r = requests.get(url + "&access_token=" + gh_token)
        stars.extend(r.json())
    else:
        break

print "Adding your starred repos to Pinboard..."

count = 0
for star in stars:
    repo_url = star['html_url']
    if repo_url == False or repo_url == None or repo_url == "None" or repo_url == "none" or repo_url == "" or repo_url == "null":
        repo_url == ""
    name = star['name']
    if name == False or name == None or name == "None" or name == "none" or name == "" or name == "null":
        name = ""

    # Skip existing starred repos
    if replace == "no":
        if repo_url in existing:
            print "Skipping " + name
            print repo_url
            continue # breaks out of the for loop that iterates through the stars.

    tagline = star['description']
    if tagline == False or tagline == None or tagline == "None" or tagline == "none" or tagline == "" or tagline == "null":
        tagline = ""
    repo_api_url = star['url']
    if repo_api_url == False or repo_api_url == None or repo_api_url == "None" or repo_api_url == "none" or repo_api_url == "" or repo_api_url == "null":
        repo_api_url = ""

    #make title
    if tagline == "":
        title = name
    else:
        title = name + ": " + tagline #max 255 characters according to the pinboard api.

    # See if the homepage is listed.
    page = star['homepage']
    if page == False or page == None or page == "None" or page == "none" or page == "" or page == "null":
        homepage = "none listed"
    else:
        homepage = str(page)

    #Make the programming languages of the repo in order of most bytes.
    langs_url = star['languages_url']
    langs = get_langs(langs_url, gh_token) + "\n\n"

    #Make readme
    readme = get_readme(repo_api_url, gh_token)

    #Make the description.
    long_description = "Github repo \nName: " + name
    long_description += "\nTagline: " + tagline
    if homepage != "none listed":
        long_description += "\nHomepage: " + homepage
    if langs != []:
        long_description += "\nLanguages:\n" + langs
    if readme != "none listed":
        long_description = long_description.encode('UTF-8','ignore')
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
    print "You're all done. " + str(count) + " repos have been added to pinboard!"