from flask import Flask, url_for, jsonify, request, session
from flask_restplus import Api, Resource,abort
import os
from werkzeug import secure_filename
import requests
import json
import re
from flask_oauthlib.client import OAuth
from Misc.database import db
from Schema.UserSchema import UserSchema
from Schema.ClaimSchema import ClaimSchema, ClaimConversationsSchema
from Misc.validators import validate_token, allowed_file

from Models.User import User
from Models.Claim import Claim, ClaimConversations

GOOGLE_CLIENT_ID = 'xxxxxxxxxxxxxxxxxxxxm'
GOOGLE_CLIENT_SECRET = 'xxxxxxxxxxxxxxxxxxxxxx'
SECRET_KEY = 'xxxxxxxxxxxxxxx'
UPLOAD_FOLDER = "xxxxxxxxxxxxxxxxxx"

app = Flask(__name__)
api = Api(app)

#put this into a config
app.secret_key = SECRET_KEY
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
oauth = OAuth(app)

google = oauth.remote_app(
    'google',
    consumer_key=GOOGLE_CLIENT_ID,
    consumer_secret=GOOGLE_CLIENT_SECRET,
    request_token_params={'scope': 'https://www.googleapis.com/auth/userinfo.email'},
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

@app.route('/login', methods = ['GET'])
def login():
    #used to login
    callback='http://localhost:5000/oauth2callback'
    return google.authorize(callback=callback)

@app.route('/oauth2callback', methods = ['GET'])
def oauth2callback():
    resp = google.authorized_response()
    if resp is None:
        return redirect('/login')

    access_token = resp['access_token']
    session['access_token'] = access_token, ''

    #get info from here https://www.googleapis.com/oauth2/v1/userinfo?alt=json&access_token=youraccess_token
    url = 'https://www.googleapis.com/userinfo/v2/me'
    me = google.get(url, data=None, headers=None, format='urlencoded', content_type='json', token=None)
    print(me.data['email'])
    print(me.data)

    user_exists = User.query.filter_by(email = me.data['email']).first()
    if user_exists is None:
        new_user = User(email = me.data['email'], name = me.data['name'], token = access_token)
        db.add(new_user)
        db.commit()

        #check if its the first user if so make it an admin user
        if new_user.id == 1:
            new_user.admin = 1
            db.commit()

    else:
        user = User.query.filter_by(email = me.data['email']).first()
        user_id = user.id
        #update the token
        user.token = access_token
        db.commit()

    return jsonify({"access_token":access_token})

@google.tokengetter
def get_access_token():
    return session.get('access_token')

@api.route('/UserClaim')
class UserClaim(Resource):
    def get(self):
        #used to get user claims
        if request.headers.get('Authorization') is None:
            abort(400, "Token Invalid")

        valid = validate_token(request.headers["Authorization"]) or None
        if valid == None:
            # return {"staus" : "failed", "message" : "Please login again"}
            abort(400, "Please sign in again")
        else:
            user = User.query.filter_by(email = valid).first()
            user_id = user.id

        user_claims = Claim.query.filter_by(user_id = user_id)
        claim_data = ClaimSchema(many = True)
        output = claim_data.dump(user_claims).data

        return {'claims' : output}

    def post(self):
        #used to create user claims
        if request.headers.get('Authorization') is None:
            abort(400, "Token Invalid")

        valid = validate_token(request.headers["Authorization"]) or None
        if valid == None:
            # return {"staus" : "failed", "message" : "Please login again"}
            abort(400, "Please sign in again")
        else:
            user = User.query.filter_by(email = valid).first()
            user_id = str(user.id)

        try:
            uploaded_file = request.files['file']
        except:
            abort(400, "Please supply a file and amount")

        amount = request.form.get('amount')
        if amount is None:
            abort(400, "Please supply a file and amount")

        # check that amount is in cents
        p = re.compile('[0-9]+.[0-9]{2}')
        if p.match(amount) is None:
            abort(400, "Please supply the amount in full Rand value(xxx.xx) or cents value(xxxxxxxxx)")
        else:
            amount = re.sub('\.', '', amount)

        #check the file ext
        if uploaded_file and allowed_file(uploaded_file.filename):
            filename = secure_filename(uploaded_file.filename)
            #check file name is unique
            user_path = app.config['UPLOAD_FOLDER'] + user_id
            full_path = user_path + "/" +  filename
            exists = Claim.query.filter_by(file_loc = full_path).first()
            if exists is None:
                if not os.path.exists(user_path):
                    os.makedirs(user_path)

                uploaded_file.save(full_path)
            else:
                abort(400, "You already have a file by that name. Please rename and upload again")
        else:
            api.abort(400, "Please upload a valid image. Accepted types are pdf, png, jpg, jpeg, gif")

        #insert claim into the database
        new_claim = Claim(file_loc = full_path, amount = int(amount), status_id = "Pending", user_id = int(user_id))
        db.add(new_claim)
        db.commit()

        return {"message": "Claim submit successful", "filename" : filename}

@api.route('/claimconversations')
class UserClaimConversations(Resource):
    def get(self):
        #gets all conversations for user for a claim
        if request.headers.get('Authorization') is None:
            abort(400, "Token Invalid")

        valid = validate_token(request.headers["Authorization"]) or None
        if valid == None:
            # return {"staus" : "failed", "message" : "Please login again"}
            abort(400, "Please sign in again")
        else:
            user = User.query.filter_by(email = valid).first()
            user_id = str(user.id)

        claim_id = request.args.get('claim_id') or None
        if claim_id is None:
            abort(400, "Please supply a valid claim id")

        conversations = ClaimConversations.query.filter_by(claim_id = claim_id, user_id = user_id)

        if conversations.first() is None:
            abort(400, "No  claim matching these parameters")

        from Schema.ClaimSchema import ClaimConversationsSchema

        conv_schema = ClaimConversationsSchema()
        convs_schema = ClaimConversationsSchema(many = True)
        print(conversations.count())

        if conversations.count() == 1:
            output = conv_schema.dump(conversations).data
        else:
            output = convs_schema.dump(conversations).data

        return {'conversations' : output}

    def post(self):
        #used to follow up on a claim
        if request.headers.get('Authorization') is None:
            abort(400, "Token Invalid")

        valid = validate_token(request.headers["Authorization"]) or None
        if valid == None:
            # return {"staus" : "failed", "message" : "Please login again"}
            abort(400, "Please sign in again")
        else:
            user = User.query.filter_by(email = valid).first()
            user_id = str(user.id)

        message = request.form.get('message') or None
        claim_id = request.form.get('claim_id') or None
        if message is None or claim_id is None:
            abort(400, "Please supply a valid message or claim id")

        #check claim id exists and belongs to this users
        exists = Claim.query.filter_by(user_id = user_id, id = claim_id).first()
        if exists is None:
            abort(400, "No claim matching those parameters")

        if re.search('^[\w\s]+$',message) is None:
            abort(400, "Please only use alphanumeric characters A-Z, a-z 0-9 underscore and spaces")

        #in a live system I would link status to another table
        new_conversation = ClaimConversations(claim_id = claim_id, message = message, user_id = user_id, status = 'new conversation')
        db.add(new_conversation)
        db.commit()

        return {"message": "message successfully sent"}

    def update(self):
        # used to reply to message
        if request.headers.get('Authorization') is None:
            abort(400, "Token Invalid")

        valid = validate_token(request.headers["Authorization"]) or None
        if valid == None:
            # return {"staus" : "failed", "message" : "Please login again"}
            abort(400, "Please sign in again")
        else:
            user = User.query.filter_by(email = valid).first()
            user_id = str(user.id)

        message = request.form.get('message') or None
        claim_id = request.form.get('claim_id') or None

        if message is None or claim_id is None:
            abort(400, "Please supply a valid message or claim id")

        #check claim id exists and belongs to this users
        exists = Claim.query.filter_by(user_id = user_id, id = claim_id).first()
        if exists is None:
            abort(400, "No claim matching those parameters")

        if re.search('^[\w\s]+$',message) is None:
            abort(400, "Please only use alphanumeric characters A-Z, a-z 0-9 underscore and spaces")

        #in a live system I would link status to another table
        reply_conversation = ClaimConversations(claim_id = claim_id, message = message, user_id = user_id, status = 'reply')
        db.add(new_conversation)
        db.commit()

        return {"message": "message successfully sent"}

@api.route('/AdminClaim')
class AdminClaim(Resource):
    def get(self):
        # used to retrieve claims
        if request.headers.get('Authorization') is None:
            abort(400, "Token Invalid")

        valid = validate_token(request.headers["Authorization"]) or None
        if valid == None:
            # return {"staus" : "failed", "message" : "Please login again"}
            abort(400, "Please sign in again")
        else:
            user = User.query.filter_by(email = valid).first()
            user_id = str(user.id)

        #first check  if the user is an admin
        admin = User.query.filter_by(id = user_id).first()
        if admin.admin == 0:
            abort(400, "Access Denied")

        claims = Claim.query.filter_by(status_id = "Pending")

        from Schema.ClaimSchema import ClaimSchema
        claim_sch = ClaimSchema(many = True)

        output = claim_sch.dump(claims).data

        return {'claims' : output}

    def post(self):
        #used to process claim
        if request.headers.get('Authorization') is None:
            abort(400, "Token Invalid")

        valid = validate_token(request.headers["Authorization"]) or None
        if valid == None:
            # return {"staus" : "failed", "message" : "Please login again"}
            abort(400, "Please sign in again")
        else:
            user = User.query.filter_by(email = valid).first()
            user_id = str(user.id)

        admin = User.query.filter_by(id = user_id).first()
        if admin.admin == 0:
            abort(400, "Access Denied")

        #pass in the claim id to know what claim was processed
        claim_id = request.form.get('claim_id') or None
        if claim_id is None:
            abort(400, "Please supply a valid claim identifier")

        #here we would say claim was paid to wallet or in cash to person

        paid = Claim.query.filter_by(id = claim_id).first()
        paid.status_id = 'Processed'
        db.commit()

        return {'message' : 'Claim Processed successfully'}

@api.route('/adminConversations')
class AdminConversations(Resource):
    def get(self):
        #used to get all the conversations
        if request.headers.get('Authorization') is None:
            abort(400, "Token Invalid")

        valid = validate_token(request.headers["Authorization"]) or None
        if valid == None:
            abort(400, "Please sign in again")
        else:
            user = User.query.filter_by(email = valid).first()
        user_id = str(user.id)

        admin = User.query.filter_by(id = user_id).first()
        if admin.admin == 0:
            abort(400, "Access Denied")

        from Schema.ClaimSchema import ClaimConversationsSchema

        if request.args.get('user_id') is None:
            #return the users
            user_schema = ClaimConversationsSchema(many = True, only = ('user_id','message'))
            users = ClaimConversations.query.group_by('user_id').order_by('id DESC')
            output = user_schema.dump(users).data

            return {'users' : output}

        else:
            #return conversations for that user for
            conv_user = request.args.get('user_id')
            user_schema = ClaimConversationsSchema(many = True, only = ('message','claim_id'))
            conversations = ClaimConversations.query.filter_by(user_id = conv_user).order_by('id ASC')
            output = user_schema.dump(conversations).data

            return {'user messages' : output}

    def post(self):
        #used to reply to follow up
        if request.headers.get('Authorization') is None:
            abort(400, "Token Invalid")

        valid = validate_token(request.headers["Authorization"]) or None
        if valid == None:
            abort(400, "Please sign in again")
        else:
            user = User.query.filter_by(email = valid).first()
        user_id = str(user.id)

        admin = User.query.filter_by(id = user_id).first()
        if admin.admin == 0:
            abort(400, "Access Denied")

        #check passed in the user id they are replying to
        reply_to_user = request.form.get('user_id') or None
        message = request.form.get('message') or None
        claim_id = request.form.get('claim_id') or None
        if reply_to_user is None or message is None or claim_id is None:
            abort(400, 'Please supply message, user id or claim id you are replying to')

        #check message for special characters
        if re.search('^[\w\s]+$',message) is None:
            abort(400, "Please only use alphanumeric characters A-Z, a-z 0-9 underscore and spaces")

        #insert reply
        message = ClaimConversations(user_id = reply_to_user, message = message, status = 'Admin Reply', claim_id = claim_id)
        db.add(message)
        db.commit()

        return {'message' : 'Message successfully sent'}

# if time add class to manage user and admin accounts

if __name__ == '__main__':
    app.run(host = "0.0.0.0", port = 5000, debug=True)
