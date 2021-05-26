"""Demo meraki addition to Nautobot."""
import logging

from django_rq import job
from nautobot_chatops.workers import subcommand_of, handle_subcommands
from nautobot_chatops.choices import CommandStatusChoices

from .utils import (
    get_meraki_orgs,
    get_meraki_org_admins,
    meraki_devices,
    meraki_get_networks_by_org,
    meraki_get_switchports,
)

logger = logging.getLogger("rq.worker")


@job("default")
def cisco_meraki(subcommand, **kwargs):
    """Interact with Meraki."""
    return handle_subcommands("meraki", subcommand, **kwargs)


@subcommand_of("meraki")
def get_meraki_organizations(dispatcher):
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
def get_meraki_org_admins(dispatcher, org_name=None):
    logger.info(f"ORG NAME: {org_name}")
    if not org_name:
        # The user didn't specify an organization, so prompt them to pick one
        org_list = get_meraki_orgs()

        # Build the list of sites, each as a pair of (user-visible string, internal value) entries
        choices = [(x["name"], x["name"]) for x in org_list]
        dispatcher.prompt_from_menu(f"meraki get-meraki-devices", "Select Organization", choices)

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
def get_meraki_devices(dispatcher, org_name=None):
    """Gathers devices from Meraki API endpoint."""
    logger.info(f"ORG NAME: {org_name}")
    if not org_name:
        # The user didn't specify an organization, so prompt them to pick one
        org_list = get_meraki_orgs()

        # Build the list of sites, each as a pair of (user-visible string, internal value) entries
        choices = [(x["name"], x["name"]) for x in org_list]
        dispatcher.prompt_from_menu(f"meraki get-meraki-devices", "Select Organization", choices)

        # Returning False indicates that the command needed to prompt the user for more information
        return False

    # If gathering information from another system may take some time, it's useful to send the user
    dispatcher.send_markdown(
        f"Stand by {dispatcher.user_mention()}, I'm getting the devices at the Organization {org_name}!"
    )

    devices = meraki_devices(org_name)

    # Render the list of devices to Markdown for display to the user's chat client
    blocks = [
        dispatcher.markdown_block(f"{dispatcher.user_mention()} here are the devices at {org_name}"),
        dispatcher.markdown_block("\n".join([x["name"] for x in devices])),
    ]

    dispatcher.send_blocks(blocks)

    return CommandStatusChoices.STATUS_SUCCEEDED
