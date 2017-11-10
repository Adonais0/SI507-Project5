## import statements
import requests_oauthlib
import webbrowser
import json
import secret_data
from datetime import datetime
from bs4 import BeautifulSoup

## CACHING SETUP
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
DEBUG = True
CACHE_FNAME = "cache_contents.json"

CREDS_CACHE_FILE = "creds.json"
CREDS_FNAME = "creds_contents.json"

CLIENT_KEY = secret_data.client_key
CLIENT_SECRET = secret_data.client_secret

REQUEST_TOKEN_URL = 'https://www.tumblr.com/oauth/request_token'
BASE_AUTH_URL = 'https://www.tumblr.com/oauth/authorize'
ACCESS_TOKEN_URL = 'https://www.tumblr.com/oauth/access_token'
#check client_key and secret
if not CLIENT_KEY or not CLIENT_SECRET:
	print("You need to fill in client_key and client_secret")
	exit()

#--------------------------------
# Load cache files: data and credentials
#--------------------------------
# Load data cache, create CACHE_DICTION
try:
    f = open('cache_contents.json')
    text = f.read()
    CACHE_DICTION = json.loads(text)#turn text into python object
except:
    CACHE_DICTION = {}# if failed in openning and reading file, diction is empty

#loads creds cache
try:
    with open(CREDS_CACHE_FILE,'r') as creds_file:
        cache_creds = creds_file.read()
        CREDS_DICTION = json.loads(cache_creds)
except:
    CREDS_DICTION = {}
#Cache functions
def has_cache_expired(timestamp_str,expire_in_days):#check if cache timestamp is over expeire times
    now = datetime.now()#current time
    cache_timestamp = datetime.strptime(timestamp_str,DATETIME_FORMAT)#formatted timestamp
    delta = now - cache_timestamp
    delta_in_days = delta.days #delta is a datetime object, and dalta_in_days is an integer

    #decide if cache is expired
    if delta_in_days > expire_in_days :
        return True
    else:
        return False#used in get_from_cache

def get_from_cache(identifier,dictionary):
    if identifier in dictionary:#dictionary of dictionary
        data_assoc_dict = dictionary[identifier]
        if has_cache_expired(data_assoc_dict['timestamp'],data_assoc_dict['expire_in_days']):
            if DEBUG:
                print("Cache has expired for {}".format(identifier))
            #remove old copy
            del dictionary[identifier]
            data = None
        else:
            data = dictionary[identifier]['values']
    else:
        data = None #Identifier not in dictionary
    return data #return data from dictionary['identifier']['values']

def set_in_data_cache(identifier, data, expire_in_days):
    identifier = identifier.upper()
    CACHE_DICTION[identifier]={
        'values':data,
        'timestamp':datetime.now().strftime(DATETIME_FORMAT),#strftime turns datetime object into strings
        'expire_in_days':expire_in_days
    }
    with open(CACHE_FNAME,'w') as cache_file:
        cache_json = json.dumps(CACHE_DICTION)#turn CACHE_DICTION into json file
        cache_file.write(cache_json)

def set_in_creds_cache(identifier, data, expire_in_days):
    identifier = identifier.upper()
    CREDS_DICTION[identifier]={
        'values':data,
        'timestamp':datetime.now().strftime(DATETIME_FORMAT),#strftime turns datetime object into strings
        'expire_in_days':expire_in_days
    }
    with open(CREDS_FNAME,'w') as cache_file:
        cache_json = json.dumps(CREDS_DICTION)#turn CACHE_DICTION into json file
        print(CREDS_DICTION)
        cache_file.write(cache_json)

## ADDITIONAL CODE for program should go here...
## Perhaps authentication setup, functions to get and process data, a class definition... etc.

