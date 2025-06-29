from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

# 1) Ensure audio/ exists on every start
os.makedirs("audio", exist_ok=True)

@app.route("/upload", methods=["POST"])
def upload_audio():
    # 2) Reject if no file field
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    audio = request.files["file"]
    save_folder = "audio"
    save_path = os.path.join(save_folder, "audio.wav")

    try:
        # 3) Save the incoming file
        audio.save(save_path)

        # 4) Debug output in logs
        app.logger.info(f"✅ Saved file to {save_path}")
        files = os.listdir(save_folder)
        app.logger.info(f"📂 audio/ contains: {files}")

        return jsonify({"status": "uploaded", "filename": "audio.wav"}), 200
    except Exception as e:
        app.logger.error(f"❌ Could not save file: {e}")
        return jsonify({"error": "Failed to save file", "details": str(e)}), 500

@app.route("/stt", methods=["POST"])
def stt_proxy():
    data = request.get_json() or {}
    filename = data.get("filename")
    if not filename:
        return jsonify({"error": "Missing filename"}), 400

    file_path = os.path.join("audio", filename)
    if not os.path.isfile(file_path):
        return jsonify({"error": f"File '{filename}' not found"}), 404

    # Forward to Deepgram
    headers = {"Authorization": f"Token {DEEPGRAM_API_KEY}"}
    with open(file_path, "rb") as f:
        resp = requests.post("https://api.deepgram.com/v1/listen", headers=headers, data=f)

    try:
        transcript = resp.json()["results"]["channels"][0]["alternatives"][0]["transcript"]
        return jsonify({"text": transcript}), 200
    except Exception as e:
        return jsonify({"error": "Deepgram parse error", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
