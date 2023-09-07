import json
from google.cloud import storage
from datetime import datetime

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super(DateTimeEncoder, self).default(obj)

def get_bucket_configuration(bucket_name):
    try:
        # Initialize a client
        storage_client = storage.Client()

        # Get a reference to the bucket
        buckets = storage_client.bucket(bucket_name)
        bucket = storage_client.get_bucket(bucket_name)
        print("====================")

        # Create a dictionary to store all configurations
        bucket_config = {
            "Created Date": bucket.time_created,
            "Location Type": bucket.location_type,
            "Location": bucket.location,
            "Default Storage Class": bucket.storage_class,
            "Requester Pays": bucket.requester_pays,
            "Tags": bucket.labels,
            "Labels": bucket.labels,
            "Cloud Console URL": f"https://console.cloud.google.com/storage/browser/{bucket_name}",
            "gsutil URI": f"gs://{bucket_name}",
            "Access Control": [],
            "Public Access Prevention": None,
            "Public Access Status": None,
            "Object Versioning": bucket.versioning_enabled,
            "Bucket Retention Policy": None,
            "Bucket Retention Period": bucket.retention_period,
            "Bucket Retention Policy Locked": bucket.retention_policy_locked,
            "Bucket Retention Policy Effective Time": bucket.retention_policy_effective_time,
            "Bucket Meta Generation": bucket.metageneration,
            "Bucket ID": bucket.id,
            "Bucket Data Locations": bucket.data_locations,
            "Encryption Type": None,
            "Lifecycle Rules": [],
            "bucket_iam_config": bucket.iam_configuration,
        }

        # Fetch and add Access Control information (if not UBLA-enabled)
        try:
            for acl in bucket.acl:
                bucket_config["Access Control"].append({
                    "Entity": acl.entity,
                    "Role": acl.role,
                })
        except Exception as acl_error:
            if "Cannot get legacy ACL" not in str(acl_error):
                raise acl_error

        # Fetch Bucket Retention Policy if it's set
        policy = bucket.get_iam_policy(requested_policy_version=3)  # Use policy version 3 for Bucket Retention Policy
        # print(f" {policy} | {policy.bindings} | {policy.authenticated_users()} | {policy.items()} | {policy.keys()}")
        for binding in policy.bindings:
            if binding["role"] == "roles/storage.legacyObjectOwner":
                # print(f"binding info: {binding}")
                retention_policy = binding.get("condition", {}).get("title")
                # print(f"retention Policy: {retention_policy}")
        #         if retention_policy:
        #             bucket_config["Bucket Retention Policy"] = retention_policy

        # Fetch Encryption Type if it's set
        default_kms_key_name = bucket.default_kms_key_name
        if default_kms_key_name:
            bucket_config["Encryption Type"] = "Customer-Supplied Encryption Key" if default_kms_key_name.startswith(
                "projects/") else "Google Managed Encryption Key"

        # Fetch Lifecycle Rules if they are set
        for rule in bucket.lifecycle_rules:
            bucket_config["Lifecycle Rules"].append({
                "Action": rule.action,
                "Condition": rule.condition,
            })


        # Check if Public Access Prevention is enabled (if not UBLA-enabled)
        iam_configuration = bucket.iam_configuration
        # print(f" Iam Configuration: {iam_configuration}")
        if iam_configuration:
            # Check if UBLA is enabled before accessing uniform_bucket_level_access
            if 'uniformBucketLevelAccess' in iam_configuration:
                uniform_bucket_level_access = iam_configuration['uniformBucketLevelAccess']
                bucket_config["Public Access Prevention"] = iam_configuration['publicAccessPrevention']

                if 'enabled' in uniform_bucket_level_access:
                    bucket_config["Public Access Status"] = uniform_bucket_level_access['enabled']

            # Convert the bucket configuration to JSON
            bucket_config_json = json.dumps(bucket_config, indent=2, cls=DateTimeEncoder)

            return bucket_config_json

    except Exception as e:
        return str(f"{e} | {e.__traceback__.tb_lineno}")


# Example usage:
bucket_name = 'qa-poc-bucket'
bucket_config = get_bucket_configuration(bucket_name)
print(bucket_config)
