import argparse
from twilio.rest import Client


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='websocket proxy.')
    parser.add_argument('--account', help='The twilio account SID', required=True)
    parser.add_argument('--token', help='The account authentication token', required=True)
    parser.add_argument('--fr', help='The phone number to send from', required=True)
    parser.add_argument('--to', help='The phone number to send to', required=True)
    args = parser.parse_args()

    client = Client(args.account, args.token)

    message = client.messages.create(
        body = "This is the ship that made the Kessel Run in fourteen parsecs?",
        from_ = args.fr,
        to = args.to,
    )

    print(message.body)