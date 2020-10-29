import redfish
from redfish.rest.v1 import ServerDownOrUnreachableError
import sys
import json
import csv


def connect_to_ilo(system_url, login_account, login_password):
    try:
        redfish_obj = redfish.RedfishClient(base_url=system_url, username=login_account, password=login_password)
        redfish_obj.login(auth="basic")
    except ServerDownOrUnreachableError:
        sys.stderr.write("ERROR: server not reachable or does not support RedFish.\n")
        sys.exit()

    return redfish_obj


def get_resource_directory(redfishobj):
    try:
        resource_uri = redfishobj.root.obj.Oem.Hpe.Links.ResourceDirectory['@odata.id']
    except KeyError:
        sys.stderr.write("Resource directory is only available on HPE servers.\n")
        return None

    response = redfishobj.get(resource_uri)
    resources = []

    if response.status == 200:
        resources = response.dict["Instances"]
    else:
        sys.stderr.write("\tResource directory missing at /redfish/v1/resourcedirectory" + "\n")

    return resources


def get_ilo_disk_info(redfishobj, redfishobj_resources):
    disk_info_list = []
    for instance in redfishobj_resources:
        if 'SmartStorage' in instance['@odata.type'] and 'Systems' in instance['@odata.id']:
            smartstorage_uri = instance['@odata.id']
            array_controllers_uri = redfishobj.get(smartstorage_uri).obj['Links']['ArrayControllers']['@odata.id']
            array_controllers = redfishobj.get(array_controllers_uri).obj['Members']
            for controller in array_controllers:
                controller_dict = {}

                _controller_i_uri = controller['@odata.id']
                controller_i = redfishobj.get(_controller_i_uri)

                # get controller model and status
                controller_dict['model'] = controller_i.obj['Model']

                disk_info_list.append(controller_dict)

                # _physical_disks_uri = controller_i.obj['Links']['PhysicalDrives']['@odata.id']
                # physical_disks = redfishobj.get(_physical_disks_uri).obj['Members']
                # for disk in physical_disks:
                #    print('placeholder')
            break
    return disk_info_list


def get_ilo_memory_info(redfishobj, redfishobj_resources):
    memory_info_list = []
    for instance in redfishobj_resources:
        if 'MemoryCollection' in instance['@odata.type'] and 'Systems' in instance['@odata.id']:
            memory_uri = instance['@odata.id']
            memory_dimms = redfishobj.get(memory_uri).obj['Members']
            for dimm in memory_dimms:
                memory_dict = {}

                _dimm_i = dimm['@odata.id']
                dimm_i = redfishobj.get(_dimm_i)

                memory_dict['Name'] = dimm_i.obj['Name']
                memory_dict['DataWidthBits'] = dimm_i.obj['DataWidthBits']

                memory_info_list.append(memory_dict)
            break

    return memory_info_list


def get_mac_addresses(redfishobj, redfishobj_resources):
    ethernet_interfaces_list = []
    for instance in redfishobj_resources:
        if 'EthernetInterfaceCollection' in instance['@odata.type'] and 'EthernetInterfaces' in instance['@odata.id']:
            ethernet_interfaces_uri = instance['@odata.id']
            ethernet_interfaces = redfishobj.get(ethernet_interfaces_uri).obj['Members']
            for interface in ethernet_interfaces:
                interface_dict = {}

                _interface_i_uri = interface['@odata.id']
                interface_i = redfishobj.get(_interface_i_uri)

                interface_dict['interface_name'] = interface_i.obj['Name']
                interface_dict['interface_mac'] = interface_i.obj['MACAddress']

                ethernet_interfaces_list.append(interface_dict)
            break
    return ethernet_interfaces_list


def get_ilo_processors_info(redfishobj, redfishobj_resources):
    processors_info_list = []
    for instance in redfishobj_resources:
        if 'ProcessorCollection' in instance['@odata.type'] and 'Systems' in instance['@odata.id']:
            processor_uri = instance['@odata.id']
            processors = redfishobj.get(processor_uri).obj['Members']
            for processor in processors:
                processor_dict = {}

                _processor_i = processor['@odata.id']
                processor_i = redfishobj.get(_processor_i)

                processor_dict['id'] = processor_i.obj['Id']
                processor_dict['model'] = processor_i.obj['Model']
                processor_dict['max_speed_mhz'] = processor_i.obj['MaxSpeedMHz']
                processor_dict['total_cores'] = processor_i.obj['TotalCores']
                processor_dict['total_threads'] = processor_i.obj['TotalThreads']

                processors_info_list.append(processor_dict)

            break

    return processors_info_list


def get_ilo_basic_info(redfishobj, redfishobj_resources):
    basic_info_list = []
    for instance in redfishobj_resources:
        if 'ServiceRoot' in instance['@odata.type'] and '/redfish/v1/' in instance['@odata.id']:
            basic_info_dict = {}
            root_uri = instance['@odata.id']
            root = redfishobj.get(root_uri)

            hostname = root.obj['Oem']['Hpe']['Manager'][0]['HostName']

            basic_info_dict['hostname'] = hostname

            basic_info_list.append(basic_info_dict)
        break
    return basic_info_list


