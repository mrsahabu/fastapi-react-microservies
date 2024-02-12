from fastapi import FastAPI
from fastapi.background import BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from redis_om import get_redis_connection, HashModel

import requests
import time

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

@app.get('/orders/{pk}')
def get(pk: str):
    order = Order.get(pk)
    redis.xadd('refund_order', order.dict(), '*')
    return order

@app.post('/orders')
async def create(request: Request, background_task: BackgroundTasks):
    body = await request.json()
    req = requests.get('http://localhost:8000/products/%s' % body['product_id'])
    product = req.json()

    order = Order(
        product_id= product['pk'],
        price= product['price'],
        fee= 0.2 * product['price'],
        total= 1.2 * product['price'],
        ordered_quantity=product['quantity'],
        status= 'pending'
    )
    
    order.save()
    background_task.add_task(order_completed, order)
    return order
    
def order_completed(order: Order):
    time.sleep(5)
    order.status = 'completed'
    order.save()
    redis.xadd('order_completed', order.dict(), '*')

    