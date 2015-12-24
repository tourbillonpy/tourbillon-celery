Configure
*********


Create the tourbillon-celery configuration file
===============================================

You must create the tourbillon-celery configuration file in order to use tourbillon-celery.
By default, the configuration file must be placed in **/etc/tourbillon/conf.d** and its name
must be **celery.conf**.

The tourbillon-celery configuration file looks like: ::

	{
		"database": {
			"name": "celery",
			"duration": "365d",
			"replication": "1"
		},
		"broker": "amqp://localhost:5672",
		"workers_stats_frequency": 1
	}


You can customize the database name, the retencion policy and the broker url.


Enable the tourbillon-celery metrics collectors
===============================================

To enable the tourbillon-celery metrics collectors types the following command: ::

	$ sudo -i tourbillon enable tourbillon.celery=<collector_name>

Where <collector_name> can be one of or a comma separated list of the colectors names within:
	
	* get_celery_stats
	* get_workers_stats



