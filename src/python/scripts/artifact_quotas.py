import requests, argparse

BASE_URL = "https://api.github.com"


def get_repos(org, token):
    headers = {"Authorization": f"token {token}"}
    repos = []
    page = 1
    while True:
        url = f"{BASE_URL}/orgs/{org}/repos?per_page=100&page={page}"
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        data = r.json()
        if not data:
            break
        repos.extend(data)
        page += 1
    return [repo["name"] for repo in repos]


def get_artifact_usage(owner, repo, token):
    headers = {"Authorization": f"token {token}"}
    total_size = 0
    page = 1
    while True:
        url = f"{BASE_URL}/repos/{owner}/{repo}/actions/artifacts?per_page=100&page={page}"
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        data = r.json()
        artifacts = data.get("artifacts", [])
        if not artifacts:
            break
        for artifact in artifacts:
            total_size += artifact["size_in_bytes"]
        page += 1
    return total_size


def main(org, token):
    repos = get_repos(org, token)
    usage = {}
    for repo in repos:
        size = get_artifact_usage(org, repo, token)
        if size > 0:
            usage[repo] = size

    sorted_usage = sorted(usage.items(), key=lambda x: x[1], reverse=True)
    for repo, size in sorted_usage:
        print(f"{repo}: {size/1024/1024:.2f} MB")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='artifacts_quota')
    parser.add_argument('-t', '--token', help='Github token')
    parser.add_argument('-o', '--organisation', help='Github organisation')
    args = parser.parse_args()
    main(args.organisation, args.token)
