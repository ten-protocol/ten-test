from web3 import Web3
import requests, asyncio
import argparse, json, sys
from eth_account.messages import encode_defunct


def generate_viewing_key(web3, url, private_key):
    sys.stdout.write('Generating viewing key for %s\n' % private_key)
    sys.stdout.flush()

    account = web3.eth.account.privateKeyToAccount(private_key)

    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    data = {"address": account.address}
    response = requests.post('%s/generateviewingkey/' % url, data=json.dumps(data), headers=headers)

    signed_msg = web3.eth.account.sign_message(encode_defunct(text='vk' + response.text), private_key=private_key)
    data = {"signature": signed_msg.signature.hex(), "address": account.address}
    requests.post('%s/submitviewingkey/' % url, data=json.dumps(data), headers=headers)


def handle_event(event):
    sys.stdout.write('%s\n' % Web3.toJSON(event))
    sys.stdout.flush()


async def log_loop(event_filter, poll_interval):
    while True:
        for Stored in event_filter.get_new_entries():
            handle_event(Stored)
        await asyncio.sleep(poll_interval)


def main(contract):
    sys.stdout.write('Starting to run the event loop\n')
    sys.stdout.flush()
    event_filter = contract.events.Stored.createFilter(fromBlock='latest')
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(
            asyncio.gather(
                log_loop(event_filter, 2)))
    finally:
        loop.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='event_listener')
    parser.add_argument("url", help="Directory containing the API")
    parser.add_argument("address", help="Address of the spatial engine")
    parser.add_argument("abi", help="Port of the spatial engine")
    parser.add_argument("--pk", help="Private key to register for a viewing key (obscuro only)")
    args = parser.parse_args()

    sys.stdout.write('URL: %s\n' % args.url)
    sys.stdout.write('ADR: %s\n' % args.address)
    sys.stdout.write('ABI: %s\n' % args.abi)
    sys.stdout.flush()

    web3 = Web3(Web3.HTTPProvider(args.url))
    if args.pk: generate_viewing_key(web3, args.url, args.pk)
    with open(args.abi) as f:
        contract = web3.eth.contract(address=args.address, abi=json.load(f))

    main(contract)
