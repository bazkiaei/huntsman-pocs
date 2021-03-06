import socket

import click
from huntsman.pocs.utils.logger import logger
from huntsman.pocs.utils.pyro.nameserver import pyro_nameserver
from huntsman.pocs.utils.pyro.service import pyro_service


@click.group()
@click.option('--verbose/--no-verbose', help='Turn on logger for panoptes utils, default False')
@click.option('--host', default=None, help='The config server IP address or host name. '
                                           'If None, lookup in config-server, else default localhost.')
@click.option('--port', default=None, help='The config server port. If None, lookup in config-server, else '
                                           'default 0 for auto-assign.')
@click.pass_context
def entry_point(context, host=None, port=None, verbose=False):
    context.ensure_object(dict)
    context.obj['host'] = host
    context.obj['port'] = port

    if verbose:
        logger.enable('panoptes')


@click.command('nameserver')
@click.option('--auto-clean', default=0, help='Interval in seconds to perform automatic object cleanup, '
                                              'default 0 for no auto_cleaning.')
@click.pass_context
def nameserver(context, auto_clean=0):
    """Starts the pyro name server.

    This function is registered as an entry_point for the module and should be called from
    the command line accordingly.
    """
    host = context.obj.get('host')
    port = context.obj.get('port')

    try:
        logger.info(f'Creating Pyro nameserver')
        ns_proc = pyro_nameserver(host=host, port=port, auto_clean=auto_clean, auto_start=False)
        logger.info(f'Starting Pyro nameserver from cli')
        ns_proc.start()
        logger.info(f'Pyro nameserver started. Ctrl-C/Cmd-C to quit...')
        ns_proc.join()
    except KeyboardInterrupt:
        logger.info(f'Pyro nameserver interrupted, shutting down.')
    except Exception as e:  # noqa
        logger.error(f'Pyro nameserver shutdown unexpectedly {e!r}')
    finally:
        logger.info(f'Pyro nameserver shut down.')


@click.command('service')
@click.option('--service-name', default=None,
              help='The name of the service to register with the nameserver.'
                   'If the default `None`, then the device hostname will be used.')
@click.option('--service-class', required=True, default=None,
              help='The class to register with Pyro. '
                   'This should be the fully qualified namespace for the class, '
                   'e.g. huntsman.pocs.camera.pyro.CameraService.')


@click.pass_context
def service(context, service_name, service_class=None):
    """Starts a pyro service.

    This function is registered as an entry_point for the module and should be called from
    the command line on a remote (to the control computer) device.
    """
    host = context.obj.get('host')
    port = context.obj.get('port')

    service_name = service_name or socket.gethostname()

    logger.info(f'Starting pyro service_name={service_name} for service_class={service_class}')

    try:
        logger.info(f'Creating Pyro service {service_name}')

        # Start the request loop
        pyro_service(service_class=service_class, service_name=service_name, host=host,
                     port=port)

    except (KeyboardInterrupt, StopIteration):
        logger.info(f'Pyro service {service_name} interrupted, shutting down.')
    except Exception as e:  # noqa
        logger.error(f'Pyro {service_name} shutdown unexpectedly {e!r}')
    finally:
        logger.info(f'Pyro {service_name} shut down.')


entry_point.add_command(nameserver)
entry_point.add_command(service)
