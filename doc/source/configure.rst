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
		"broker": "amqp://localhost:5672"
	}


You can customize the database name, the retencion policy and the broker url.


Enable the tourbillon-celery metrics collector
==============================================

To enable the tourbillon-celery metrics collector types the following command: ::

	$ sudo -i tourbillon enable tourbillon.celery=get_celery_stats


