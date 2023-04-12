from fastapi import Header
from .crud_utils import get_user
from .schema import UserBase, UserProfile

def user_from_header(x_omic_userid: str = Header(..., description="The omic user-id."),)->UserProfile:
    user_id = x_omic_userid
    user = get_user(user_id)
    user_profile = UserBase.from_orm(user).dict()
    team = user.active_team
    user_profile['team'] = team
    user_profile['workspace'] = team.workspace
    return user_profile