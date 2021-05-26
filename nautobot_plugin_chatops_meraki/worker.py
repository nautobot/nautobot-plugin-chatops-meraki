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
    # If gathering information from another system may take some time, it's useful to send the user
    dispatcher.send_markdown(f"Stand by {dispatcher.user_mention()}, I'm getting the Organizations!")
    # Render the list of devices to Markdown for display to the user's chat client
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
def get_devices(dispatcher, org_name=None, device_type=None):
    """Gathers devices from Meraki API endpoint."""
    logger.info(f"ORG NAME: {org_name}")
    logger.info(f"DEVICE TYPE: {device_type}")
    if not org_name:
        org_list = get_meraki_orgs()
        choices = [(x["name"], x["name"]) for x in org_list]
        dispatcher.prompt_from_menu(f"meraki get-devices", "Select Organization", choices)
        return False
    if not device_type:
        device_choices = ["All", "Access Points", "Cameras", "Firewalls", "Switches"]
        dispatcher.prompt_from_menu(f"meraki get-devices", "Select Device Type", device_choices)
        return False

    dispatcher.send_markdown(
        f"Stand by {dispatcher.user_mention()}, I'm getting {device_type} from Organization {org_name}!"
    )
    devices = get_meraki_devices(org_name)
    # Render the list of devices to Markdown for display to the user's chat client
    blocks = [
        dispatcher.markdown_block(f"{dispatcher.user_mention()} here are the devices at {org_name}"),
        dispatcher.markdown_block("\n".join([x["name"] for x in devices])),
    ]
    dispatcher.send_blocks(blocks)
    return CommandStatusChoices.STATUS_SUCCEEDED


def get_switches():
    pass


def get_firewalls():
    pass


def get_cameras():
    pass


def get_aps():
    pass


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
    # Render the list of devices to Markdown for display to the user's chat client
    blocks = [
        dispatcher.markdown_block(f"{dispatcher.user_mention()} here are the devices at {org_name}"),
        dispatcher.markdown_block("\n".join([x["name"] for x in networks])),
    ]
    dispatcher.send_blocks(blocks)
    return CommandStatusChoices.STATUS_SUCCEEDED