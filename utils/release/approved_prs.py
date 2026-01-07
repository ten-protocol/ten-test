import os, requests

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OWNER = "ten-protocol"
REPO = "go-ten"

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
}

def get_pull_requests():
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/pulls"
    params = {
        "state": "open",
        "per_page": 100
    }
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json()

def is_pr_approved(pr_number):
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/pulls/{pr_number}/reviews"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()

    reviews = response.json()
    for review in reviews:
        if review["state"] == "APPROVED":
            return True
    return False

def main():
    prs = get_pull_requests()
    approved_prs = []

    for pr in prs:
        if is_pr_approved(pr["number"]):
            approved_prs.append(pr)

    print("Approved PRs:\n")
    for pr in approved_prs:
        print(f"- #{pr['number']} {pr['title']} ({pr['html_url']})")

if __name__ == "__main__":
    main()
