Measurements
************

tourbillon-celery collects metrics about workers and tasks.

Please refers to  `http://docs.celeryproject.org/en/latest/userguide/workers.html <http://docs.celeryproject.org/en/latest/userguide/workers.html>`_ and `http://docs.celeryproject.org/en/latest/userguide/monitoring.html <http://docs.celeryproject.org/en/latest/userguide/monitoring.html>`_ for more information.


Workers
=======

tourbillon-celery listen to the workers heartbeat events and store metrics in the ``workers`` series. It also inspects the worker stats to extract the maximum rss memory used by the worker process.
Each datapoint is tagged with the workers name and the values collected are:


Tags
----
	* **name**: worker name

Values
------

	* **timestamp**: event timestamp
	* **active**: number of currently executing tasks
	* **processed**: number of tasks processed by this worker since it starts
	* **mem**: maximum resident size used by the worker process 


Tasks
=====

tourbillon-celery listen to the tasks events and store metrics in the ``tasks`` series if the task state is **SUCCESS** or **FAILURE**.


Tags
----
	* **worker**: worker name
	* **task_name**: name of the task
	* **state**: task state (SUCCESS, FAILURE)

Fields
------

	* **timestamp**: event timestamp
	* **started**: timestamp in which the worker has started to process the task
	* **runtime**: the number of millis elapsed to process the task