def get_health_status(redfishobj, redfishobj_resources):
    health_status_list = []
    for instance in redfishobj_resources:
        if 'ComputerSystemCollection' in instance['@odata.type'] and 'Systems' in instance['@odata.id']:
            systems_uri = instance['@odata.id']
            systems = redfishobj.get(systems_uri).obj['Members']
            for system in systems:
                _system_i = system['@odata.id']
                system_i = redfishobj.get(_system_i)

                health_status_dict = {}
                aggregated_health_status_components = system_i.obj['Oem']['Hpe']['AggregateHealthStatus']

                if aggregated_health_status_components['AgentlessManagementService'] == 'Ready':
                    health_status_dict['agentless_management_service_status'] = 1
                else:
                    health_status_dict['agentless_management_service_status'] = 0

                if aggregated_health_status_components['BiosOrHardwareHealth']['Status']['Health'] == 'OK':
                    health_status_dict['bios_or_hardware_health_status'] = 1
                else:
                    health_status_dict['bios_or_hardware_health_status'] = 0

                if aggregated_health_status_components['FanRedundancy'] == 'Redundant':
                    health_status_dict['fans_redundancy_status'] = 1
                else:
                    health_status_dict['fans_redundancy_status'] = 0

                if aggregated_health_status_components['Fans']['Status']['Health'] == 'OK':
                    health_status_dict['fans_status'] = 1
                else:
                    health_status_dict['fans_status'] = 0

                if aggregated_health_status_components['Memory']['Status']['Health'] == 'OK':
                    health_status_dict['memory_status'] = 1
                else:
                    health_status_dict['memory_status'] = 0

                if aggregated_health_status_components['Network']['Status']['Health'] == 'OK':
                    health_status_dict['network_status'] = 1
                else:
                    health_status_dict['network_status'] = 0

                if aggregated_health_status_components['PowerSupplies']['PowerSuppliesMismatch'] == 'false':
                    health_status_dict['power_supplies_mismatch_status'] = 1
                else:
                    health_status_dict['power_supplies_mismatch_status'] = 0

                if aggregated_health_status_components['PowerSupplies']['Status']['Health'] == 'OK':
                    health_status_dict['power_supplies_status'] = 1
                else:
                    health_status_dict['power_supplies_status'] = 0

                if aggregated_health_status_components['PowerSupplyRedundancy'] == 'Redundant':
                    health_status_dict['power_supply_redundancy_status'] = 1
                else:
                    health_status_dict['power_supply_redundancy_status'] = 0

                if aggregated_health_status_components['Processors']['Status']['Health'] == 'OK':
                    health_status_dict['processors_status'] = 1
                else:
                    health_status_dict['processors_status'] = 0

                if aggregated_health_status_components['SmartStorageBattery']['Status']['Health'] == 'OK':
                    health_status_dict['smart_storage_battery'] = 1
                else:
                    health_status_dict['smart_storage_battery'] = 0

                if aggregated_health_status_components['Storage']['Status']['Health'] == 'OK':
                    health_status_dict['storage_status'] = 1
                else:
                    health_status_dict['storage_status'] = 0

                if aggregated_health_status_components['Temperatures']['Status']['Health'] == 'OK':
                    health_status_dict['temperatures_status'] = 1
                else:
                    health_status_dict['temperatures_status'] = 0

                health_status_list.append(health_status_dict)
    return health_status_list


if __name__ == "__main__":

    SYSTEM_URLS = ["https://ilorestfulapiexplorer.ext.hpe.com/",
                   "https://ilorestfulapiexplorer.ext.hpe.com/",
                   "https://ilorestfulapiexplorer.ext.hpe.com/",
                   "https://ilorestfulapiexplorer.ext.hpe.com/"]
    with open('information.csv', 'w', newline='') as file:
        writer = csv.writer(file)

        for SYSTEM_URL in SYSTEM_URLS:
            LOGIN_ACCOUNT = "admin"
            LOGIN_PASSWORD = "password"

            # create a session and login to ilo
            REDFISHOBJ = connect_to_ilo(SYSTEM_URL, LOGIN_ACCOUNT, LOGIN_PASSWORD)
            REDFISHOBJ_RESOURCES = get_resource_directory(REDFISHOBJ)

            # get information
            INFO_DICT = {'basic_info': get_ilo_basic_info(REDFISHOBJ, REDFISHOBJ_RESOURCES),
                         'disk_info': get_ilo_disk_info(REDFISHOBJ, REDFISHOBJ_RESOURCES),
                         'processor_info': get_ilo_processors_info(REDFISHOBJ, REDFISHOBJ_RESOURCES),
                         'memory_info': get_ilo_memory_info(REDFISHOBJ, REDFISHOBJ_RESOURCES),
                         'ethernet_interfaces': get_mac_addresses(REDFISHOBJ, REDFISHOBJ_RESOURCES),
                         'status': get_health_status(REDFISHOBJ, REDFISHOBJ_RESOURCES)}

            print(json.dumps(INFO_DICT))

            # log out from ilo
            REDFISHOBJ.logout()
