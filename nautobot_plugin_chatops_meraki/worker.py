"""Demo meraki addition to Nautobot."""
import logging

from django_rq import job
from nautobot_chatops.workers import subcommand_of, handle_subcommands
from nautobot_chatops.choices import CommandStatusChoices

from .utils import (
    get_meraki_orgs,
    get_meraki_org_admins,
    get_meraki_devices,
    get_meraki_networks_by_org,
    get_meraki_switchports,
    get_meraki_switchports_status,
    get_meraki_firewall_performance,
    get_meraki_network_ssids,
    get_meraki_camera_recent,
    get_meraki_device_clients,
    get_meraki_device_lldpcdp,
    update_meraki_switch_port,
)

MERAKI_LOGO_PATH = "nautobot_meraki/meraki.png"
MERAKI_LOGO_ALT = "Meraki Logo"

LOGGER = logging.getLogger("nautobot_plugin_chatops_meraki")


DEVICE_TYPES = [
    ("all", "all"),
    ("aps", "aps"),
    ("cameras", "cameras"),
    ("firewalls", "firewalls"),
    ("switches", "switches"),
]


def meraki_logo(dispatcher):
    """Construct an image_element containing the locally hosted Meraki logo."""
    return dispatcher.image_element(dispatcher.static_url(MERAKI_LOGO_PATH), alt_text=MERAKI_LOGO_ALT)


def prompt_for_organization(dispatcher, command):
    """Prompt the user to select a Meraki Organization."""
    org_list = get_meraki_orgs()
    dispatcher.prompt_from_menu(command, "Select an Organization", [(org["name"], org["name"]) for org in org_list])
    return False


def prompt_for_device(dispatcher, command, org, dev_type=None):
    """Prompt the user to select a Meraki device."""
    dev_list = get_meraki_devices(org)
    if not dev_type:
        dispatcher.prompt_from_menu(
            command, "Select a Device", [(dev["name"], dev["name"]) for dev in dev_list if len(dev["name"]) > 0]
        )
        return False
    dev_list = parse_device_list(dev_type, get_meraki_devices(org))
    dispatcher.prompt_from_menu(command, "Select a Device", [(dev, dev) for dev in dev_list])
    return False


def prompt_for_network(dispatcher, command, org):
    """Prompt the user to select a Network name."""
    net_list = get_meraki_networks_by_org(org)
    dispatcher.prompt_from_menu(
        command, "Select a Network", [(net["name"], net["name"]) for net in net_list if len(net["name"]) > 0]
    )
    return False


def prompt_for_port(dispatcher, command, org, switch_name):
    """Prompt the user to select a port from a switch."""
    ports = get_meraki_switchports(org, switch_name)
    dispatcher.prompt_from_menu(command, "Select a Port", [(port["portId"], port["portId"]) for port in ports])
    return False


def parse_device_list(dev_type, devs):
    """Take a list of device and a type and returns only those device types."""
    meraki_dev_mapper = {
        "aps": "MR",
        "cameras": "MV",
        "firewalls": "MX",
        "switches": "MS",
    }
    if dev_type != "all":
        return [dev["name"] for dev in devs if meraki_dev_mapper.get(dev_type) in dev["model"]]
    return [dev["name"] for dev in devs]


@job("default")
def cisco_meraki(subcommand, **kwargs):
    """Interact with Meraki."""
    return handle_subcommands("meraki", subcommand, **kwargs)


@subcommand_of("meraki")
def get_organizations(dispatcher):
    """Gather all the Meraki Organizations."""
    org_list = get_meraki_orgs()
    dispatcher.send_markdown(f"Stand by {dispatcher.user_mention()}, I'm getting the Organizations!")
    blocks = [
        *dispatcher.command_response_header(
            "meraki",
            "get-organizations",
            [],
            meraki_logo(dispatcher),
        ),
        dispatcher.markdown_block(f"{dispatcher.user_mention()} here are the Meraki organizations"),
        dispatcher.markdown_block("\n".join([org["name"] for org in org_list])),
    ]
    dispatcher.send_blocks(blocks)
    return CommandStatusChoices.STATUS_SUCCEEDED


@subcommand_of("meraki")
def get_admins(dispatcher, org_name=None):
    """Based on an Organization Name Return the Admins."""
    LOGGER.info("ORG NAME: %s", org_name)
    if not org_name:
        return prompt_for_organization(dispatcher, "meraki get-admins")
    dispatcher.send_markdown(
        f"Stand by {dispatcher.user_mention()}, I'm getting the admins for the Organization {org_name}!"
    )
    admins = get_meraki_org_admins(org_name)
    blocks = [
        dispatcher.markdown_block(f"{dispatcher.user_mention()} here are the admins for {org_name}"),
        dispatcher.markdown_block("\n".join([admin["name"] for admin in admins])),
    ]
    dispatcher.send_blocks(blocks)
    return CommandStatusChoices.STATUS_SUCCEEDED


