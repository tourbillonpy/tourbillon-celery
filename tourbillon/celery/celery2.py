from celery import Celery
from celery.events import EventReceiver
import logging


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

    def handle_task_event(event):
        try:
            state.event(event)
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
            state.event(event)
            logger.debug('worker event: %s', event)
            worker_name = event['hostname']
            inspect = app.control.inspect([])
            worker_stat = inspect.stats()[worker_name]

            if 'active' in event and event['active'] > 0:
                data = [{
                    'measurement': 'workers',
                    'tags': {
                        'name': event['hostname']
                    },
                    'fields': {
                        'processed': event['processed'],
                        'timestamp': float(event['timestamp']),
                        'active': event['active'],
                        'mem': worker_stat['rusage']['maxrss'],
                    }
                }]
                agent.push(data, db_config['name'])
        except:
            logger.exception('cannot parse worker event')

    with app.connection() as connection:
        Receiver = app.subclass_with_self(TourbillonReceiver,
                                          reverse='events.Receiver')
        recv = Receiver(agent.run_event, connection, handlers={
            'worker-heartbeat': handle_worker_event,
            '*': handle_task_event,
        })

        try:
            logger.debug('start capturing events')
            recv.capture()
        except:
            logger.exception('cannot get celery stats')

    logger.debug('get_celery_stats exited')
