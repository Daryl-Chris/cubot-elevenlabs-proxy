from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")

@app.route("/stt", methods=["POST"])
def stt_proxy():
    data = request.get_json()
    filename = data.get("filename")

    if not filename:
        return jsonify({"error": "Missing filename"}), 400

    file_path = os.path.join("audio", filename)
    if not os.path.exists(file_path):
        return jsonify({"error": f"File '{filename}' not found"}), 404

    files = {
        "file": ("audio.wav", open(file_path, "rb"), "audio/wav")
    }

    payload = {
        "model_id": "scribe_v1",
        "tag_audio_events": "true"
    }

    try:
        response = requests.post(
            "https://api.elevenlabs.io/v1/speech-to-text",
            headers={
                "xi-api-key": ELEVEN_API_KEY
            },
            files=files,
            data=payload
        )

        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