@subcommand_of("meraki")
def get_devices(dispatcher, org_name=None, device_type=None):
    """Gathers devices from Meraki."""
    LOGGER.info("ORG NAME: %s", org_name)
    LOGGER.info("DEVICE TYPE: %s", device_type)
    if not org_name:
        return prompt_for_organization(dispatcher, "meraki get-devices")
    if not device_type:
        dispatcher.prompt_from_menu(f"meraki get-devices '{org_name}'", "Select a Device Type", DEVICE_TYPES)
        return False
    LOGGER.info("Translated Device Type: %s", device_type)
    devices = get_meraki_devices(org_name)
    devices_result = parse_device_list(device_type, devices)
    if len(devices_result) > 0:
        blocks = [
            dispatcher.markdown_block(f"{dispatcher.user_mention()} here are the devices requested"),
            dispatcher.markdown_block("\n".join(devices_result)),
        ]
    else:
        blocks = [
            dispatcher.markdown_block(f"{dispatcher.user_mention()} there are NO devices that meet the requirements"),
        ]
    dispatcher.send_blocks(blocks)
    return CommandStatusChoices.STATUS_SUCCEEDED


@subcommand_of("meraki")
def get_networks(dispatcher, org_name=None):
    """Gathers networks from Meraki."""
    LOGGER.info("ORG NAME: %s", org_name)
    if not org_name:
        return prompt_for_organization(dispatcher, "meraki get-networks")
    dispatcher.send_markdown(
        f"Stand by {dispatcher.user_mention()}, I'm getting the networks at the Organization {org_name}!"
    )
    networks = get_meraki_networks_by_org(org_name)
    blocks = [
        dispatcher.markdown_block(f"{dispatcher.user_mention()} here are the networks in {org_name}"),
        dispatcher.markdown_block("\n".join([net["name"] for net in networks])),
    ]
    dispatcher.send_blocks(blocks)
    return CommandStatusChoices.STATUS_SUCCEEDED


@subcommand_of("meraki")
def get_switchports(dispatcher, org_name=None, device_name=None):
    """Gathers switch ports from a MS switch device."""
    LOGGER.info("ORG NAME: %s", org_name)
    LOGGER.info("DEVICE NAME: %s", device_name)
    if not org_name:
        return prompt_for_organization(dispatcher, "meraki get-switchports")
    if not device_name:
        return prompt_for_device(dispatcher, f"meraki get-switchports {org_name}", org_name, dev_type="switches")
    dispatcher.send_markdown(f"Stand by {dispatcher.user_mention()}, I'm getting the switchports from {device_name}!")
    ports = get_meraki_switchports(org_name, device_name)
    dispatcher.send_large_table(
        [
            "Port",
            "Name",
            "Tags",
            "Enabled",
            "PoE",
            "Type",
            "VLAN",
            "Voice VLAN",
            "Allowed VLANs",
            "Isolation Enabled",
            "RSTP Enabled",
            "STP Guard",
            "Link Negotiation",
            "Port Scheduled ID",
            "UDLD",
        ],
        [
            (
                entry["portId"],
                entry["name"],
                entry["tags"],
                entry["enabled"],
                entry["poeEnabled"],
                entry["type"],
                entry["vlan"],
                entry["voiceVlan"],
                entry["allowedVlans"],
                entry["isolationEnabled"],
                entry["rstpEnabled"],
                entry["stpGuard"],
                entry["linkNegotiation"],
                entry["portScheduleId"],
                entry["udld"],
            )
            for entry in ports
        ],
    )
    return CommandStatusChoices.STATUS_SUCCEEDED


