import pytest
from google.cloud import compute_v1

client = compute_v1.InstancesClient()

project_vm_instances = ["cdp-rubix-dev-m"]

def test_get_instance_names():
    # Fetch the list of instances
    instances = client.aggregated_list(project="de0360-pkce-rubix-cl-dev000").items
    instance_names = []

    # Process and Get the instance names in a list
    for zone, zone_instances in instances.items():
        for instance in zone_instances.instances or []:
            if instance.name not in instance_names: instance_names.append(instance.name)
            # if instance.name == "cdp-rubix-dev-m":
            print(f' {instance.name} - Guest Accelerators: {instance.disks[0].type_}')
            print("==========")
    return instance_names

