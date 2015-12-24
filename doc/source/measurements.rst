Measurements
************

tourbillon-celery collects metrics about workers and tasks.

Please refers to  `http://docs.celeryproject.org/en/latest/userguide/workers.html <http://docs.celeryproject.org/en/latest/userguide/workers.html>`_ and `http://docs.celeryproject.org/en/latest/userguide/monitoring.html <http://docs.celeryproject.org/en/latest/userguide/monitoring.html>`_ for more information.


Workers
=======

tourbillon-celery listen to the workers heartbeat events and store metrics in the ``workers`` series.
Each datapoint is tagged with the workers name and the values collected are:


Tags
----
	* **name**: worker name

Fields
------

	* **timestamp**: event timestamp
	* **active**: number of currently executing tasks
	* **processed**: number of tasks processed by this worker since it starts


Workers stats
=============

tourbillon-celery inspects the workers statistics and store them in the ``workers_stats`` series. 
Each datapoint is tagged with the workers name and the values collected are:


Tags
----
	* **worker**: worker name

Fields
------

	* **timestamp**: event timestamp
	* **writes_avg**: average of write operations
	* **active**: number of active tasks
	* **reserved**: number reserved tasks
	* **stime**: time spent in operating system code on behalf of this process
	* **utime**: time spent executing user instructions
	* **maxrss**: the maximum resident size used by this process (in kilobytes)
	* **idrss**: amount of unshared memory used for data (in kilobytes times ticks of execution)
	* **isrss**: amount of unshared memory used for stack space (in kilobytes times ticks of execution)
	* **ixrss**: amount of memory shared with other processes (in kilobytes times ticks of execution)
	* **inblock**: number of times the file system had to read from the disk on behalf of this process
	* **oublock**: number of times the file system has to write to disk on behalf of this process
	* **majflt**: number of page faults which were serviced by doing I/O
	* **minflt**: number of page faults which were serviced without doing I/O
	* **msgrcv**: number of IPC messages received
	* **msgsnd**: number of IPC messages sent
	* **nvcsw**: number of times this process voluntarily invoked a context switch
	* **nivcsw**: number of times an involuntary context switch took place
	* **nsignals**: number of signals received
	* **nswap**: the number of times this process was swapped entirely out of memory

Please refers to  `http://docs.celeryproject.org/en/latest/userguide/workers.html#worker-statistics <http://docs.celeryproject.org/en/latest/userguide/workers.html#worker-statistics>`_ for more information.	


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
