"""Utilities for Meraki SDK."""

import meraki


def _org_name_to_id(org_name):
    """Translate Org Name to Org Id."""
    return [org['id'] for org in get_meraki_orgs() if org['name'] == org_name][0]


def _switchname_to_id(sw_name):
    """Translate Switch Name to Switch ID."""
    pass


def get_meraki_orgs():
    """Query the Meraki Dashboard API for a list of defined organizations."""
    dashboard = meraki.DashboardAPI(suppress_logging=True)
    return dashboard.organizations.getOrganizations()


def get_meraki_org_admins(org_name):
    """Query the Meraki Dashboard API for the admins of a organization."""
    dashboard = meraki.DashboardAPI(suppress_logging=True)
    return dashboard.organizations.getOrganizationAdmins(_org_name_to_id(org_name))


def get_meraki_devices(org_name):
    """Query the Meraki Dashboard API for a list of devices in the given organization."""
    dashboard = meraki.DashboardAPI(suppress_logging=True)
    return dashboard.organizations.getOrganizationDevices(organizationId=_org_name_to_id(org_name))


def get_meraki_networks_by_org(org_name):
    """Query the Meraki Dashboard API for a list of Networks."""
    dashboard = meraki.DashboardAPI(suppress_logging=True)
    return dashboard.organizations.getOrganizationNetworks(_org_name_to_id(org_name))


def get_meraki_switchports(sn):
    """Query the Meraki Dashboard API for a list of Networks."""
    dashboard = meraki.DashboardAPI(suppress_logging=True)
    return dashboard.switch.getDeviceSwitchPorts(sn)
