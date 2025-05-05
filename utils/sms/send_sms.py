from twilio.rest import Client

account_sid = ''
auth_token = ''
client = Client(account_sid, auth_token)

message = client.messages.create(
    body="This is the ship that made the Kessel Run in fourteen parsecs?",
    from_="",
    to="",
)

print(message.body)