from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from redis_om import get_redis_connection, HashModel

import requests

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=['*'],
    allow_headers=['*']
)

#this should be different db
#just for learning purpose
redis = get_redis_connection(
    host='redis-11677.c305.ap-south-1-1.ec2.cloud.redislabs.com',
    port=11677,
    password='Hkr76nAxKCkwUcYofsoVf5HrvO3YjjiV',
    decode_responses=True
)

class Order(HashModel):
    product_id: str
    price: float
    fee: float
    total: float
    ordered_quantity: int
    status: str #pending/completed/refunded
    
    class Meta:
        database = redis

@app.post('/orders')
async def create(request: Request):
    body = await request.json()
    
    req = requests.get('http://localhost:8000/products/%s' % body['product_id'])
    return req.json()
    
    
    