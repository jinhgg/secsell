import redis
from threading import Thread

# 初始化 redis
r = redis.Redis()

KEY = "count"  # 库存 key


def sell(i):
    '''
    售卖方法
    param: i 用户
    '''
    with r.pipeline() as pipe:  # 初始化 pipe
        while 1:
            try:
                pipe.watch(KEY)  # 监听库存
                c = int(pipe.get(KEY))  # 查看当前库存
                if c > 0:  # 有库存则售卖
                    pipe.multi()  # 开始事务
                    print('减少之前:', c)
                    # pipe.decr(KEY)
                    c -= 1
                    pipe.set(KEY, c)  # 减少库存
                    print('看看现在减少了没有：', c)
                    pipe.execute()  # 执行事务
                    # 抢购成功并结束
                    print('用户 {} 抢购成功，商品剩余 {}'.format(i, c))
                    break
                else:
                    # 库存卖完，抢购结束
                    print('用户 {} 抢购停止，商品卖完'.format(i))
                    break
            except Exception as e:
                # 抢购失败，重试
                print('用户 {} 抢购失败，重试一次'.format(i))
                continue
            finally:
                # 重置 pipe，准备下次抢购
                pipe.reset()


if __name__ == "__main__":
    r.set(KEY, 10)  # 初始化 10 个库存
    for i in range(15):  # 共 15 个人开始抢购
        t = Thread(target=sell, args=(i,))
        t.start()
