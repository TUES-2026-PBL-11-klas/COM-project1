from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/quizzes')
def quizzes():
    return jsonify({"message": "quiz service working"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)