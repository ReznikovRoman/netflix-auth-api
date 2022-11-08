import requests
from jose import jwt

from auth.core.config import get_settings

from .exceptions import OAuthError

settings = get_settings()


def validate_token(token: str) -> dict:
    """Validate access token using auth0 service.

    Example from docs: https://auth0.com/docs/quickstart/backend/python#create-the-jwt-validation-decorator
    """
    try:
        unverified_header = jwt.get_unverified_header(token)
    except jwt.JWTError:
        raise OAuthError("Unable to parse authentication token", "invalid_header")
    if unverified_header["alg"] == "HS256":
        raise OAuthError("Invalid header. Use an RS256 signed JWT Access Token", "invalid_header")
    jwks = requests.get(f"https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json").json()
    rsa_key = {}
    for key in jwks["keys"]:
        if key["kid"] != unverified_header["kid"]:
            continue
        rsa_key = {"kty": key["kty"], "kid": key["kid"], "use": key["use"], "n": key["n"], "e": key["e"]}
    if not rsa_key:
        raise OAuthError("Unable to find appropriate key", "invalid_header")
    try:
        payload = jwt.decode(
            token=token,
            key=rsa_key,
            algorithms=settings.AUTH0_ALGORITHMS,
            audience=settings.AUTH0_API_AUDIENCE,
            issuer=settings.AUTH0_ISSUER,
        )
    except jwt.ExpiredSignatureError:
        raise OAuthError("Token is expired", "token_expired")
    except jwt.JWTClaimsError:
        raise OAuthError("Incorrect claims, please check the audience and issuer", "invalid_claims")
    except Exception:
        raise OAuthError("Unable to parse authentication token", "invalid_header")
    return payload
