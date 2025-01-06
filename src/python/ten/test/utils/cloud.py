import requests

def is_azure_vm():
    metadata_url = "http://169.254.169.254/metadata/instance?api-version=2021-02-01"
    headers = {"Metadata": "true"}

    try:
        response = requests.get(metadata_url, headers=headers, timeout=3)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except requests.exceptions.RequestException as e:
        return None
