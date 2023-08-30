import allure
import pytest
import yaml
from google.cloud import storage

# Read configuration from the YAML file
with open("/Users/dpkprmr/PycharmProjects/Learning/GCP_Infratests/config/gcs_test_config.yaml", "r") as config_file:
    config = yaml.safe_load(config_file)


# Fixture to fetch GCS Buckets for each project and store them as class attributes

def list_gcs_buckets(project_id):
    # Get the zone for the specific project from the configuration
    project = next((p for p in config["projects"] if p["project_id"] == project_id), None)
    if not project:
        raise ValueError(f"Project with project_id '{project_id}' not found in the configuration YAML.")

    zone = project.get("zone", None)
    if not zone:
        raise ValueError(f"Zone not specified for project with project_id '{project_id}' in the configuration YAML.")
    # Initialize the Google Cloud Storage client
    client = storage.Client(project=project_id)

    # List all GCS buckets in the project
    buckets = list(client.list_buckets())

    return {"project_id": project_id, "buckets": buckets}


# list_gcs_buckets()