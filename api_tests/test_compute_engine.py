import allure
import pytest
import yaml
from google.cloud import compute_v1

# Read configuration from the YAML file
with open("/Users/dpkprmr/PycharmProjects/Learning/GCP_Infratests/config/config.yaml", "r") as config_file:
    config = yaml.safe_load(config_file)


'''
    ====================
    Fixture to fetch VM instances for each project and store them as class attributes
    ====================
'''
def fetch_project_vm_instances(project_id, zone):
    # Get the zone for the specific project from the configuration
    project = next((p for p in config["projects"] if p["project_id"] == project_id), None)
    if not project:
        raise ValueError(f"Project with project_id '{project_id}' not found")

    zone = project.get("zone", None)
    if not zone:
        raise ValueError(f"Zone not specified for project with project_id '{project_id}' in the configuration YAML.")

    vm_client = compute_v1.InstancesClient()
    instances = vm_client.list(project=project_id, zone=zone)

    return project_id, instances


@allure.feature("Compute Engine")
class TestComputeEngine:

    @pytest.fixture(scope="class")
    def project_vm_instances(self, request):
        instances_list = []
        for project in config["projects"]:
            project_id = project["project_id"]
            zone = project.get("zone", None)
            if not zone:
                raise ValueError(f"Zone not specified for project with project_id '{project_id}' in the configuration YAML.")

            instances = fetch_project_vm_instances(project_id, zone)
            instances_list.append(instances)

        return instances_list

    '''
            ============
            Test Case 1
            ============
    '''
    @allure.story("Verify tags are attached to every Compute Engine VM Resource")
    @pytest.mark.parametrize("project_vm_instances", [(p["project_id"],) for p in config["projects"]], indirect=True)
    @pytest.mark.severity("Medium")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.smoke("Smoke")
    @allure.label("Suite", "Smoke")
    @allure.label("Severity", "Medium")
    def test_tags_attached(self, project_vm_instances):
        for project_id, instances in project_vm_instances:
            if not instances:
                continue

            missing_tags_instances = []  # Instances missing required tags

            for instance in instances:
                test_case_name = f"Tags Test Case - {project_id}"
                allure.dynamic.title(test_case_name)

                assert_value = next(p["tags_assertion"] for p in config["projects"] if p["project_id"] == project_id)
                tags = instance.tags.items if instance.tags else None
                assert_result = (tags is not None) == assert_value

                with allure.step(f"Check Tags for VM instance {instance.name} in project {project_id}"):
                    if assert_result:
                        allure.dynamic.label("result", "passed")
                        print(f"Tags found for VM instance {instance.name} in project {project_id}")
                    else:
                        allure.dynamic.label("result", "failed")
                        print(f"No Tags found for VM instance {instance.name} in project {project_id}")
                        missing_tags_instances.append(instance.name)

            # Generate a title based on assertion results
            if not missing_tags_instances:
                title = "All instances have required tags attached"
            else:
                title = f"Instances missing required tags: {', '.join(missing_tags_instances)}"

            # Raise an assertion error if any instance failed the assertion
            assert all([(tags is not None) == assert_value for tags in
                        [instance.tags.items if instance.tags else None for instance in instances]]), title

    '''
            ============
            Test Case 2
            ============
    '''
    @allure.story("Verify labels are attached to every Compute Engine VM Resource")
    @pytest.mark.parametrize("project_vm_instances", [(p["project_id"],) for p in config["projects"]], indirect=True)
    @pytest.mark.severity("Medium")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.smoke("Smoke")
    @allure.label("Suite", "Smoke")
    @allure.label("Severity", "Medium")
    def test_labels_attached(self, project_vm_instances):
        for project_id, instances in project_vm_instances:
            if not instances:
                continue

            missing_labels_instances = []  # Instances missing required labels

            for instance in instances:
                test_case_name = f"Labels Test Case - {project_id}"
                allure.dynamic.title(test_case_name)

                assert_value = next(p["labels_assertion"] for p in config["projects"] if p["project_id"] == project_id)
                labels = instance.labels.items if instance.labels else None
                assert_result = (labels is not None) == assert_value

                with allure.step(f"Check Labels for VM instance {instance.name} in project {project_id}"):
                    if assert_result:
                        allure.dynamic.label("result", "passed")
                        print(f"Labels found for VM instance {instance.name} in project {project_id}")
                    else:
                        allure.dynamic.label("result", "failed")
                        print(f"No Labels found for VM instance {instance.name} in project {project_id}")
                        missing_labels_instances.append(instance.name)

            # Generate a title based on assertion results
            if not missing_labels_instances:
                title = "All instances have required labels attached"
            else:
                title = f"Instances missing required labels: {', '.join(missing_labels_instances)}"

            # Raise an assertion error if any instance failed the assertion
            assert all([(labels is not None) == assert_value for labels in
                        [instance.labels.items if instance.labels else None for instance in instances]]), title

    '''
            ============
            Test Case 3
            ============
    '''
    @allure.story("Verify the zone for every Compute Engine VM Resource is europe-west3-x")
    @pytest.mark.parametrize("project_vm_instances", [(p["project_id"],) for p in config["projects"]], indirect=True)
    @pytest.mark.severity("Critical")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke("Smoke")
    @allure.label("Suite", "Smoke")
    @allure.label("Severity", "Critical")
    def test_zone_europe_west3_x(self, project_vm_instances):
        for project_id, instances in project_vm_instances:
            if not instances:
                continue

            wrong_zone_instances = []  # Instances in zones other than europe-west3-x

            for instance in instances:
                test_case_name = f"Zone Test Case - {project_id}"
                allure.dynamic.title(test_case_name)

                zone_assertion = next(
                    (p["zone_assertion"] for p in config["projects"] if p["project_id"] == project_id), None)

                if zone_assertion is None:
                    raise ValueError(
                        f"Zone assertion not found for project_id '{project_id}' in the configuration YAML.")

                assert_result = instance.zone.endswith(zone_assertion)

                with allure.step(f"Check Zone for VM instance {instance.name} in project {project_id}"):
                    if assert_result:
                        allure.dynamic.label("result", "passed")
                        print(f"Zone assertion passed for VM instance {instance.name}")
                    else:
                        allure.dynamic.label("result", "failed")
                        print(f"Zone assertion failed for VM instance {instance.name}")
                        wrong_zone_instances.append(instance.name)

            # Generate a title based on assertion results
            if not wrong_zone_instances:
                title = f"All instances are in the correct zone: {zone_assertion}"
            else:
                title = f"Instances in wrong zones: {', '.join(wrong_zone_instances)}"

            # Raise an assertion error if any instance failed the assertion
            assert all([instance.zone.endswith(zone_assertion) for instance in instances]), title

    '''
            ============
            Test Case 4
            ============
    '''

    @allure.story("Verify deletion protection is enabled for every Compute Engine VM Resource")
    @pytest.mark.parametrize("project_vm_instances", [(p["project_id"],) for p in config["projects"]], indirect=True)
    @pytest.mark.severity("Medium")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.smoke("Smoke")
    @allure.label("Suite", "Smoke")
    @allure.label("Severity", "Medium")
    def test_deletion_protection_enabled(self, project_vm_instances):
        for project_id, instances in project_vm_instances:
            if not instances:
                continue

            print(f"Running test for Project ID: {project_id}")

            enabled_instances = []  # Instances with deletion protection enabled
            disabled_instances = []  # Instances with deletion protection disabled

            for instance in instances:
                test_case_name = f"Deletion Protection Test Case - {project_id}"
                allure.dynamic.title(test_case_name)

                assert_value = next(
                    p["deletion_protection_assertion"] for p in config["projects"] if p["project_id"] == project_id)
                deletion_protection = instance.deletion_protection
                assert_result = deletion_protection == assert_value

                with allure.step(f"Check Deletion Protection for VM instance {instance.name} in project {project_id}"):
                    if assert_result:
                        allure.dynamic.label("result", "passed")
                        print(f"Deletion Protection is enabled for VM instance {instance.name} in project {project_id}")
                        enabled_instances.append(instance.name)
                    else:
                        allure.dynamic.label("result", "failed")
                        print(
                            f"Deletion Protection is not enabled for VM instance {instance.name} in project {project_id}")
                        disabled_instances.append(instance.name)

            # Generate a custom error message based on assertion results
            if not enabled_instances:
                failed_instances = ", ".join(disabled_instances)
                raise AssertionError(
                    f"All instances have Deletion Protection disabled: Instance(s) Names: {failed_instances}")
            elif not disabled_instances:
                passed_instances = ", ".join(enabled_instances)
                raise AssertionError(
                    f"All instances have Deletion Protection enabled: Instance(s) Names: {passed_instances}")

    '''
            ============
            Test Case 5
            ============
    '''
    @allure.story("Verify Display Device is disabled for every Compute Engine VM Resource")
    @pytest.mark.parametrize("project_vm_instances", [(p["project_id"],) for p in config["projects"]], indirect=True)
    @pytest.mark.severity("Low")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.smoke("Smoke")
    @allure.label("Suite", "Smoke")
    @allure.label("Severity", "Low")
    def test_display_device_disabled(self, project_vm_instances):
        for project_id, instances in project_vm_instances:
            if not instances:
                continue

            enabled_instances = []  # Instances with Display Device enabled
            disabled_instances = []  # Instances with Display Device disabled

            for instance in instances:
                test_case_name = f"Display Device Test Case - {project_id}"
                allure.dynamic.title(test_case_name)

                assert_value = next(
                    p["display_device_assertion"] for p in config["projects"] if p["project_id"] == project_id)
                display_device = instance.display_device
                assert_result = not display_device == assert_value

                with allure.step(f"Check Display Device for VM instance {instance.name} in project {project_id}"):
                    if assert_result:
                        allure.dynamic.label("result", "passed")
                        print(f"Display Device is disabled for VM instance {instance.name} in project {project_id}")
                        disabled_instances.append(instance.name)
                    else:
                        allure.dynamic.label("result", "failed")
                        print(f"Display Device is enabled for VM instance {instance.name} in project {project_id}")
                        enabled_instances.append(instance.name)

            # Generate a title based on assertion results
            if not enabled_instances:
                title = f"All instances have Display Device disabled: Instance(s) Names: {', '.join(disabled_instances)}"
            elif not disabled_instances:
                title = f"All instances have Display Device enabled: Instance(s) Names: {', '.join(enabled_instances)}"
            else:
                title = f"Instances with Display Device enabled: {', '.join(enabled_instances)} | Instances with Display Device disabled: {', '.join(disabled_instances)}"

            # Raise an assertion error if any instance failed the assertion
            assert all([not instance.display_device for instance in instances]), title

    '''
            ============
            Test Case 6
            ============
    '''
    @allure.story("Verify no GPU is assigned to any Compute Engine VM Resource")
    @pytest.mark.parametrize("project_vm_instances", [(p["project_id"],) for p in config["projects"]], indirect=True)
    @pytest.mark.severity("Low")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.smoke("Smoke")
    @allure.label("Suite", "Smoke")
    @allure.label("Severity", "Low")
    def test_no_gpu_assigned(self, project_vm_instances):
        for project_id, instances in project_vm_instances:
            if not instances:
                continue

            print(f"Running test for Project ID: {project_id}")

            gpu_assigned_instances = []  # Instances with GPU assigned
            no_gpu_assigned_instances = []  # Instances without GPU assigned

            for instance in instances:
                test_case_name = f"No GPU Test Case - {project_id}"
                allure.dynamic.title(test_case_name)

                assert_value = next(p["no_gpu_assertion"] for p in config["projects"] if p["project_id"] == project_id)
                gpu_count = len(instance.guest_accelerators)
                assert_result = gpu_count == assert_value

                with allure.step(f"Check GPU assignment for VM instance {instance.name} in project {project_id}"):
                    if assert_result:
                        allure.dynamic.label("result", "passed")
                        print(f"No GPU assigned for VM instance {instance.name} in project {project_id}")
                        no_gpu_assigned_instances.append(instance.name)
                    else:
                        allure.dynamic.label("result", "failed")
                        print(f"GPU assigned for VM instance {instance.name} in project {project_id}")
                        gpu_assigned_instances.append(instance.name)

            # Generate a title based on assertion results
            if not gpu_assigned_instances:
                title = f"All instances have no GPU assigned: Instance(s) Names: {', '.join(no_gpu_assigned_instances)}"
            elif not no_gpu_assigned_instances:
                title = f"All instances have GPU assigned: Instance(s) Names: {', '.join(gpu_assigned_instances)}"
            else:
                title = f"Instances with GPU assigned: {', '.join(gpu_assigned_instances)} | Instances without GPU assigned: {', '.join(no_gpu_assigned_instances)}"

            # Raise an assertion error if any instance failed the assertion
            assert all(
                [gpu_count == 0 for gpu_count in [len(instance.guest_accelerators) for instance in instances]]), title

    '''
            ============
            Test Case 7
            ============
    '''
    @allure.story("Verify Persistent Boot Disk for every Compute Engine VM Resource")
    @pytest.mark.parametrize("project_vm_instances", [(p["project_id"],) for p in config["projects"]], indirect=True)
    @pytest.mark.severity("High")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke("Smoke")
    @allure.label("Suite", "Smoke")
    @allure.label("Severity", "High")
    def test_persistent_boot_disk(self, project_vm_instances):
        for project_id, instances in project_vm_instances:
            if not instances:
                continue

            non_persistent_instances = []  # Instances with non-persistent boot disk

            for instance in instances:
                test_case_name = f"Persistent Boot Disk Test Case - {project_id}"
                allure.dynamic.title(test_case_name)

                assert_value = next(
                    p["persistent_boot_disk_assertion"] for p in config["projects"] if p["project_id"] == project_id)
                boot_disk_type = instance.disks[0].type_ if instance.disks and instance.disks[0].type_ else None

                assert_result = boot_disk_type == assert_value

                with allure.step(f"Check Persistent Boot Disk for VM instance {instance.name} in project {project_id}"):
                    if assert_result:
                        allure.dynamic.label("result", "passed")
                        print(f"Persistent Boot Disk for VM instance {instance.name} in project {project_id}")
                    else:
                        allure.dynamic.label("result", "failed")
                        print(f"Non-Persistent Boot Disk for VM instance {instance.name} in project {project_id}")
                        non_persistent_instances.append(instance.name)

            # Generate a title based on assertion results
            if not non_persistent_instances:
                title = "All instances have Persistent Boot Disk"
            else:
                title = f"Instances with Non-Persistent Boot Disk: {', '.join(non_persistent_instances)}"

            # Raise an assertion error if any instance failed the assertion
            assert all([boot_disk_type == assert_value for boot_disk_type in [
                instance.disks[0].type_ if instance.disks and instance.disks[0].type_ else None for instance in
                instances]]), title

    '''
            ============
            Test Case 8
            ============
    '''
    @allure.story("Verify Secure Boot is enabled for every Compute Engine VM Resource")
    @pytest.mark.parametrize("project_vm_instances", [(p["project_id"],) for p in config["projects"]], indirect=True)
    @pytest.mark.severity("High")
    @pytest.mark.smoke("Smoke")
    @allure.label("Suite", "Smoke")
    @allure.label("Severity", "High")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_secure_boot(self, project_vm_instances):
        for project_id, instances in project_vm_instances:
            if not instances:
                continue

            disabled_secure_boot_instances = []  # Instances with Secure Boot disabled

            for instance in instances:
                test_case_name = f"Secure Boot Test Case - {project_id}"
                allure.dynamic.title(test_case_name)

                assert_value = next(
                    p["secure_boot_assertion"] for p in config["projects"] if p["project_id"] == project_id)
                secure_boot = instance.shielded_instance_config.enable_secure_boot

                assert_result = secure_boot == assert_value

                with allure.step(f"Check Secure Boot for VM instance {instance.name} in project {project_id}"):
                    if assert_result:
                        allure.dynamic.label("result", "passed")
                        print(f"Secure Boot is enabled for VM instance {instance.name} in project {project_id}")
                    else:
                        allure.dynamic.label("result", "failed")
                        print(f"Secure Boot is disabled for VM instance {instance.name} in project {project_id}")
                        disabled_secure_boot_instances.append(instance.name)

            # Generate a title based on assertion results
            if not disabled_secure_boot_instances:
                title = "All instances have Secure Boot enabled"
            else:
                title = f"Instances with Secure Boot disabled: {', '.join(disabled_secure_boot_instances)}"

            # Raise an assertion error if any instance failed the assertion
            assert all([secure_boot for secure_boot in
                        [instance.shielded_instance_config.enable_secure_boot for instance in instances]]), title

    '''
            ============
            Test Case 9
            ============
    '''
    @allure.story("Verify vTPM is enabled for every Compute Engine VM Resource")
    @pytest.mark.parametrize("project_vm_instances", [(p["project_id"],) for p in config["projects"]], indirect=True)
    @pytest.mark.severity("High")
    @pytest.mark.smoke("Smoke")
    @allure.label("Suite", "Smoke")
    @allure.label("Severity", "High")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_vtpm(self, project_vm_instances):
        for project_id, instances in project_vm_instances:
            if not instances:
                continue

            disabled_vtpm_instances = []  # Instances with vTPM disabled

            for instance in instances:
                test_case_name = f"vTPM Test Case - {project_id}"
                allure.dynamic.title(test_case_name)

                assert_value = next(p["vtpm_assertion"] for p in config["projects"] if p["project_id"] == project_id)
                vtpm_enabled = instance.shielded_instance_config.enable_vtpm if instance.shielded_instance_config and instance.shielded_instance_config.enable_vtpm else None

                assert_result = vtpm_enabled == assert_value

                with allure.step(f"Check vTPM for VM instance {instance.name} in project {project_id}"):
                    if assert_result:
                        allure.dynamic.label("result", "passed")
                        print(f"vTPM is enabled for VM instance {instance.name} in project {project_id}")
                    else:
                        allure.dynamic.label("result", "failed")
                        print(f"vTPM is disabled for VM instance {instance.name} in project {project_id}")
                        disabled_vtpm_instances.append(instance.name)

            # Generate a title based on assertion results
            if not disabled_vtpm_instances:
                title = "All instances have vTPM enabled"
            else:
                title = f"Instances with vTPM disabled: {', '.join(disabled_vtpm_instances)}"

            # Raise an assertion error if any instance failed the assertion
            assert all([vtpm_enabled == assert_value for vtpm_enabled in [
                instance.shielded_instance_config.enable_vtpm if instance.shielded_instance_config and instance.shielded_instance_config.enable_vtpm else None
                for instance in instances]]), title

    '''
            ============
            Test Case 10
            ============
    '''
    @allure.story("Verify Integrity Monitoring is enabled for every Compute Engine VM Resource")
    @pytest.mark.parametrize("project_vm_instances", [(p["project_id"],) for p in config["projects"]], indirect=True)
    @pytest.mark.severity("High")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke("Smoke")
    @allure.label("Suite", "Smoke")
    @allure.label("Severity", "High")
    def test_integrity_monitoring(self, project_vm_instances):
        for project_id, instances in project_vm_instances:
            if not instances:
                continue

            disabled_integrity_monitoring_instances = []  # Instances with Integrity Monitoring disabled

            for instance in instances:
                test_case_name = f"Integrity Monitoring Test Case - {project_id}"
                allure.dynamic.title(test_case_name)

                assert_value = next(
                    p["integrity_monitoring_assertion"] for p in config["projects"] if p["project_id"] == project_id)
                integrity_monitoring_enabled = instance.shielded_instance_config.enable_integrity_monitoring  # if instance.virtual_machine and instance.shielded_instance_config.enable_integrity_monitoring else None

                assert_result = integrity_monitoring_enabled == assert_value

                with allure.step(f"Check Integrity Monitoring for VM instance {instance.name} in project {project_id}"):
                    if assert_result:
                        allure.dynamic.label("result", "passed")
                        print(
                            f"Integrity Monitoring is enabled for VM instance {instance.name} in project {project_id}")
                    else:
                        allure.dynamic.label("result", "failed")
                        print(
                            f"Integrity Monitoring is disabled for VM instance {instance.name} in project {project_id}")
                        disabled_integrity_monitoring_instances.append(instance.name)

            # Generate a title based on assertion results
            if not disabled_integrity_monitoring_instances:
                title = "All instances have Integrity Monitoring enabled"
            else:
                title = f"Instances with Integrity Monitoring disabled: {', '.join(disabled_integrity_monitoring_instances)}"

            # Raise an assertion error if any instance failed the assertion
            assert all([integrity_monitoring_enabled == assert_value for integrity_monitoring_enabled in [
                instance.shielded_instance_config.enable_integrity_monitoring if instance.shielded_instance_config and instance.shielded_instance_config.enable_integrity_monitoring else None
                for instance in instances]]), title

    '''
            ============
            Test Case 11
            ============
    '''
    @allure.story("Verify VM Provisioning Model for every Compute Engine VM Resource")
    @pytest.mark.parametrize("project_vm_instances", [(p["project_id"],) for p in config["projects"]], indirect=True)
    @pytest.mark.severity("Medium")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.smoke("Smoke")
    @allure.label("Suite", "Smoke")
    @allure.label("Severity", "Medium")
    def test_vm_provisioning_model(self, project_vm_instances):
        for project_id, instances in project_vm_instances:
            if not instances:
                continue

            wrong_provisioning_model_instances = []  # Instances with wrong VM provisioning model

            for instance in instances:
                test_case_name = f"VM Provisioning Model Test Case - {project_id}"
                allure.dynamic.title(test_case_name)

                assert_value = next(
                    p["vm_provisioning_model_assertion"] for p in config["projects"] if p["project_id"] == project_id)
                provisioning_model = instance.scheduling.provisioning_model if instance.scheduling else None

                assert_result = provisioning_model == assert_value

                with allure.step(
                        f"Check VM Provisioning Model for VM instance {instance.name} in project {project_id}"):
                    if assert_result:
                        allure.dynamic.label("result", "passed")
                        print(
                            f"Correct VM Provisioning Model \"{provisioning_model}\" for VM instance {instance.name} in project {project_id}")
                    else:
                        allure.dynamic.label("result", "failed")
                        print(
                            f"Wrong VM Provisioning Model \"{provisioning_model}\" for VM instance {instance.name} in project {project_id}")
                        wrong_provisioning_model_instances.append(instance.name)

            # Generate a title based on assertion results
            if not wrong_provisioning_model_instances:
                title = "All instances have correct VM Provisioning Model"
            else:
                title = f"Instances with wrong VM Provisioning Model: {', '.join(wrong_provisioning_model_instances)}"

            # Raise an assertion error if any instance failed the assertion
            assert all([provisioning_model == assert_value for provisioning_model in
                        [instance.scheduling.provisioning_model if instance.scheduling else None for
                         instance in instances]]), title

    '''
            ============
            Test Case 12
            ============
    '''
    @allure.story("Verify On-Host Maintenance for every Compute Engine VM Resource")
    @pytest.mark.parametrize("project_vm_instances", [(p["project_id"],) for p in config["projects"]], indirect=True)
    @pytest.mark.severity("Medium")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.smoke("Smoke")
    @allure.label("Suite", "Smoke")
    @allure.label("Severity", "Medium")
    def test_on_host_maintenance(self, project_vm_instances):
        for project_id, instances in project_vm_instances:
            if not instances:
                continue

            incorrect_on_host_maintenance_instances = []  # Instances with incorrect On-Host Maintenance setting

            for instance in instances:
                test_case_name = f"On-Host Maintenance Test Case - {project_id}"
                allure.dynamic.title(test_case_name)

                assert_value = next(
                    p["on_host_maintenance_assertion"] for p in config["projects"] if p["project_id"] == project_id)
                on_host_maintenance = instance.scheduling.on_host_maintenance if instance.scheduling else None
                assert_result = on_host_maintenance == assert_value

                with allure.step(f"Check On-Host Maintenance for VM instance {instance.name} in project {project_id}"):
                    if assert_result:
                        allure.dynamic.label("result", "passed")
                        print(
                            f"Correct On-Host Maintenance setting \"{on_host_maintenance}\" for VM instance {instance.name} in project {project_id}")
                    else:
                        allure.dynamic.label("result", "failed")
                        print(
                            f"Incorrect On-Host Maintenance setting \"{on_host_maintenance}\" for VM instance {instance.name} in project {project_id}")
                        incorrect_on_host_maintenance_instances.append(instance.name)

            # Generate a title based on assertion results
            if not incorrect_on_host_maintenance_instances:
                title = "All instances have correct On-Host Maintenance setting"
            else:
                title = f"Instances with incorrect On-Host Maintenance setting: {', '.join(incorrect_on_host_maintenance_instances)}"

            # Raise an assertion error if any instance failed the assertion
            assert all([on_host_maintenance == assert_value for on_host_maintenance in
                        [instance.scheduling.on_host_maintenance if instance.scheduling else None for instance in
                         instances]]), title

    '''
            ============
            Test Case 13
            ============
    '''
    @allure.story("Verify Automatic Restart for every Compute Engine VM Resource")
    @pytest.mark.parametrize("project_vm_instances", [(p["project_id"],) for p in config["projects"]], indirect=True)
    @pytest.mark.severity("High")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.smoke("Smoke")
    @allure.label("Suite", "Smoke")
    @allure.label("Severity", "Medium")
    def test_automatic_restart(self, project_vm_instances):
        for project_id, instances in project_vm_instances:
            if not instances:
                continue

            disabled_automatic_restart_instances = []  # Instances with Automatic Restart disabled

            for instance in instances:
                test_case_name = f"Automatic Restart Test Case - {project_id}"
                allure.dynamic.title(test_case_name)

                assert_value = next(
                    p["automatic_restart_assertion"] for p in config["projects"] if p["project_id"] == project_id)
                automatic_restart = instance.scheduling.automatic_restart if instance.scheduling else None
                assert_result = automatic_restart == assert_value

                with allure.step(f"Check Automatic Restart for VM instance {instance.name} in project {project_id}"):
                    if assert_result:
                        allure.dynamic.label("result", "passed")
                        print(f"Automatic Restart is enabled for VM instance {instance.name} in project {project_id}")
                    else:
                        allure.dynamic.label("result", "failed")
                        print(f"Automatic Restart is disabled for VM instance {instance.name} in project {project_id}")
                        disabled_automatic_restart_instances.append(instance.name)

            # Generate a title based on assertion results
            if not disabled_automatic_restart_instances:
                title = "All instances have Automatic Restart enabled"
            else:
                title = f"Instances with Automatic Restart disabled: {', '.join(disabled_automatic_restart_instances)}"

            # Raise an assertion error if any instance failed the assertion
            assert all([automatic_restart == assert_value for automatic_restart in
                        [instance.scheduling.automatic_restart if instance.scheduling else None for instance in
                         instances]]), title


