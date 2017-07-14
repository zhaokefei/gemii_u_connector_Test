import multiprocessing

#errorlog = '-'
#accesslog = '-'
bind = "127.0.0.1:21123"
worker_class = 'gevent'
workers = multiprocessing.cpu_count()*2+1