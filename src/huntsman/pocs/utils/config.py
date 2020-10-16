import os

from panoptes.utils.config.client import get_config as pocs_get_config


def get_config(key, host=None, port=None, *args, **kwargs):
    """Allow for a custom port.

    Note that this should make it's way upstream eventually.
    """
    host = host or os.getenv('PANOPTES_CONFIG_HOST', 'localhost')
    port = port or os.getenv('PANOPTES_CONFIG_PORT', 6563)
    return pocs_get_config(
        key=key,
        host=host,
        port=port,
        *args,
        **kwargs
    )
