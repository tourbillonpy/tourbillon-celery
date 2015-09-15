from celery import Celery
import logging


logger = logging.getLogger(__name__)


def get_celery_stats(agent):
    agent.run_event.wait()
    config = agent.config['celery']
    db_config = config['database']
    agent.create_database(**db_config)

    app = Celery(broker=config['broker'])
    state = app.events.State()

    def handle_task_event(event):
        state.event(event)
        logger.debug('task event: %s', event)
        if 'uuid' in event:
            task = state.tasks.get(event['uuid'])

            if task.state in ['SUCCESS', 'FAILURE'] and task.name is not None:
                data = [{
                    'measurement': 'tasks',
                    'tags': {
                        'worker': task.worker.hostname,
                        'task_name': task.name,
                        'state': task.state,
                    },
                    'fields': {
                        'runtime': task.runtime if task.runtime else 0,
                        'timestamp': task.timestamp,
                        'started': task.started
                    }
                }]
                agent.push(data, db_config['name'])

    def handle_worker_event(event):
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
                    'timestamp': event['timestamp'],
                    'active': event['active'],
                    'mem': worker_stat['rusage']['maxrss'],
                }
            }]
            agent.push(data, db_config['name'])

    with app.connection() as connection:
        recv = app.events.Receiver(connection, handlers={
            'worker-heartbeat': handle_worker_event,
            '*': handle_task_event,
        })
        while agent.run_event.is_set():
            try:
                recv.capture(limit=config['limit'],
                             timeout=config['timeout'],
                             wakeup=config['wakeup'])
            except:
                logger.exception('cannot get celery stats')

    logger.debug('get_celery_stats exited')
