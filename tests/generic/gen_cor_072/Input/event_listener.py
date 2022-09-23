from web3 import Web3
import logging
import requests, asyncio
import argparse, json, sys
from eth_account.messages import encode_defunct

logging.basicConfig(format='%(asctime)s %(message)s', stream=sys.stdout, level=logging.INFO)


def generate_viewing_key(web3, url, private_key):
    logging.info('Generating viewing key for %s' % private_key)

    account = web3.eth.account.privateKeyToAccount(private_key)

    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    data = {"address": account.address}
    response = requests.post('%s/generateviewingkey/' % url, data=json.dumps(data), headers=headers)

    signed_msg = web3.eth.account.sign_message(encode_defunct(text='vk' + response.text), private_key=private_key)
    data = {"signature": signed_msg.signature.hex(), "address": account.address}
    requests.post('%s/submitviewingkey/' % url, data=json.dumps(data), headers=headers)


async def log_loop(event_filter, poll_interval):
    while True:
        for event in event_filter.get_new_entries():
            logging.info(Web3.toJSON(event))
        await asyncio.sleep(poll_interval)


def main(contract):
    logging.info('Starting to run the event loop')
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
    parser.add_argument("url", help="Connection URL")
    parser.add_argument("address", help="Address of the contract")
    parser.add_argument("abi", help="Abi of the contract")
    parser.add_argument("--pk", help="Private key to register for a viewing key (obscuro only)")
    args = parser.parse_args()

    logging.info('URL: %s' % args.url)
    logging.info('ADR: %s' % args.address)
    logging.info('ABI: %s' % args.abi)

    web3 = Web3(Web3.HTTPProvider(args.url))
    if args.pk: generate_viewing_key(web3, args.url, args.pk)
    with open(args.abi) as f:
        contract = web3.eth.contract(address=args.address, abi=json.load(f))

    main(contract)