@subcommand_of("meraki")
def get_switchports_status(dispatcher, org_name=None, device_name=None):
    """Gathers switch ports status from a MS switch device."""
    LOGGER.info("ORG NAME: %s", org_name)
    LOGGER.info("DEVICE NAME: %s", device_name)
    if not org_name:
        return prompt_for_organization(dispatcher, "meraki get-switchports-status")
    if not device_name:
        return prompt_for_device(dispatcher, f"meraki get-switchports-status {org_name}", org_name, dev_type="switches")
    dispatcher.send_markdown(
        f"Stand by {dispatcher.user_mention()}, I'm getting the switchports status from {device_name}!"
    )
    ports = get_meraki_switchports_status(org_name, device_name)
    dispatcher.send_large_table(
        [
            "Port",
            "Enabled",
            "Status",
            "Errors",
            "Warnings",
            "Speed",
            "Duplex",
            "Usage (Kb)",
            "Client Count",
            "Traffic In (Kbps)",
        ],
        [
            (
                entry["portId"],
                entry["enabled"],
                entry["status"],
                "\n".join(entry["errors"]),
                "\n".join(entry["warnings"]),
                entry["speed"],
                entry["duplex"],
                "\n".join([f"{key}: {value}" for key, value in entry["usageInKb"].items()]),
                entry["clientCount"],
                "\n".join([f"{key}: {value}" for key, value in entry["trafficInKbps"].items()]),
            )
            for entry in ports
        ],
    )
    return CommandStatusChoices.STATUS_SUCCEEDED


@subcommand_of("meraki")
def get_firewall_performance(dispatcher, org_name=None, device_name=None):
    """Query Meraki with a firewall to device performance."""
    LOGGER.info("ORG NAME: %s", org_name)
    LOGGER.info("DEVICE NAME: %s", device_name)
    if not org_name:
        return prompt_for_organization(dispatcher, "meraki get-firewall-performance")
    if not device_name:
        return prompt_for_device(
            dispatcher, f"meraki get-firewall-performance {org_name}", org_name, dev_type="firewalls"
        )
    dispatcher.send_markdown(f"Stand by {dispatcher.user_mention()}, I'm getting the performance for {device_name}!")
    fw_perfomance = get_meraki_firewall_performance(org_name, device_name)
    blocks = [
        dispatcher.markdown_block(f"{dispatcher.user_mention()} here are the devices at {org_name}"),
        dispatcher.markdown_block(f"{device_name} has a performance score of {fw_perfomance['perfScore']}"),
    ]
    dispatcher.send_blocks(blocks)
    return CommandStatusChoices.STATUS_SUCCEEDED


@subcommand_of("meraki")
def get_network_ssids(dispatcher, org_name=None, net_name=None):
    """Query Meraki for all SSIDs for a given Network."""
    LOGGER.info("ORG NAME: %s", org_name)
    LOGGER.info("NETWORK NAME: %s", net_name)
    if not org_name:
        return prompt_for_organization(dispatcher, "meraki get-network-ssids")
    if not net_name:
        return prompt_for_network(dispatcher, f"meraki get-network-ssids {org_name}", org_name)
    dispatcher.send_markdown(f"Stand by {dispatcher.user_mention()}, I'm getting the SSIDs for network {net_name}!")
    ssids = get_meraki_network_ssids(org_name, net_name)
    blocks = [
        dispatcher.markdown_block(f"{dispatcher.user_mention()} here are the SSIDs for network {net_name}"),
        dispatcher.markdown_block("\n".join([ssid["name"] for ssid in ssids])),
    ]
    dispatcher.send_blocks(blocks)
    return CommandStatusChoices.STATUS_SUCCEEDED


@subcommand_of("meraki")
def get_camera_recent(dispatcher, org_name=None, device_name=None):
    """Query Meraki Recent Camera Analytics."""
    LOGGER.info("ORG NAME: %s", org_name)
    LOGGER.info("DEVICE NAME: %s", device_name)
    if not org_name:
        return prompt_for_organization(dispatcher, "meraki get-camera-recent")
    if not device_name:
        return prompt_for_device(dispatcher, f"meraki get-camera-recent '{org_name}'", org_name, dev_type="cameras")
    dispatcher.send_markdown(
        f"Stand by {dispatcher.user_mention()}, I'm getting the recent camera analytics for {device_name}!"
    )
    camera_stats = get_meraki_camera_recent(org_name, device_name)
    dispatcher.send_large_table(
        ["Zone", "Start Time", "End Time", "Entrances", "Average Count"],
        [
            (
                entry["zoneId"],
                entry["startTs"],
                entry["endTs"],
                entry["entrances"],
                entry["averageCount"],
            )
            for entry in camera_stats
        ],
    )
    return CommandStatusChoices.STATUS_SUCCEEDED


@subcommand_of("meraki")
def get_clients(dispatcher, org_name=None, device_name=None):
    """Query Meraki for List of Clients."""
    LOGGER.info("ORG NAME: %s", org_name)
    LOGGER.info("DEVICE NAME: %s", device_name)
    if not org_name:
        return prompt_for_organization(dispatcher, "meraki get-clients")
    if not device_name:
        return prompt_for_device(dispatcher, f"meraki get-clients '{org_name}'", org_name)
    dispatcher.send_markdown(f"Stand by {dispatcher.user_mention()}, I'm getting the clients for {device_name}!")
    client_list = get_meraki_device_clients(org_name, device_name)
    dispatcher.send_large_table(
        ["Usage", "Description", "MAC", "IP", "User", "VLAN", "Switchport", "DHCP Hostname"],
        [
            (
                entry["usage"],
                entry["description"],
                entry["mac"],
                entry["ip"],
                entry["user"],
                entry["vlan"],
                entry["switchport"],
                entry["dhcpHostname"],
            )
            for entry in client_list
        ],
    )
    return CommandStatusChoices.STATUS_SUCCEEDED


