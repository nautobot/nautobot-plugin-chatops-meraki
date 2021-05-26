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
    get_meraki_firewall_performance,
    get_meraki_network_ssids,
    get_meraki_camera_recent,
)

logger = logging.getLogger("rq.worker")


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
        dispatcher.markdown_block(f"{dispatcher.user_mention()} here are the Meraki organizations"),
        dispatcher.markdown_block("\n".join([x["name"] for x in org_list])),
    ]
    dispatcher.send_blocks(blocks)
    return CommandStatusChoices.STATUS_SUCCEEDED


@subcommand_of("meraki")
def get_admins(dispatcher, org_name=None):
    """Based on an Organization Name Return the Admins."""
    logger.info(f"ORG NAME: {org_name}")
    if not org_name:
        # The user didn't specify an organization, so prompt them to pick one
        org_list = get_meraki_orgs()
        # Build the list of sites, each as a pair of (user-visible string, internal value) entries
        choices = [(x["name"], x["name"]) for x in org_list]
        dispatcher.prompt_from_menu(f"meraki get-admins", "Select Organization", choices)
        # Returning False indicates that the command needed to prompt the user for more information
        return False
    # If gathering information from another system may take some time, it's useful to send the user
    dispatcher.send_markdown(
        f"Stand by {dispatcher.user_mention()}, I'm getting the admins for the Organization {org_name}!"
    )
    admins = get_meraki_org_admins(org_name)
    # Render the list of devices to Markdown for display to the user's chat client
    blocks = [
        dispatcher.markdown_block(f"{dispatcher.user_mention()} here are the admins for {org_name}"),
        dispatcher.markdown_block("\n".join([x["name"] for x in admins])),
    ]
    dispatcher.send_blocks(blocks)
    return CommandStatusChoices.STATUS_SUCCEEDED


@subcommand_of("meraki")
def get_devices(dispatcher, org_name=None):
    """Gathers devices from Meraki API endpoint."""
    logger.info(f"ORG NAME: {org_name}")
    if not org_name:
        org_list = get_meraki_orgs()
        choices = [(x["name"], x["name"]) for x in org_list]
        dispatcher.prompt_from_menu(f"meraki get-devices", "Select Organization", choices)
        return False
    dispatcher.send_markdown(
        f"Stand by {dispatcher.user_mention()}, I'm getting devices from Organization {org_name}!"
    )
    devices = get_meraki_devices(org_name)
    blocks = [
        dispatcher.markdown_block(f"{dispatcher.user_mention()} here are the devices at {org_name}"),
        dispatcher.markdown_block("\n".join([x["name"] for x in devices])),
    ]
    dispatcher.send_blocks(blocks)
    return CommandStatusChoices.STATUS_SUCCEEDED


@subcommand_of("meraki")
def get_switches(dispatcher, org_name=None):
    """Gathers switches from Meraki API endpoint."""
    logger.info(f"ORG NAME: {org_name}")
    if not org_name:
        org_list = get_meraki_orgs()
        choices = [(x["name"], x["name"]) for x in org_list]
        dispatcher.prompt_from_menu(f"meraki get-devices", "Select Organization", choices)
        return False
    dispatcher.send_markdown(
        f"Stand by {dispatcher.user_mention()}, I'm getting switches from Organization {org_name}!"
    )
    devices = get_meraki_devices(org_name)
    blocks = [
        dispatcher.markdown_block(f"{dispatcher.user_mention()} here are the devices at {org_name}"),
        dispatcher.markdown_block("\n".join([x['name'] for x in devices if 'MS' in x['model']])),
    ]
    dispatcher.send_blocks(blocks)
    return CommandStatusChoices.STATUS_SUCCEEDED


@subcommand_of("meraki")
def get_firewalls(dispatcher, org_name=None):
    """Gathers firewalls from Meraki API endpoint."""
    logger.info(f"ORG NAME: {org_name}")
    if not org_name:
        org_list = get_meraki_orgs()
        choices = [(x["name"], x["name"]) for x in org_list]
        dispatcher.prompt_from_menu(f"meraki get-devices", "Select Organization", choices)
        return False
    dispatcher.send_markdown(
        f"Stand by {dispatcher.user_mention()}, I'm getting firewalls from Organization {org_name}!"
    )
    devices = get_meraki_devices(org_name)
    blocks = [
        dispatcher.markdown_block(f"{dispatcher.user_mention()} here are the devices at {org_name}"),
        dispatcher.markdown_block("\n".join([x['name'] for x in devices if 'MX' in x['model']])),
    ]
    dispatcher.send_blocks(blocks)
    return CommandStatusChoices.STATUS_SUCCEEDED


