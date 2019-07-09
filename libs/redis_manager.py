from decimal import Decimal

import redis

from apps import db
from apps.seckill.models import Order, Orderitem, Saleproduct
from apps.user.models import User

r = redis.Redis(port=7000)


def setcache(key, time, value):
    """
    Set the ``value``  to ``name`` that expires in ``time``
    seconds.
    """
    r.setex(key, time, value)


def getcache(key):
    """
    Return the value of ``key``, or None if the key doesn't exist
    """
    return r.get(key)


def queuesize(key):
    """
    Return the len of the list ``key`` or None if the key doesn't exist
    """
    return r.llen(key)


def setqueue(key, item):
    li = r.lpush(key, item)


# 限制一个api或页面访问的频率，例如单ip或单用户一分钟之内只能访问多少次
def check_request_limit(key, limit):
    # key = '{}'.format(key)
    check = r.exists(key)
    if check:
        r.incr(key)
        r.expire(key, 60)
        count = int(r.get(key))
        if count > limit:
            return False
        else:
            return True
    else:
        r.set(key, 1)
        # sec_redis.incr(key)
        r.expire(key, 60)
        return True


# 秒杀修改库存
def update_stock(key, productid, userid, qty, price):
    qty = int(qty)
    item = "%s-%s-%s-%s" % (userid, productid, qty, price)
    cart_key = 'cart:{}'.format(userid)
    with r.pipeline() as pipe:
        while True:
            try:
                # 关注一个key,watch 字面就是监视的意思，这里可以看做为数据库中乐观锁的概念，谁都可以读，谁都可以修改，但是修改的人必须保证自己watch的数据没有被别人修改过，否则就修改失败了；
                pipe.watch(key)
                count = int(getcache(key))  # 取库存
                if count < qty:
                    pipe.unwatch()
                    print('库存不足')
                    return False
                # 事务开始
                pipe.multi()
                remainqty = count - qty
                pipe.set(key, remainqty)  # 保存剩余库存
                pipe.sadd(cart_key, item)


                # 事务结束
                pipe.execute()

                # 把命令推送过去

            except Exception as e:
                print(e)
                pipe.unwatch()
                continue
            else:
                return True


# 取队列元素，先进先出
def popqueue(key):
    popqueue = r.rpop(key)
    # time.sleep(0.1)
    return popqueue
