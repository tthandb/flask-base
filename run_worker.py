import click
import os
import multiprocessing as mp
import traceback
import faktory
import uuid
from common.errors import UBadRequest
from workers.example import Example
from middlewares.logger import write_log


routes = {
    'WORKER_EXAMPLE': [Example, 'run'],
}


class ExceptionProcess(mp.Process):
    def __init__(self, *args, **kwargs):
        mp.Process.__init__(self, *args, **kwargs)
        self._pconn, self._cconn = mp.Pipe()
        self._exception = None

    def run(self):
        try:
            mp.Process.run(self)
            self._cconn.send(None)
        except Exception as e:
            tb = traceback.format_exc()
            self._cconn.send((e, tb))

    @property
    def exception(self):
        if self._pconn.poll():
            self._exception = self._pconn.recv()
        return self._exception


def detect_worker(message):
    if 'action' not in message:
        raise UBadRequest('Missing action type')
    action = message['action']
    if action not in routes:
        raise UBadRequest('Action invalid')
    process = ExceptionProcess(target=call_message, args=(message,))
    process.start()
    process.join()
    if process.exception:
        error, traceback = process.exception
        raise error
    print('DONE PROCESS')


def call_message(message):
    action = message['action']
    class_worker, method = routes[action]

    request_id = str(uuid.uuid4())
    extra_log = {
        'request_id': request_id,
        'tags': request_id,
        'environment': os.getenv('ENVIRONMENT', 'development'),
        'request_type': 'FAKTORY_WORKER',
        'action': '{}.{}'.format(class_worker.__name__, method)
    }
    write_log(
        raw_message={'params': message},
        extra=extra_log
    )
    worker_obj = class_worker()
    getattr(worker_obj, method)(message)
    write_log(
        raw_message='FINISH WORK',
        extra=extra_log
    )


def create_worker(worker_type=os.getenv('FAKTORY_QUEUE_NAME'), concurrency=1):
    environment = os.getenv('ENVIRONMENT', 'development'),
    print(os.getenv('FAKTORY_URL'))
    worker = faktory.Worker(
        faktory=os.getenv('FAKTORY_URL'),
        queues=[worker_type],
        concurrency=concurrency,
        use_threads=False
    )
    worker.register(
        worker_type,
        detect_worker
    )
    worker.run()


@click.command()
@click.option('-w', '--worker', type=str, required=True, help='Worker name')
def run_worker(worker):
    if worker == 'example':
        create_worker(worker_type='example', concurrency=5)
    else:
        create_worker()


if __name__ == '__main__':
    run_worker()
