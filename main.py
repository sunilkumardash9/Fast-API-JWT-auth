from fastapi import FastAPI, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, HTTPBearer
from auth_handler import encode_jwt, decode_jwt

from passlib.context import CryptContext

from datamodels import user_schema, UserLoginSchema, post_schema
from database import engine, Base, user_details, user_blogs, SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy import select

Base.metadata.create_all(engine)

app = FastAPI()


users = dict()

crypto_context = CryptContext(schemes="bcrypt")
Oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/posts/token')

def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def get_user(userid:str, session: Session = Depends(get_session)):
    session = Session(bind = engine, expire_on_commit=False)
    
    stmt = select(user_details).where(user_details.email == userid)
    result = session.execute(stmt)
    obj = list(result)[0].user_details
    return user_schema(**{'fullname':obj.name,'email':obj.email, 'password':obj.password_hashed})

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not crypto_context.verify(password, user.password):
        return False
    return user

async def current_user(token: str = Depends(Oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    decoded_token = decode_jwt(token)
    if not decoded_token:
        raise credentials_exception
    
    user = get_user(decoded_token['user'])
    
    return user



@app.get('/')
def welcome():
    return "FastAPI JWT (JSON Web Token) Authentication"


@app.get("/posts/me", dependencies=[Depends(current_user)], tags=['posts'])
async def see_posts(user: user_schema = Depends(current_user)):
    session = Session(bind = engine, expire_on_commit=False)
    
    stmt = select(user_blogs).where(user_blogs.user_email == user.email)
    result = session.execute(stmt)
    post_list = []
    for row in result:
        post_dict = {'title':row.user_blogs.title,'body':row.user_blogs.body}

        post_list.append(post_dict)
    
    return post_list
        


@app.post("/posts", dependencies=[Depends(current_user)] ,tags=['posts'],status_code=status.HTTP_201_CREATED)
async def write_post(post:post_schema, session : Session = Depends(get_session), user : user_schema = Depends(current_user)):

    post = user_blogs(id=post.id, user_email= user.email, title = post.title, body = post.body)
    session.add(post)
    session.commit()

    return "post added"

@app.get('/users', tags=['User'])
async def users_in_db(session: Session = Depends(get_session)):
    
    users = session.query(user_details).all()
    user_list = []
    for user in users:
    
        data = {'user':user.email, 'name':user.name, 'password':user.password_hashed}

        user_list.append(data)

    return user_list


@app.post("/posts/sign_up", tags=['User'], status_code=status.HTTP_201_CREATED)
async def user_signUp(user: user_schema, session : Session = Depends(get_session)):
    user.password = crypto_context.hash(user.password)
    user_val = user_details(email=user.email, name = user.fullname, password_hashed = user.password)

    session.add(user_val)
    session.commit()
    
    return f"Mr/Mrs {user.fullname} welcome!"

        
@app.post("/posts/token", tags=['User'])
async def user_login(user_details: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(user_details.username, user_details.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    else:
        access_token = encode_jwt(user.email)
        return {"access_token": access_token, "token_type": "bearer"}

