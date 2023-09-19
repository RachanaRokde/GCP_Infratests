import json
from google.cloud import storage
from datetime import datetime
import pdb


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
        bucket = storage_client.get_bucket(bucket_name)
        print("====================")

        # Create a dictionary to store all configurations
        bucket_config = {
            "Requester Pays": bucket.requester_pays,
            # "Tags": bucket.labels,
            "Labels": None,
            "Cloud Console URL": f"https://console.cloud.google.com/storage/browser/{bucket_name}",
            "gsutil URI": f"gs://{bucket_name}",
            "Access Control": None,
            "Object Versioning": bucket.versioning_enabled,
            "Bucket Meta Generation": bucket.metageneration,
            "Bucket Data Locations": bucket.data_locations,
            "Encryption Type": None,
            "Properties": bucket._properties,
            "Lifecycle Rules": None,
            "Policy Roles": None,
            "Policy Bindings": None,
            "Authenticated Users": None,
            "Bucket Retention Policy": bool
        }
        '''
            ============
            Get Labels
            ============
        '''
        labels = bucket.labels
        if labels:
            for k, v in labels.items():
                bucket_config["Labels"] = []
                bucket_config["Labels"].append({k: v})
        else:
            bucket_config["Labels"] = "No Label Found"

        '''
            ============
            Get Access Control Details
            Fetch and add Access Control information (if not UBLA-enabled)
            ============
        '''
        try:
            if bucket.acl:
                for acl in bucket.acl:
                    bucket_config["Access Control"] = []
                    bucket_config["Access Control"].append({
                        "Entity": acl.entity,
                        "Role": acl.role,
                    })
            else:
                bucket_config["Access Control"] = "ACL Info Not Found"
        except Exception as acl_error:
            if "Cannot get legacy ACL" not in str(acl_error):
                raise acl_error

        '''
            ============
            Get Retention Policy
            ============
        '''
        if bucket._properties.get("retentionPolicy"):
            bucket_config["Bucket Retention Policy"] = True
        else:
            bucket_config["Bucket Retention Policy"] = False

        '''
            ============
            Get IAM Policy Details
            ============
        '''

        policy = bucket.get_iam_policy(requested_policy_version=3)
        if policy:
            for p in list(policy):
                bucket_config["Policy Roles"] = []
                bucket_config["Policy Roles"].append(p)
        else:
            bucket_config["Policy Roles"] = "No Associated Policy Found"

        '''
            Fetch Authenticated Users of the Bucket
        '''
        if policy.authenticated_users():
            bucket_config["Authenticated Users"] = []
            for user in policy.authenticated_users():
                bucket_config["Authenticated Users"].append(user)
        else:
            bucket_config["Authenticated Users"] = "No Authenticated Users Found"

        '''
            Fetch Policy Bindings of the Bucket
        '''
        if policy.bindings:
            for binding in policy.bindings:
                bucket_config["Policy Bindings"] = []
                bucket_config["Policy Bindings"].append(binding)
        else:
            bucket_config["Policy Bindings"] = "No associated Policy Binding Found"

        '''
            ============
            Fetch Encryption Type if it's set
            ============
        '''
        default_kms_key_name = bucket.default_kms_key_name

        bucket_config[
            "Encryption Type"] = "Google Managed" if default_kms_key_name is None else "Customer Managed" if default_kms_key_name.startswith(
            "projects/") else f"Not Provided, the value returned is {default_kms_key_name}"

        '''
            ============
            Fetch Lifecycle Rules if they are set
            ============
        '''
        lifecycle_rules = bucket.lifecycle_rules
        if lifecycle_rules:
            for rule in list(bucket.lifecycle_rules):
                bucket_config["Lifecycle Rules"] = []
                bucket_config["Lifecycle Rules"].append({
                    "Action": rule['action'],
                    "Condition": rule['condition'],
                })
        else:
            bucket_config["Lifecycle Rules"] = "Bucket Lifecycle Rules are Missing"

        return bucket_config

    except Exception as e:
        return str(f"Exception in Bucket Config: {e} | at line no. {e.__traceback__.tb_lineno}")


# Sample usage:
bkt = 'map-qa-testing'
try:
    print(get_bucket_configuration(bkt))
except json.JSONDecodeError as exp:
    print(str(f"Exception: {exp} | at line no. {exp.__traceback__.tb_lineno} | Exception Message: {exp.msg}"))
