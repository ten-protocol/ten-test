import json, logging, random, time
import argparse, sys, requests

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', stream=sys.stdout, level=logging.INFO)

msg_id = 0


def json_hex_to_obj(hex_str):
    if hex_str.startswith('0x'): hex_str = hex_str[2:]
    byte_str = bytes.fromhex(hex_str)
    json_str = byte_str.decode('utf-8')
    return json.loads(json_str)


def split_into_segments(total, page_size):
    result = []
    start = 0
    while total > 0:
        if total >= page_size:
            result.append((start, page_size))
            total -= page_size
            start += page_size
        else:
            result.append((start, total))
            break
    return result


def size_personal_transactions(url, address, show_public, show_synthetic):
    return get_personal_transactions(url, address, show_public, show_synthetic, 0, 1)['Total']


def get_personal_transactions(url, address, show_public, show_synthetic, offset, size):
    global msg_id
    msg_id = msg_id + 1
    payload = {"address": address, "pagination": {"offset": offset, "size": size},
               "showAllPublicTxs": show_public, "showSyntheticTxs": show_synthetic}
    data = {"jsonrpc": "2.0",
            "method": "eth_getStorageAt",
            "params": ["0x0000000000000000000000000000000000000002",
                       json.dumps(payload), None], "id": msg_id }

    response = requests.post(url, json=data)
    if 'result' in response.json(): return json_hex_to_obj(response.json()['result'])
    elif 'error' in response.json(): logging.info(response.json()['error']['message'])
    return None


def run(url, address):
    while True:
        choice = random.randrange(4)
        show_public = None
        show_synthetic = None
        if choice == 0:
            show_public = True
            show_synthetic = True
        if choice == 1:
            show_public = True
            show_synthetic = False
        if choice == 2:
            show_public = False
            show_synthetic = False
        if choice == 3:
            show_public = False
            show_synthetic = True

        total = size_personal_transactions(url, address, show_public, show_synthetic)
        pages = split_into_segments(total, 50)
        logging.info('Requesting offset %d and size %d (total is %d)', pages[-1][0], pages[-1][1], total)
        logging.info('Request has show public %s and show synthetic %s', show_public, show_synthetic)
        txs = get_personal_transactions(url, address, show_public, show_synthetic, pages[-1][0], pages[-1][1])
        logging.info('Returned set has size %s', len(txs))
        time.sleep(2.0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='lister')
    parser.add_argument('-u', '--network_http', help='Connection URL')
    parser.add_argument('-a', '--address', help='Address of user account')
    args = parser.parse_args()

    logging.info(args.network_http)
    logging.info('Starting listing of personal transactions')
    run(args.network_http, args.contract_address)


