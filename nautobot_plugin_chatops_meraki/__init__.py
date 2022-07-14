"""Plugin declaration for nautobot_plugin_chatops_meraki."""
try:
    from importlib import metadata
except ImportError:
    # Python version < 3.8
    import importlib_metadata as metadata

__version__ = metadata.version(__name__)

from nautobot.extras.plugins import PluginConfig


class NautobotPluginChatopsMerakiConfig(PluginConfig):
    """Plugin configuration for the nautobot_plugin_chatops_meraki plugin."""

    name = "nautobot_plugin_chatops_meraki"
    verbose_name = "Nautobot Plugin Chatops Meraki"
    version = __version__
    author = "Network to Code, LLC"
    description = "Nautobot Plugin Chatops Meraki."
    required_settings = []
    min_version = "1.1.0"
    max_version = "1.9999"
    default_settings = {}
    caching_config = {}


config = NautobotPluginChatopsMerakiConfig  # pylint:disable=invalid-name
