import pytest
import yaml
from google.cloud import compute_v1

# @pytest.fixture
def config_file():
    # Read the configuration from the YAML file
    with open("/Users/dpkprmr/PycharmProjects/Learning/GCP_Infratests/config/configuration.yaml") as config_file:
        config = yaml.safe_load(config_file)
        project_id = config['gce_project_id']
        zone = config['zone']
        vm_details = config['vm_details']
    return config, project_id, zone, vm_details

@pytest.fixture
def gce_client():
    return compute_v1.InstancesClient()


# Get the Instances List
def get_gce_vm_details(gce_client):
    # Test logic to retrieve and compare VM details using the GCE API
    # Use gce_client.get() or other methods to retrieve VM details
    client = compute_v1.InstancesClient()

    # Fetch the list of instances
    instances = client.aggregated_list(project=config_file()[1]).items #config_file()[1] = project_id
    instance_names = []

    # Process and Get the instance names in a list
    for zone, zone_instances in instances.items():
        for instance in zone_instances.instances or []:
            if instance.name not in instance_names:instance_names.append(instance.name)
    return instance_names

# Get VM Details
def get_vm_details(project_id, zone, instance_name):
    client = compute_v1.InstancesClient()

    # Construct the instance URL manually
    instance_url = f'projects/{project_id}/zones/{zone}/instances/{instance_name}'

    try:
        instance = client.get(project=project_id, zone=zone, instance=instance_name)
        return {
            "Instance Zone": instance.zone,
            "Instance Name": instance.name,
            "Machine Type": instance.machine_type,
            "Status": instance.status,
            "Disks": instance.disks,
            "Deletion Protection": instance.deletion_protection,
            "Labels": instance.labels,
            "Meta Data": instance.metadata,
            "Network Interfaces": instance.network_interfaces,
            "Scheduling": instance.scheduling,
            "Service Accounts": instance.service_accounts,
            "Shielded Config": instance.shielded_instance_config,
            "Tags": instance.tags,
        }
    except Exception as e:
        print(f'Error fetching VM details: {e}')
        return None


# Validate VM Detail
def validate_vm_details(actual_details, expected_details):
    print("Actual details:", actual_details)
    print("Expected details:", expected_details)
    for actual, expected in zip(actual_details, expected_details):
        assert actual["Instance Name"] == expected["instance_name"]
        assert actual["Instance Zone"] == expected["instance_zone"]
        # assert actual["device_name"] == expected["device_name"]
        assert actual["Machine Type"] == expected["machine_type"]
        assert actual["Deletion Protection"] == expected["deletion_protection"]


# Test the instance
def test_vm_detail():
    instances_name = get_gce_vm_details(gce_client)
    for instance_name in instances_name:
        if instance_name == "cdp-rubix-dev-m":
            details = get_vm_details(config_file()[1], config_file()[2], instance_name) #config_file()[2] = zone
            # print(details)
            return details


def test_validate_compute_engine_vm():
    # Load the expected VM details from the config file
    expected_vm_details = config_file()[3][0]
    actual_vm_details = test_vm_detail()
    if actual_vm_details:
        # Validate the actual VM details against the expected details
        validate_vm_details([actual_vm_details], [expected_vm_details])
    else:
        pytest.fail(f"VM in zone not found.")
        print(f'Actual VM Details: {actual_vm_details}')