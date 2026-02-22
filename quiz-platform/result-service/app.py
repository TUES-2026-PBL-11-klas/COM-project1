from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/results')
def results():
    return jsonify({"message": "result service working"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)