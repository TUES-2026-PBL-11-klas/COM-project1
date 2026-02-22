from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/users')
def users():
    return jsonify({"message": "users service working"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)