@subcommand_of("meraki")
def get_lldp_cdp(dispatcher, org_name=None, device_name=None):
    """Query Meraki for List of LLDP or CDP Neighbors."""
    LOGGER.info("ORG NAME: %s", org_name)
    LOGGER.info("DEVICE NAME: %s", device_name)
    if not org_name:
        return prompt_for_organization(dispatcher, "meraki get-lldp-cdp")
    if not device_name:
        return prompt_for_device(dispatcher, f"meraki get-lldp-cdp '{org_name}'", org_name)
    dispatcher.send_markdown(
        f"Stand by {dispatcher.user_mention()}, I'm getting the discovery protocol information for {device_name}!"
    )
    neighbor_list = get_meraki_device_lldpcdp(org_name, device_name)
    if len(neighbor_list) > 0:
        table_data = []
        for key, vals in neighbor_list["ports"].items():
            for dp_type, dp_vals in vals.items():
                if dp_type == "cdp":
                    print("inside cdp")
                    table_data.append(
                        (key, dp_type, dp_vals.get("deviceId"), dp_vals.get("portId"), dp_vals.get("address"))
                    )
                elif dp_type == "lldp":
                    print("inside lldp")
                    print(dp_vals)
                    table_data.append(
                        (
                            key,
                            dp_type,
                            dp_vals.get("systemName"),
                            dp_vals.get("portId"),
                            dp_vals.get("managementAddress"),
                        )
                    )
                else:
                    print(dp_type)
        dispatcher.send_large_table(
            ["Local Port", "Type", "Remote Device", "Remote Port", "Remote Address"],
            table_data,
        )
    else:
        dispatcher.send_markdown(f"{dispatcher.user_mention()}, NO LLDP/CDP neighbors for {device_name}!")
    return CommandStatusChoices.STATUS_SUCCEEDED


@subcommand_of("meraki")
def configure_basic_access_port(  # pylint: disable=too-many-arguments
    dispatcher, org_name=None, device_name=None, port_number=None, enabled=None, vlan=None, port_desc=None
):
    """Configure an access port with description, VLAN and state."""
    if not org_name:
        return prompt_for_organization(dispatcher, "meraki configure-basic-access-port")
    if not device_name:
        return prompt_for_device(
            dispatcher, f"meraki configure-basic-access-port {org_name}", org_name, dev_type="switches"
        )
    if not port_number:
        return prompt_for_port(
            dispatcher, f"meraki configure-basic-access-port {org_name} {device_name}", org_name, device_name
        )
    if not (enabled and vlan and port_desc):
        if not enabled:
            dispatcher.send_warning("Enable state must be specified")
        if not vlan:
            dispatcher.send_warning("A VLAN must be specified")
        if not port_desc:
            dispatcher.send_warning("A Port Description must be specified")
        dialog_list = [
            {
                "type": "select",
                "label": "Port Enabled Status",
                "choices": [("Port Enabled", "True"), ("Port Disabled", "False")],
                "default": ("Port Enabled", "True"),
            },
            {"type": "text", "label": "VLAN", "default": ""},
            {"type": "text", "label": "Port Description", "default": ""},
        ]
        dispatcher.multi_input_dialog(
            "meraki",
            f"configure-basic-access-port {org_name} {device_name} {port_number}",
            dialog_title="Port Configuration",
            dialog_list=dialog_list,
        )
        return False
    port_params = dict(name=port_desc, enabled=bool(enabled), type="access", vlan=vlan)
    LOGGER.info("PORT PARMS: %s", port_params)
    dispatcher.send_markdown(
        f"Stand by {dispatcher.user_mention()}, I'm configuring port {port_number} on {device_name}!"
    )
    result = update_meraki_switch_port(org_name, device_name, port_number, **port_params)
    blocks = [
        dispatcher.markdown_block(
            f"{dispatcher.user_mention()} The port has been configured, here is the current configuration."
        ),
        dispatcher.markdown_block("\n".join([f"{key}: {value}" for key, value in result.items()])),
    ]
    dispatcher.send_blocks(blocks)
    return CommandStatusChoices.STATUS_SUCCEEDED
