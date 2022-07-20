from typing import Dict, Optional, List
import jwt
#from datetime import datetime, timedelta
import time
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.requests import Request
from starlette.status import HTTP_403_FORBIDDEN
from src.core.config import settings
from src.core.schema import PassportVisaToken

class HTTPBearerToken(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> dict:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        
        if credentials:
            if credentials.scheme.lower() != "bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            token_data = self.verify_jwt_token(credentials.credentials)
            return token_data
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    def verify_jwt_token(self, jwtoken: str) -> dict:
        try:
            options={"verify_signature": False}
            decoded_token = jwt.decode(
                jwtoken, 
                settings.passport_secret_key, 
                algorithms=[settings.passport_algorithm],
                options=options
            )
            print(decoded_token)
            #if decoded_token["expires"] <= time.time():
            #    raise HTTPException(status_code=403, detail="token expired.")
            return decoded_token
        except Exception as e:
            print(e)
            raise HTTPException(status_code=403, detail="Invalid token")

async def authorize_bearer_token(
    token_data  = Depends(HTTPBearerToken())
) -> PassportVisaToken:
    try:
        return PassportVisaToken(**token_data)
    except Exception:
        HTTPException(status_code=HTTP_403_FORBIDDEN, detail="invalid claims")
