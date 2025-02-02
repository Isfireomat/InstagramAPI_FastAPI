from os import environ
from app.models.schemas import Text
from fastapi import Depends, HTTPException, Response, Request, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from app.data_base.db_connect import get_session
from sqlalchemy.future import select
from sqlalchemy.dialects.postgresql import insert
from app.models.models import User, Message
from sqlalchemy.orm import aliased
from sqlalchemy import desc 
import httpx

UserSender = aliased(User)
UserRecipient = aliased(User)

INSTAGRAM_API_URL = "https://graph.instagram.com/v22.0"
ACCESS_TOKEN = environ.get("ACCESS_TOKEN")

router: APIRouter = APIRouter()

@router.get('/messages')
async def messages(request: Request, user_id: int | None = None, username: str | None = None, limit: int=10, session: AsyncSession = Depends(get_session)):
    if (not user_id and not username) or (limit<=0):
        raise HTTPException(status_code=400, detail="Bad request")
    if not user_id: 
        stmt: str = select(User).where(User.username==username)
        result = await session.execute(stmt)
        user: User = result.scalars().first()
        if user:
            user_id: int = user.id
        else:
            raise HTTPException(status_code=404, detail="Not found")
    stmt: str = select(
        UserSender.username.label('sender_username'),
        UserRecipient.username.label('recipient_username'),
        Message.text,
        Message.created_time
    ).join(UserSender, UserSender.id == Message.sender_id) \
     .join(UserRecipient, UserRecipient.id == Message.recipient_id) \
     .where(Message.sender_id == user_id)\
     .distinct()\
     .order_by(desc(Message.created_time))\
     .limit(limit)
    result = await session.execute(stmt)
    messages: list = result.fetchall()
    return [f'{message[0]} -> {message[1]}: {message[2]}' for message in messages], 200
    
    
@router.get('/user')
async def messages(request: Request, user_id: int | None = None, username: str | None = None, session: AsyncSession = Depends(get_session)):
    if not user_id and not username:
        raise HTTPException(status_code=400, detail="Bad request")
    if user_id:
        stmt: str = select(User).where(User.id==user_id)
    elif username:
        stmt: str = select(User).where(User.username==username)
    else:
        raise HTTPException(status_code=404, detail="Not found")
    result = await session.execute(stmt)
    user: User = result.scalars().first()
    print(user)
    query_params: dict = {
        'fields': 'id,username,name',
        'access_token': ACCESS_TOKEN
    }
    url: str = f"{INSTAGRAM_API_URL}/{user.id}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url=url, params=query_params, timeout=60.0)
    return response.json(), 200
    
@router.get("/webhook")
async def verify_webhook(request: Request):
    query_params = request.query_params
    if query_params.get("hub.mode") == "subscribe" and query_params.get("hub.verify_token") == environ.get("VERIFY_TOKEN"):
        return Response(content=query_params.get("hub.challenge"))
    return "Verification failed", 400

@router.post('/webhook')
async def messages(request: Request, session: AsyncSession = Depends(get_session)):
    data: dict = await request.json()
    message: dict = data['entry'][0]['messaging'][0]
    text: str = message['message']['text']
    mid: str = message['message']['mid']
    url: str = f"{INSTAGRAM_API_URL}/{mid}"
    query_params: dict = {
        'fields': 'from,to',
        'access_token': ACCESS_TOKEN
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url=url, params=query_params, timeout=60.0)
        data: dict = response.json()
        sender_id: str = data['from']['id']
        sender_name: str = data['from']['username']
        recipient_id: str = data['to']['data'][0]['id']
        recipient_name: str = data['to']['data'][0]['username']
        stmt: str = insert(User).values(id=int(sender_id), username=sender_name)
        stmt: str = stmt.on_conflict_do_update(
            index_elements=['id'],  
            set_=dict(username=sender_name) 
        )
        await session.execute(stmt)
        stmt: str = insert(User).values(id=int(recipient_id), username=recipient_name)
        stmt: str = stmt.on_conflict_do_update(
            index_elements=['id'],  
            set_=dict(username=recipient_name) 
        )
        await session.execute(stmt)
        stmt: str = insert(Message).values(sender_id=int(sender_id), recipient_id=int(recipient_id), text=text)
        await session.execute(stmt)  
        await session.execute(stmt)
    
@router.post('/messages/send')
async def messages(request: Request, user_id: int, text: Text):
    url: str = f"{INSTAGRAM_API_URL}/me/messages"
    headers: dict = {
        'Authorization': f'Bearer {ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    body: dict = {
        "recipient":{
            "id": f"{user_id}"
        },
        "message":{
            "text": text.text
        }
    }
    async with httpx.AsyncClient() as client:
        await client.post(url=url, headers=headers, json=body, timeout=60.0)
    return {'Send': 'successful'}, 200
