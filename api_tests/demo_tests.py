import allure
import pytest
import yaml
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
                raise ValueError(f"Zone not specified for project with project_id '{project_id}' in the configuration YAML.")

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
        for project_id, buckets in project_buckets_list.items():
            # print(f"{project_id} | {buckets}")
            if not buckets:
                continue

            missing_tags_buckets = []  # Buckets missing required tags

            print(f"buckets: {buckets}")
            for bucket in buckets[1]:
                print(f"bucket: {bucket}")
                continue
            #     test_case_name = f"Tags Test Case - {project_id}/{bucket.name}"
            #     allure.dynamic.title(test_case_name)
            #
            #     assert_value = next(p["tags_assertion"] for p in config["projects"] if p["project_id"] == project_id)
            #     tags = bucket.labels if bucket.labels else None
            #     assert_result = (tags is not None) == assert_value
            #
            #     with allure.step(f"Check Tags for GCS bucket {bucket.name} in project {project_id}"):
            #         if assert_result:
            #             allure.dynamic.label("result", "passed")
            #             print(f"Tags found for GCS bucket {bucket.name} in project {project_id}")
            #         else:
            #             allure.dynamic.label("result", "failed")
            #             print(f"No Tags found for GCS bucket {bucket.name} in project {project_id}")
            #             missing_tags_buckets.append(bucket.name)
            #
            # # Generate a title based on assertion results
            # if not missing_tags_buckets:
            #     title = "All buckets have required tags attached"
            # else:
            #     title = f"Buckets missing required tags: {', '.join(missing_tags_buckets)}"
            #
            # # Raise an assertion error if any bucket failed the assertion
            # assert all([(tags is not None) == assert_value for tags in
            #             [instance.labels if instance.labels else None for instance in buckets]]), title

