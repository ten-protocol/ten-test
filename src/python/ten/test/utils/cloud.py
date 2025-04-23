import requests
from collections import namedtuple

CloudInfo = namedtuple("CloudInfo", ["cloud_name", "instance_name", "instance_location"])


def is_cloud_vm():
    """Return cloud info, or none if not running on a cloud provider. """
    cloud_info = is_alibaba_vm()
    if cloud_info is not None: return cloud_info
    cloud_info = is_azure_vm()
    if cloud_info is not None: return cloud_info
    return None


def is_alibaba_vm():
    metadata_url = "http://100.100.100.200/latest/meta-data/"
    try:
        resp = requests.get(metadata_url, timeout=2)
        if "instance-id" in resp.text:
            instance_location = requests.get(metadata_url + "region-id", timeout=1).text.strip()
            instance_name = requests.get(metadata_url + "instance/instance-name", timeout=1).text.strip()
            return CloudInfo("alibaba", instance_name, instance_location)
        else:
            return None
    except requests.exceptions.RequestException as e:
        return None


def is_azure_vm():
    metadata_url = "http://169.254.169.254/metadata/instance?api-version=2021-02-01"
    headers = {"Metadata": "true"}

    try:
        response = requests.get(metadata_url, headers=headers, timeout=2)
        if response.status_code == 200:
            cloud_metadata = response.json()
            instance_name = cloud_metadata['compute']['name']
            instance_location = cloud_metadata['compute']['location']
            return CloudInfo("azure", instance_name, instance_location)
        else:
            return None
    except requests.exceptions.RequestException as e:
        return None


if __name__=='__main__':
    clound_info = is_cloud_vm()
    if is_cloud_vm(): print(clound_info)