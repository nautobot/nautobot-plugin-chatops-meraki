"""Plugin declaration for nautobot_plugin_chatops_meraki."""
# Metadata is inherited from Nautobot. If not including Nautobot in the environment, this should be added
from nautobot.extras.plugins import PluginConfig

__version__ = "1.1.0"


class NautobotPluginChatopsMerakiConfig(PluginConfig):
    """Plugin configuration for the nautobot_plugin_chatops_meraki plugin."""

    name = "nautobot_plugin_chatops_meraki"
    verbose_name = "Nautobot Plugin Chatops Meraki"
    version = __version__
    author = "Network to Code, LLC"
    description = "Nautobot Plugin Chatops Meraki."
    required_settings = []
    min_version = "1.2.3"
    max_version = "1.9999"
    default_settings = {}
    caching_config = {}


config = NautobotPluginChatopsMerakiConfig  # pylint:disable=invalid-name
