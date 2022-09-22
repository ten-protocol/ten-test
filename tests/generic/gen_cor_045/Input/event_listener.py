from web3 import Web3
import asyncio, argparse, json


def handle_event(event):
    print(Web3.toJSON(event))


async def log_loop(event_filter, poll_interval):
    while True:
        for Stored in event_filter.get_new_entries():
            handle_event(Stored)
        await asyncio.sleep(poll_interval)


def main(contract):
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
    parser.add_argument("abi", type=int, help="Port of the spatial engine")
    args = parser.parse_args()

    web3 = Web3(Web3.HTTPProvider(args.url))
    with open(args.abi) as f:
        contract = web3.eth.contract(address=args.address, abi=json.load(f))

    main(contract)