from main import redis, Order

import time

key = 'refund_order'
group = 'payment_group'

try:
    redis.xgroup_create(key, group)
except Exception as e:
    print('Group already exists.')


while True:
    try:
        results = redis.xreadgroup(group, key, {key: '>'}, None)
        if results != []:
            for result in results:
                obj = result[1][0][1]
                order = Order.get(obj['product_id'])
                order.status = 'refund'      
                order.save()  
    except Exception as e:
        print(str(e))
    time.sleep(1)