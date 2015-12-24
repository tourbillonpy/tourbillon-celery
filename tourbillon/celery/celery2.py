import logging
import time

from celery import Celery
from celery.events import EventReceiver

logger = logging.getLogger(__name__)


class TourbillonReceiver(EventReceiver):

    def __init__(self, stop_event, *args, **kwargs):
        super(TourbillonReceiver, self).__init__(*args, **kwargs)
        self.stop_event = stop_event

    @property
    def should_stop(self):
        logger.debug('should stop checked')
        return not self.stop_event.is_set()


def get_celery_stats(agent):
    agent.run_event.wait()
    config = agent.config['celery']
    db_config = config['database']
    agent.create_database(**db_config)

    app = Celery(broker=config['broker'])
    state = app.events.State()

    def handle_event(event):
        try:
            state.event(event)
            if event['type'] == 'worker-heartbeat':
                return handle_worker_event(event)
            return handle_task_event(event)
        except:
            logger.exception('cannot handle celery event')

    def handle_task_event(event):
        try:
            logger.debug('task event: %s', event)
            if 'uuid' in event:
                task = state.tasks.get(event['uuid'])
                logger.debug('current task: %s', task)
                if task.state in ['SUCCESS', 'FAILURE'] and \
                        task.name is not None:
                    runtime = task.runtime if task.runtime else 0
                    data = [{
                        'measurement': 'tasks',
                        'tags': {
                            'worker': task.worker.hostname,
                            'task_name': task.name,
                            'state': task.state,
                        },
                        'fields': {
                            'runtime': float(runtime),
                            'timestamp': float(task.timestamp),
                            'started': float(task.started)
                        }
                    }]
                    agent.push(data, db_config['name'])
        except:
            logger.exception('cannot parse task event')

    def handle_worker_event(event):
        try:
            logger.debug('worker event: %s', event)
            worker_name = event['hostname']
            info = state.workers.get(worker_name)
            logger.debug(info)
            # inspect = app.control.inspect([])
            # stats = inspect.stats()
            # if not stats:
            #     return
            # worker_stat = stats[worker_name]
            print(info.loadavg)

            if 'active' in event and event['active'] > 0:
                data = [{
                    'measurement': 'workers',
                    'tags': {
                        'name': info.hostname
                    },
                    'fields': {
                        'processed': info.processed,
                        'active': info.active,
                        # 'loadavg': info['loadavg']
                        # 'mem': worker_stat['rusage']['maxrss'],
                    }
                }]
                agent.push(data, db_config['name'])
        except:
            logger.exception('cannot parse worker event')

    while agent.run_event.is_set():
        try:
            with app.connection() as connection:
                Receiver = app.subclass_with_self(TourbillonReceiver,
                                                  reverse='events.Receiver')
                recv = Receiver(agent.run_event, connection, handlers={
                    '*': handle_event,
                })

                logger.debug('start capturing events')
                recv.capture()
        except:
            logger.exception('event receiver failed: sleep 1 seconds')
            time.sleep(1)

    logger.debug('get_celery_stats exited')


def get_workers_stats(agent):
    logger.debug('get_workers_stats init')
    agent.run_event.wait()
    config = agent.config['celery']
    db_config = config['database']
    agent.create_database(**db_config)

    app = Celery(broker=config['broker'])
    logger.debug('get_workers_stats init completed')
    while agent.run_event.is_set():
        try:
            logger.debug('gathering workers stats...')
            inspect = app.control.inspect()
            stats = inspect.stats()
            active = inspect.active()
            reserved = inspect.reserved()
            for worker, wdata in stats.items():
                active_by_wk = len(active[worker]) if worker in active else 0
                reserved_by_wk = len(reserved[worker])\
                    if worker in reserved else 0
                rusage = wdata['rusage']
                writes_avg = float(wdata['pool']['writes']['avg'][:-1])
                data = [{
                    'measurement': 'workers_stats',
                    'tags': {
                        'worker': worker
                    },
                    'fields': {
                        'writes_avg': writes_avg,
                        'active': active_by_wk,
                        'reserved': reserved_by_wk
                    }
                }]
                for field, value in rusage.items():
                    data[0]['fields'][field] = value

                agent.push(data, db_config['name'])
                logger.debug('data pushed for worker {}'.format(worker))
        except:
            logger.exception('cannot get workers stats')
        time.sleep(config['workers_stats_frequency'])

    logger.info('get_workers_stats exited')
