from Misc.Schema import ma
from Models.Claim import Claim, ClaimConversations

class ClaimSchema(ma.Schema):
    class Meta:
        fields = ('id', 'amount', 'status_id', 'user_id')

class ClaimConversationsSchema(ma.Schema):
    class Meta:
        fields = ('claim_id' ,'message', 'user_id','id')

# class ClaimConversationsUserSchema(ma.Schema):
#     class Meta:
#         fields = ('id','user_id')
