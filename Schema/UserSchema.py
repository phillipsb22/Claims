from Misc.Schema import ma
from Models.User import User

class UserSchema(ma.Schema):
        fields = ('name', 'email' ,'token', 'admin', 'admin')
