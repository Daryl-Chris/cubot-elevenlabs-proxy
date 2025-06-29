from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

@app.route("/upload", methods=["POST"])
def upload_audio():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    audio = request.files["file"]
    save_path = os.path.join("audio", "audio.wav")
    audio.save(save_path)

    return jsonify({"status": "uploaded", "filename": "audio.wav"}), 200

@app.route("/stt", methods=["POST"])
def stt_proxy():
    data = request.get_json()
    filename = data.get("filename")

    if not filename:
        return jsonify({"error": "Missing filename"}), 400

    file_path = os.path.join("audio", filename)
    if not os.path.exists(file_path):
        return jsonify({"error": f"File '{filename}' not found"}), 404

    headers = {
        "Authorization": f"Token {DEEPGRAM_API_KEY}"
    }

    with open(file_path, "rb") as audio:
        response = requests.post(
            "https://api.deepgram.com/v1/listen",
            headers=headers,
            data=audio
        )

    try:
        text = response.json()["results"]["channels"][0]["alternatives"][0]["transcript"]
        return jsonify({ "text": text })
    except Exception as e:
        return jsonify({"error": "Failed to parse Deepgram response", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
