from fastapi import Query, HTTPException
from .crud_utils import get_user
from .schema import UserBase, UserProfile

def user_from_query(x_omic_userid: str = Query(None, description="The omic user-id."))->UserProfile:
    user_id = x_omic_userid
    if not user_id:
        raise HTTPException(status_code=500, detail="require x_omic_userid query param  ")
    user = get_user(user_id)
    user_profile = UserBase.from_orm(user).dict()
    team = user.active_team
    user_profile['team'] = team
    user_profile['workspace'] = team.workspace
    return user_profile