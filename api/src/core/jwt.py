#import requests
import jwt
from datetime import datetime, timedelta
from jwt import PyJWKClient
from .config import settings

issuer = f'https://cognito-idp.{settings.user_pool_region}.amazonaws.com/{settings.user_pool_id}'
keys_url = f'{issuer}/.well-known/jwks.json'

jwks_client = PyJWKClient(keys_url)

def decode_cognito_token(jwt_token: str) -> dict:
    try:
        signing_key = jwks_client.get_signing_key_from_jwt(jwt_token)
        claims = jwt.decode(
            jwt_token, 
            signing_key.key,
            algorithms=["RS256"],
            audience=settings.user_pool_client_id, 
            options={"verify_exp": False},
        )
        print(claims)
    except Exception as e:
        return None, e.__str__()
    return claims, None

def encode_passport_token(claims: dict) -> str:
    to_encode = claims.copy()
    expires_delta = settings.passport_token_expire_mins
    expire = datetime.utcnow() + timedelta(minutes=expires_delta)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.passport_secret_key, 
        algorithm=settings.passport_algorithm
    )
    return encoded_jwt