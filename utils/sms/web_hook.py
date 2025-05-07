import argparse
from flask import Flask, request, jsonify

app = Flask(__name__)
api_token = None


@app.route('/webhook', methods=['POST'])
def webhook():
    auth_header = request.headers.get('Authorization')

    if not auth_header or auth_header != f"Bearer {api_token}":
        return jsonify({'status': 'unauthorized', 'message': 'Invalid token'}), 401

    data = request.get_json()
    print("Received webhook data:", data)

    return jsonify({'status': 'success', 'message': 'Webhook received'}), 200


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='web hook')
    parser.add_argument('--port', help='The port to run the server on', required=True)
    parser.add_argument('--token', help='The account authentication token', required=True)
    args = parser.parse_args()

    api_token = args.token
    app.run(port=int(args.port))
