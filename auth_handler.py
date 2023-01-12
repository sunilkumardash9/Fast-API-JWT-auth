from jose import jwt, JWTError, ExpiredSignatureError
from decouple import config
import time
from fastapi import HTTPException


jwt_token = config('secret')
algorithm = config('algorithm')



def encode_jwt(email:str):

    payload = {'user':email, 'expires':time.time()+180}

    encoded_payload = jwt.encode(payload, key = jwt_token, algorithm=algorithm)

    return encoded_payload

def decode_jwt(token:str):
    timeout = ExpiredSignatureError()
    try:
        decoded_token = jwt.decode(token, key=jwt_token, algorithms = algorithm)
        
        if decoded_token["expires"] >= time.time():
            return decoded_token 
        else:
            raise timeout

    except:
        raise HTTPException(status_code=400, detail="inactive user")
