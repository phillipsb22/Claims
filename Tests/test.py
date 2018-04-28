import sys
import requests
import os.path

if len(sys.argv) != 4:
    print("Please supply google access token, host url http://xxxx.xx.xx:xxxx/ and image to upload location")
    quit()

access_token = sys.argv[1]
host_url = sys.argv[2]
file_path = sys.argv[3]
header = {'Authorization' : access_token}

#check file exists
try:
    file = open(file_path,'rb')
except:
    print("file does not exist")
    quit()

#################################################################
# test request without access tokengetter
#################################################################
full_url = host_url + 'UserClaim'
request = requests.get(full_url)
if request.status_code == 200:
    print("Test without access token failed")
else:
    print("Test without access token Passed")
#################################################################

#################################################################
#add user claims with no data
#################################################################
request = requests.post(full_url, headers = header)
try:
    if request.status_code != 200:
        print("Add claim no data success")
    else:
        print("add user claim no data request failed")
except:
    print("add user claim no data request failed")
#################################################################

#################################################################
#add user claims with data
#################################################################
file_data = {'file': open(file_path, 'rb')}
amount_data = {'amount' : '1234.00'}
request = requests.post(full_url, headers = header, files = file_data, data = amount_data)
try:
    if request.status_code == 200:
        print("Add claim success")
    else:
        print("add user claim request failed")
except:
    print("add user claim request failed")
#################################################################

#################################################################
# list user claims
#################################################################
request = requests.get(full_url, headers = header)
try:
    if request.status_code == 200:
        jo = request.json()
        claim_id = jo['claims'][0]['id']
    else:
        print("List user claim request failed")
except:
    print("List user claim request exception thrown")
#################################################################

#################################################################
#user add claim conversation no data
#################################################################
full_url = host_url + 'claimconversations'
request = requests.post(full_url, headers = header)
try:
    if request.status_code != 200:
        print("Add conversation with claim no data: passed")
    else:
        print("Add conversation with claim request: failed")
except:
    print("Add conversation with claim request: exception")
#################################################################

#################################################################
#user add claim conversation with data
#################################################################
full_url = host_url + 'claimconversations'
request_data = {'message' : 'Test message', 'claim_id' : claim_id}
request = requests.post(full_url, headers = header, data = request_data)
try:
    if request.status_code == 200:
        print("Add conversation with claim with data: passed")
    else:
        print("Add conversation with claim with data request: failed")
except:
    print("Add conversation with claim request with data: exception")
#################################################################

#################################################################
#admin retrieve Claims
#################################################################
full_url = host_url + 'AdminClaim'
request = requests.get(full_url, headers = header)
try:
    if request.status_code == 200:
        jo = request.json()
        claim_id = jo['claims'][0]['id']
        print("Admin get unprocessed claims: passed")
    else:
        print("Admin get unprocessed claims: failed")
except:
    print("Admin get unprocessed claims: exception")
#################################################################

#################################################################
#admin authorise claims
#################################################################
full_url = host_url + 'AdminClaim'
post_data = {'claim_id' : claim_id}
request = requests.post(full_url, headers = header, data = post_data)
try:
    if request.status_code == 200:
        print("Admin process claim: passed")
    else:
        print("Admin process claim: failed")
except:
    print("Admin process claim: exception")
#################################################################

#################################################################
#admin get claim conversation list all new
#################################################################
full_url = host_url + 'adminConversations'
request = requests.get(full_url, headers = header)
try:
    if request.status_code == 200:
        jo = request.json()
        get_conv_for_user = jo['users'][0]['user_id']
        print("admin list conversation with user with data: passed")
    else:
        print("admin list conversation with user with data: failed")
except:
    print("admin list conversation with user with data: exception")

#################################################################

#################################################################
#admin get claim conversation list for a user
#################################################################
full_url = host_url + 'adminConversations?user_id=' + str(get_conv_for_user)
request = requests.get(full_url, headers = header)
try:
    if request.status_code == 200:
        jo = request.json()
        claim_id = jo['user_messages'][0]['claim_id']
        print("admin get claim conversation list for a user: passed")
    else:
        print("admin get claim conversation list for a user: failed")
except:
    print("admin get claim conversation list for a user: exception")
#################################################################

#################################################################
#admin reply to conversation
#################################################################
full_url = host_url + 'adminConversations'
request_data = {'user_id' : get_conv_for_user, 'message' : 'Test reply message from admin', 'claim_id' : claim_id}
request = requests.post(full_url, headers = header, data = request_data)
try:
    if request.status_code == 200:
        print("admin reply to a user: passed")
    else:
        print("admin reply to a user: failed")
except:
    print("admin reply to a user: exception")
#################################################################

#################################################################
#user reply to conversation
#we will use the same claim id that the admin just replied to
#################################################################
full_url = host_url + 'claimconversations'
request_data = {'message' : 'Test reply message from user', 'claim_id' : claim_id}
request = requests.put(full_url, headers = header, data = request_data)
try:
    if request.status_code == 200:
        print("user reply to admin: passed")
    else:
        print("user reply to admin: failed")
except:
    print("user reply to admin: exception")
#################################################################
