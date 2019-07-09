import os
import multiprocessing

# debug = True
loglevel = 'debug'
bind = "0.0.0.0:8000"
pidfile = None
accesslog = "./access.log"
errorlog = "./error.log"
daemon=True                                                                                                                                                                                                       

# 启动的进程数
workers = multiprocessing.cpu_count()
# worker_class = 'gevent'
x_forwarded_for_header = 'X-FORWARDED-FOR'
