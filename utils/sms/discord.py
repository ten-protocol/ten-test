import requests, argparse

webhook_url = 'https://discord.com/api/webhooks/%s/%s'
red = 15158332
green = 3066993

embed = {
    "title": "🚨 Health Checks Failed 🚨",
    "description": "CODE RED - The E2E health checks have failed!  :scream:",
    "color": red,
    "fields": [
        {"name": "Team status", "value": "Panicking", "inline": True},
        {"name": "On-call support", "value": "<@814873419207409685>", "inline": True},
        {"name": "Workflow", "value": "[health_check_uat](https://github.com/ten-protocol/ten-test/actions/workflows/health_check_uat.yml)", "inline": False},

    ],
    "footer": {"text": "E2E Monitoring"},
}

data = {
    "content":  "Please investigate <@814873419207409685>",
    "username": "E2E Health Checks",
    "embeds": [embed]
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='web hook')
    parser.add_argument('--id', help='The discord webhook id', required=True)
    parser.add_argument('--token', help='The discord webhook token', required=True)
    args = parser.parse_args()

    response = requests.post(webhook_url%(args.id, args.token), json=data)

    if response.status_code == 204:
        print("Embed sent successfully!")
    else:
        print(f"Failed to send embed: {response.status_code}, {response.text}")
