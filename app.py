from flask import Flask, request, jsonify
from controller import PhysicalController

app = Flask(__name__)
controller = PhysicalController()

@app.route('/command', methods=['POST'])
def command():
    data = request.get_json()
    if not data or 'action' not in data:
        return jsonify({'error': 'missing action'}), 400
    action = data['action']
    if action == 'alert':
        controller.alert()
    elif action == 'track':
        controller.track()
    elif action == 'idle':
        controller.idle()
    else:
        return jsonify({'error': f'unknown action: {action}'}), 400
    return jsonify({'status': 'ok', 'action': action})

@app.route('/sensor', methods=['GET'])
def sensor():
    return jsonify({'status': 'ok'})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'online'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)