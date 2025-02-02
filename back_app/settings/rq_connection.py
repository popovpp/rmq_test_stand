import time
from redis import Redis
from rq import Queue, Retry
from rq.command import send_kill_horse_command, send_shutdown_command
from rq.worker import Worker, WorkerStatus

from back_app.settings.settings import REDIS_HOST, REDIS_PORT, REDIS_DB


zero_retry = Retry(max=1)

redis = Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB
)

worker_3 = Worker(['q3',], connection=redis, name='w3')
worker_4 = Worker(['q4',], connection=redis, name='w4')
worker_5 = Worker(['q5',], connection=redis, name='w5')

rq_conn_3 = Queue('q3', connection=redis)
rq_conn_4 = Queue('q4', connection=redis)
rq_conn_5 = Queue('q5', connection=redis)


def kill_all_rqworkers():
    workers = Worker.all(redis)
    while workers:
        for worker in workers:
            send_shutdown_command(redis, worker.name)
            send_kill_horse_command(redis, worker.name)
        time.sleep(1)
        workers = Worker.all(redis)
    print(Worker.all(redis))
    print('############################################')