@subcommand_of("meraki")
def get_cameras(dispatcher, org_name=None):
    """Gathers cameras from Meraki API endpoint."""
    logger.info(f"ORG NAME: {org_name}")
    if not org_name:
        org_list = get_meraki_orgs()
        choices = [(x["name"], x["name"]) for x in org_list]
        dispatcher.prompt_from_menu(f"meraki get-devices", "Select Organization", choices)
        return False

    dispatcher.send_markdown(
        f"Stand by {dispatcher.user_mention()}, I'm getting cameras from Organization {org_name}!"
    )
    devices = get_meraki_devices(org_name)
    # Render the list of devices to Markdown for display to the user's chat client
    blocks = [
        dispatcher.markdown_block(f"{dispatcher.user_mention()} here are the devices at {org_name}"),
        dispatcher.markdown_block("\n".join([x['name'] for x in devices if 'MV' in x['model']])),
    ]
    dispatcher.send_blocks(blocks)
    return CommandStatusChoices.STATUS_SUCCEEDED


@subcommand_of("meraki")
def get_aps(dispatcher, org_name=None):
    """Gathers access points from Meraki API endpoint."""
    logger.info(f"ORG NAME: {org_name}")
    # logger.info(f"DEVICE TYPE: {device_type}")
    if not org_name:
        org_list = get_meraki_orgs()
        choices = [(x["name"], x["name"]) for x in org_list]
        dispatcher.prompt_from_menu(f"meraki get-devices", "Select Organization", choices)
        return False
    dispatcher.send_markdown(
        f"Stand by {dispatcher.user_mention()}, I'm getting access points from Organization {org_name}!"
    )
    devices = get_meraki_devices(org_name)
    blocks = [
        dispatcher.markdown_block(f"{dispatcher.user_mention()} here are the devices at {org_name}"),
        dispatcher.markdown_block("\n".join([x['name'] for x in devices if 'MR' in x['model']])),
    ]
    dispatcher.send_blocks(blocks)
    return CommandStatusChoices.STATUS_SUCCEEDED


@subcommand_of("meraki")
def get_networks(dispatcher, org_name=None):
    """Gathers networks from Meraki API endpoint."""
    logger.info(f"ORG NAME: {org_name}")
    if not org_name:
        org_list = get_meraki_orgs()
        choices = [(x["name"], x["name"]) for x in org_list]
        dispatcher.prompt_from_menu(f"meraki get-networks", "Select Organization", choices)
        return False
    dispatcher.send_markdown(
        f"Stand by {dispatcher.user_mention()}, I'm getting the devices at the Organization {org_name}!"
    )
    networks = get_meraki_networks_by_org(org_name)
    blocks = [
        dispatcher.markdown_block(f"{dispatcher.user_mention()} here are the devices at {org_name}"),
        dispatcher.markdown_block("\n".join([x["name"] for x in networks])),
    ]
    dispatcher.send_blocks(blocks)
    return CommandStatusChoices.STATUS_SUCCEEDED


@subcommand_of("meraki")
def get_switchports(dispatcher, org_name=None, device_name=None):
    """Query the Meraki Dashboard API for a list of switch ports."""
    if not org_name:
        dispatcher.send_warning("Organization Name is required. Use `/meraki get-organizations`")
    if not device_name:
        dispatcher.send_warning("Device Name is required. Use `/meraki get-devices`")
    ports = get_meraki_switchports(org_name, device_name)
    dispatcher.send_large_table(
        ["Port ID", "Name", "Tags", "Enabled", "poeEnabled", "Type", "VLAN", "Voice VLAN", "Allowed VLANs", "Isolation Enabled", "RSTP Enabled", "STP Guard", "Link Negotiation", "Port Scheduled ID", "UDLD"],
        [
            (
                entry['portId'],
                entry['name'],
                entry['tags'],
                entry['enabled'],
                entry['poeEnabled'],
                entry['type'],
                entry['vlan'],
                entry['voiceVlan'],
                entry['allowedVlans'],
                entry['isolationEnabled'],
                entry['rstpEnabled'],
                entry['stpGuard'],
                entry['linkNegotiation'],
                entry['portScheduleId'],
                entry['udld'],
            )
            for entry in ports
        ],
    )

    return CommandStatusChoices.STATUS_SUCCEEDED    


@subcommand_of("meraki")
def get_firewall_performance(dispatcher, org_name=None, device_name=None):
    """Query Meraki with a firewall to device performance."""
    pass


@subcommand_of("meraki")
def get_network_ssids(dispatcher, org_name=None, net_name=None):
    """Query Meraki for all SSIDs for a given Network."""
    pass


@subcommand_of("meraki")
def get_meraki_camera_recent(dispatcher, org_name=None, device_name=None):
    """Query Meraki Recent Camera Analytics."""
    pass
