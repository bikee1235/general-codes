from flask import Flask, jsonify, request
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        'message': 'Welcome to the Flask server!',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'OK',
        'service': 'Flask Server',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/users', methods=['GET'])
def get_users():
    users = ['John', 'Jane', 'Bob', 'Alice']
    return jsonify({'users': users})

@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'error': 'Name is required'}), 400
    
    return jsonify({
        'message': f'User {data["name"]} created successfully',
        'user': data
    }), 201

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5100)
