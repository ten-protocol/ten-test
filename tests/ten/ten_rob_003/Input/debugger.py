import logging, random, time
import argparse, sys, requests
from web3 import Web3

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', stream=sys.stdout, level=logging.INFO)

msg_id = 0


def get_debug_event_log_relevancy(url, address, signature, from_block, to_block):
    global msg_id
    msg_id = msg_id + 1
    data = {"jsonrpc": "2.0",
            "method": "debug_eventLogRelevancy",
            "params": [{
                "fromBlock":from_block,
                "toBlock":to_block,
                "address": address,
                "topics": [signature]
            }],
            "id": msg_id }
    response = requests.post(url, json=data)
    if 'result' in response.json(): return response.json()['result']
    elif 'error' in response.json(): logging.info(response.json()['error']['message'])
    return None


def run(url, web3, address):
    while True:
        choice = random.randrange(4)
        target = None
        if choice == 0: target = 'SimpleEvent(uint256,string,address)'
        if choice == 1: target = 'ArrayEvent(uint256,uint256[],string[])'
        if choice == 2: target = 'StructEvent(uint256,User)'
        if choice == 3: target = 'MappingEvent(uint256,address[],uint256[])'

        block_num = web3.eth.get_block_number()
        start_block_num = (block_num - 5) if block_num > 5 else 0
        response = get_debug_event_log_relevancy( url=url, address=address,
                                                  signature=web3.keccak(text=target).hex(),
                                                  from_block=hex(start_block_num-5), to_block='latest')
        logging.info('Num events: %d' % len(response))
        time.sleep(0.25)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='debug_events')
    parser.add_argument('-u', '--network_http', help='Connection URL')
    parser.add_argument('-a', '--contract_address', help='Address of the contract')
    args = parser.parse_args()

    web3 = Web3(Web3.HTTPProvider(args.network_http))
    logging.info(args.network_http)
    logging.info('Starting debug_events')
    run(args.network_http, web3, args.contract_address)


