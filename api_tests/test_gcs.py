import json
import allure
import pytest
import yaml
from google.cloud import storage
from api_tests.single_bucket_response import get_bucket_configuration, DateTimeEncoder

# Read configuration from the YAML file
with open("/Users/dpkprmr/PycharmProjects/Learning/GCP_Infratests/config/gcs_test_config.yaml", "r") as config_file:
    config = yaml.safe_load(config_file)

'''
    ====================
    Fixture to fetch GCS Buckets for each project and store them as class attributes
    ====================
'''


def fetch_project_gcs_buckets(project_id, zone):
    # Get the zone for the specific project from the configuration
    project = next((p for p in config["projects"] if p["project_id"] == project_id), None)
    if not project:
        raise ValueError(f"Project with project_id '{project_id}' not found.")

    zone = project.get("zone", None)
    if not zone:
        raise ValueError(f"Zone not specified for project with project_id '{project_id}' in the configuration YAML.")
    # Initialize the Google Cloud Storage client
    client = storage.Client(project=project_id)

    # List all GCS buckets in the project
    buckets = list(client.list_buckets())

    return project_id, buckets


def get_bucket_details(bucket_name):
    # if bucket_name == 'qa-poc-bucket':
    bucket_detail = get_bucket_configuration(bucket_name)
    return bucket_detail


@allure.feature("Google Cloud Storage")
class TestGCS:
    @pytest.fixture(scope="class")
    def project_gcs_buckets(self, request):
        buckets_list = []
        for project in config["projects"]:
            project_id = project["project_id"]
            zone = project.get("zone", None)
            if not zone:
                raise ValueError(
                    f"Zone not specified for project with project_id '{project_id}' in the configuration YAML.")

            buckets = fetch_project_gcs_buckets(project_id, zone)
            buckets_list.append(buckets)
        return buckets_list

    @allure.story("Verify labels are attached to every GCS Bucket Resource")
    @pytest.mark.parametrize("project_gcs_buckets", [(p["project_id"],) for p in config["projects"]], indirect=True)
    @pytest.mark.severity("Medium")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.smoke("Smoke")
    @allure.label("Suite", "Smoke")
    @allure.label("Severity", "Medium")
    def test_labels_attached(self, project_gcs_buckets):
        print(f"Project GCS Buckets: {project_gcs_buckets}")
        # for project_id, buckets in project_gcs_buckets:
        #     if not buckets:
        #         continue
        #
        #     missing_labels_buckets = []  # Buckets missing required labels
        #
        #     for bucket in buckets:
        #         test_case_name = f"Labels Test Case - {project_id}"
        #         allure.dynamic.title(test_case_name)
        #
        #         assert_value = next(p["labels_assertion"] for p in config["projects"] if p["project_id"] == project_id)
        #         labels = get_bucket_details(bucket)['Labels']
        #         label_value = labels != "No Label Found"
        #         assert_result = label_value == assert_value
        #
        #         with allure.step(f"Check Labels for GCS Bucket {bucket.name} in project {project_id}"):
        #             if assert_result:
        #                 allure.dynamic.label("result", "passed")
        #                 print(f"Labels found for GCS Bucket {bucket.name} in project {project_id}")
        #             else:
        #                 allure.dynamic.label("result", "failed")
        #                 print(f"No Labels found for GCS Bucket {bucket.name} in project {project_id}")
        #                 missing_labels_buckets.append(bucket.name)
        #
        #     # Generate a title based on assertion results
        #     if not missing_labels_buckets:
        #         title = "All buckets have required labels attached"
        #     else:
        #         title = f"Buckets missing required labels: {', '.join(missing_labels_buckets)}"
        #
        #     # Raise an assertion error if any bucket failed the assertion
        #     assert all([(labels != "No Label Found") == assert_value for labels in
        #                 [get_bucket_details(bucket)['Labels'] for bucket in buckets]]), title