#get credentials from twitter 获取api证书
def get_tokens(client_key = CLIENT_KEY, client_secret = CLIENT_SECRET, request_token_url = REQUEST_TOKEN_URL, base_authorization_url = BASE_AUTH_URL, access_token_url = ACCESS_TOKEN_URL, verifier_auto = True):
    oauth_inst = requests_oauthlib.OAuth1Session(client_key,client_secret = client_secret)#oauth instance
    fetch_owner_key = oauth_inst.fetch_request_token(request_token_url)#returns a dictionary contains request token
    resource_owner_key = fetch_owner_key.get('oauth_token')
    resource_owner_secret = fetch_owner_key.get('oauth_token_secret')
    auth_url = oauth_inst.authorization_url(base_authorization_url)#add all the information to the authorization_url

    webbrowser.open(auth_url)
    #let the user to input the url and subtract the credentials
    redirect_result = input("Paste the full redirect URL here: ")
    oauth_resp = oauth_inst.parse_authorization_response(redirect_result)#the dictionary of the result of user's authorization
    verifier = oauth_resp.get('oauth_verifier')#get the verifier
    #Regenerate the oauth instance to get the access token
    oauth_inst = requests_oauthlib.OAuth1Session(client_key,client_secret = client_secret, resource_owner_key = resource_owner_key, resource_owner_secret = resource_owner_secret, verifier = verifier)
    fetch_owner_key = oauth_inst.fetch_access_token(access_token_url)

    resource_owner_key = fetch_owner_key.get('oauth_token')
    resource_owner_secret = fetch_owner_key.get('oauth_token_secret')
    return client_key, client_secret, resource_owner_key, resource_owner_secret, verifier

def get_tokens_from_service(service_name_ident, expire_in_days=7): # Default: 7 days for creds expiration
    creds_data = get_from_cache(service_name_ident, CREDS_DICTION)
    if creds_data:
        if DEBUG:
            print("Loading creds from cache...")
            print()
    else:
        if DEBUG:
            print("Fetching fresh credentials...")
            print("Prepare to log in via browser.")
            print()
        creds_data = get_tokens()
        # print(creds_data)#successfully get data
        set_in_creds_cache(service_name_ident, creds_data, expire_in_days=expire_in_days)
    return creds_data

def create_request_identifier(url, params_diction):
    sorted_params = sorted(params_diction.items(),key=lambda x:x[0])
    params_str = "_".join([str(e) for l in sorted_params for e in l]) # Make the list of tuples into a flat list using a complex list comprehension
    total_ident = url + "?" + params_str
    return total_ident.upper() # Creating the identifier

def get_posts_list(my_params,blogid,service_ident,expire_in_days=7):#use service_ident to search for service credentials in creds cache
    url = 'https://api.tumblr.com/v2/blog/{}.tumblr.com/posts'.format(blogid)
    ident = create_request_identifier(url, my_params)
    data = get_from_cache(ident,CACHE_DICTION)
    print(bool(data))
    if data:
        if DEBUG:
            print("Loading from data cache: {}... data".format(ident))
    else:
        if DEBUG:
            print("Fetching new data from {}".format(url))
        # Get credentials
        client_key, client_secret, resource_owner_key, resource_owner_secret, verifier = get_tokens_from_service(service_ident)
        oauth = requests_oauthlib.OAuth1Session(client_key,
        	client_secret = client_secret,
        	resource_owner_key = resource_owner_key,
        	resource_owner_secret = resource_owner_secret)
        r = oauth.get(url,params = my_params)
        resps_dict= r.json()
        dict_list = []
        for post in resps_dict['response']['posts']:
            post_dict = {}
            post_dict['title'] = post['slug']
            post_dict['summary'] = post['summary']
            post_dict['tags'] = post['tags']
            post_dict['date'] = post['date']
            post_dict['short_url'] = post['short_url']
            dict_list.append(post_dict)
        data = dict_list
        set_in_data_cache(ident, data, expire_in_days)
    return data
# ?? if I'm just fetching blogs posted by users, is there any need to use oauth anymore?

def collect_posts(blogid):
    outfile = open('{}.csv'.format(blogid),'w')
    outfile.write("Title, Summary, Tags, Date, URL\n")
    for i in range(5):
        my_params = {'limit':20,'offset':i}
        dict_list = get_posts_list(my_params,blogid,"Tumblr")
        for dic in dict_list:
            outfile.write('"{}","{}","{}","{}","{}"\n'.format(dic['title'],dic['summary'],dic['tags'],dic['date'],dic['short_url']))
# write_csv('alldesignprocess')
collect_posts('uxdesignresource')
collect_posts('uxdesignprocess-blog')
collect_posts('alldesignprocess')
## Make sure to run your code and write CSV files by the end of the program.
