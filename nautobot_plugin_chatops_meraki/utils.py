"""Utilities for Meraki SDK."""

import meraki


def _org_name_to_id(org_name):
    """Translate Org Name to Org Id."""
    return [org["id"] for org in get_meraki_orgs() if org["name"].lower() == org_name.lower()][0]


def _name_to_serial(org_name, device_name):
    """Translate Name to Serial."""
    return [dev["serial"] for dev in get_meraki_devices(org_name) if dev["name"] == device_name][0]


def _netname_to_id(org_name, net_name):
    """Translate Network Name to Network ID."""
    return [net["id"] for net in get_meraki_networks_by_org(org_name) if net["name"] == net_name][0]


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


def get_meraki_switchports(org_name, device_name):
    """Query the Meraki Dashboard API for a list of Switchports for a Switch."""
    dashboard = meraki.DashboardAPI(suppress_logging=True)
    return dashboard.switch.getDeviceSwitchPorts(_name_to_serial(org_name, device_name))


def get_meraki_switchports_status(org_name, device_name):
    """Query Meraki for Port Status for a Switch."""
    dashboard = meraki.DashboardAPI(suppress_logging=True)
    return dashboard.switch.getDeviceSwitchPortsStatuses(_name_to_serial(org_name, device_name))


def get_meraki_firewall_performance(org_name, device_name):
    """Query Meraki with a firewall to return device performance."""
    dashboard = meraki.DashboardAPI(suppress_logging=True)
    return dashboard.appliance.getDeviceAppliancePerformance(_name_to_serial(org_name, device_name))


def get_meraki_network_ssids(org_name, net_name):
    """Query Meraki for a Networks SSIDs."""
    dashboard = meraki.DashboardAPI(suppress_logging=True)
    return dashboard.wireless.getNetworkWirelessSsids(_netname_to_id(org_name, net_name))


def get_meraki_camera_recent(org_name, device_name):
    """Query Meraki Recent Cameras."""
    dashboard = meraki.DashboardAPI(suppress_logging=True)
    return dashboard.camera.getDeviceCameraAnalyticsRecent(_name_to_serial(org_name, device_name))


def get_meraki_device_clients(org_name, device_name):
    """Query Meraki for Clients."""
    dashboard = meraki.DashboardAPI(suppress_logging=True)
    return dashboard.devices.getDeviceClients(_name_to_serial(org_name, device_name))


def get_meraki_device_lldpcdp(org_name, device_name):
    """Query Meraki for Clients."""
    dashboard = meraki.DashboardAPI(suppress_logging=True)
    return dashboard.devices.getDeviceLldpCdp(_name_to_serial(org_name, device_name))


def update_meraki_switch_port(org_name, device_name, port, **kwargs):
    """Update SwitchPort Configuration."""
    dashboard = meraki.DashboardAPI(suppress_logging=True)
    return dashboard.switch.updateDeviceSwitchPort(_name_to_serial(org_name, device_name), port, **kwargs)
