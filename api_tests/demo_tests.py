import allure
import pytest
import yaml
import json
from google.cloud import storage

# Read configuration from the YAML file
config_path = "/Users/dpkprmr/PycharmProjects/Learning/GCP_Infratests/config/gcs_test_config.yaml"
with open(config_path, "r") as config_file:
    config = yaml.safe_load(config_file)


# Fixture to fetch GCS Buckets for each project and store them as class attributes
def list_gcs_buckets(project_id):
    project = next((p for p in config["projects"] if p["project_id"] == project_id), None)
    if not project:
        raise ValueError(f"Project with project_id '{project_id}' not found in the configuration YAML.")

    zone = project.get("zone")
    if not zone:
        raise ValueError(f"Zone not specified for project with project_id '{project_id}' in the configuration YAML.")

    client = storage.Client(project=project_id)
    buckets = list(client.list_buckets())
    actual_buckets = []
    for bucket in buckets:
        bucket_name = str(bucket).replace("<Bucket: ", "").replace(">", "")
        actual_buckets.append(bucket_name)

    return {"project_id": project_id, "buckets": actual_buckets}


@allure.feature("Google Cloud Storage")
class TestGCS:

    @pytest.fixture(scope="class")
    def project_buckets_list(self):
        for project in config["projects"]:
            project_id = project["project_id"]
            zone = project.get("zone")
            if not zone:
                raise ValueError(
                    f"Zone not specified for project with project_id '{project_id}' in the configuration YAML.")

            buckets = list_gcs_buckets(project_id)
            # print(buckets)

            return buckets

    @allure.story("Verify tags are attached to every GCS Bucket")
    @pytest.mark.parametrize("project_buckets_list", [(p["project_id"],) for p in config["projects"]], indirect=True)
    @pytest.mark.severity("Medium")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.smoke("Smoke")
    @allure.label("Suite", "Smoke")
    @allure.label("Severity", "Medium")
    def test_tags_attached(self, project_buckets_list):
        # print(project_buckets_list)
        project_id = project_buckets_list.get("project_id")
        buckets = project_buckets_list.get("buckets")

        for bucket in buckets:  # write Key value notation and get the project ID and store it in a variable
            if not bucket:
                continue

            missing_tags_buckets = []  # Buckets missing required tags
            # client = storage.Client()
            # current_bucket = client.get_bucket(bucket)
            # test_case_name = f"Tags Test Case - {project_id} / {bucket}"
            # print(current_bucket.get_metadata())
            # print("============================")
            # bucket_metadata = current_bucket.get_metadata()
            # bucket_meta_json = json.dumps(bucket_metadata, indent=2)
            # print(f"Metadata Json: {bucket_meta_json}")
            # print(test_case_name)
            if bucket == "dp-multi-tenancy-poc-bkt":
                client = storage.Client()
                current_bucket = client.get_bucket(bucket)
                print(current_bucket)
                bucket_config = {
                    "Name": current_bucket.name,
                    "Labels": current_bucket.labels,
                    "ID": current_bucket.id,
                    "ACL": current_bucket.acl,
                    "Autoclass_Enabled": current_bucket.autoclass_enabled,
                    "Data_Locations": current_bucket.data_locations,
                    "Versioning_Enabled": current_bucket.versioning_enabled,
                    "CORS": current_bucket.cors,
                    "Default_KMS_Key_Name": current_bucket.default_kms_key_name,
                    "Etag": current_bucket.etag,
                    "IAM_Configs": current_bucket.iam_configuration,
                    "Lifecycle_Rules": current_bucket.lifecycle_rules,
                    "Bucket_Location": current_bucket.location,
                    "Location_Type": current_bucket.location_type,
                    "MetaGeneration": current_bucket.metageneration,
                    "Autoclass_Toggle_Time": current_bucket.autoclass_toggle_time,
                    "default_object_acl": current_bucket.default_object_acl,
                    "Owner": current_bucket.owner,
                    "Path": current_bucket.path,
                    "Project_Number": current_bucket.project_number,
                    "Requester_Pays": current_bucket.requester_pays,
                    "Retention_Period": current_bucket.retention_period,
                    "Retention_Policy_Effective_Time": current_bucket.retention_policy_effective_time,
                    "Retention_Policy_Locked": current_bucket.retention_policy_locked,
                    "RPO": current_bucket.rpo,
                    "Self_Link": current_bucket.self_link,
                    "Storage_Class": current_bucket.storage_class,
                    "Creation_Time": current_bucket.time_created,
                    "User_Project": current_bucket.user_project,
                    "DefaultEvent_Based_Hold": current_bucket.default_event_based_hold,
                    "Logging": current_bucket.get_logging(),
                }
                print(bucket_config)

                return bucket_config

                # current_bucket = client.get_bucket(bucket)
                # test_case_name = f"Tags Test Case - {project_id} / {bucket}"
                # print(current_bucket.get_metadata())
                # print("============================")
                # bucket_metadata = current_bucket.get_iam_configuration()
                # # bucket_meta_json = json.dumps(bucket_metadata, indent=2)
                # print(f"Metadata Json: {bucket_metadata}")
            # allure.dynamic.title(test_case_name)
            #
            # assert_value = next(p["tags_assertion"] for p in config["projects"] if p["project_id"] == project_id)
            # tags = bucket.labels if bucket.labels else None
            # assert_result = (tags is not None) == assert_value
            #
            # with allure.step(f"Check Tags for GCS bucket {bucket} in project {project_id}"):
            #     if assert_result:
            #         allure.dynamic.label("result", "passed")
            #         print(f"Tags found for GCS bucket {bucket} in project {project_id}")
            #     else:
            #         allure.dynamic.label("result", "failed")
            #         print(f"No Tags found for GCS bucket {bucket} in project {project_id}")
            #         missing_tags_buckets.append(bucket)

            # Generate a title based on assertion results
            # if not missing_tags_buckets:
            #     title = "All buckets have required tags attached"
            # else:
            #     title = f"Buckets missing required tags: {', '.join(missing_tags_buckets)}"
            #
            # # Raise an assertion error if any bucket failed the assertion
            # assert all([(tags is not None) == assert_value for tags in
            #             [instance.labels if instance.labels else None for instance in buckets]]), title
