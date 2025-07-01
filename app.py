from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

UPLOAD_FILE = "audio.wav"
DG_KEY = os.getenv("DEEPGRAM_API_KEY")

@app.route("/upload_raw", methods=["POST"])
def upload_raw():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "Missing file"}), 400

    file.save(UPLOAD_FILE)
    print(f"✅ Received upload: {UPLOAD_FILE}, {os.path.getsize(UPLOAD_FILE)} bytes")
    return jsonify({"status": "uploaded"}), 200

@app.route("/stt", methods=["POST"])
def stt():
    if not os.path.exists(UPLOAD_FILE):
        return jsonify({"error": "audio.wav not found"}), 404

    with open(UPLOAD_FILE, "rb") as f:
        headers = {
            "Authorization": f"Token {DG_KEY}",
            "Content-Type": "audio/wav"
        }
        r = requests.post("https://api.deepgram.com/v1/listen", headers=headers, data=f)

    print("📨 Deepgram status:", r.status_code)
    if r.status_code != 200:
        return jsonify({"error": f"Deepgram failed", "details": r.text}), r.status_code

    data = r.json()
    transcript = data.get("results", {}).get("channels", [{}])[0].get("alternatives", [{}])[0].get("transcript", "")
    print("🧠 Transcript:", transcript)
    return jsonify({"text": transcript or "[empty]"}), 200

@app.route("/debug", methods=["GET"])
def debug():
    if not os.path.exists(UPLOAD_FILE):
        return jsonify({"status": "missing"})
    size = os.path.getsize(UPLOAD_FILE)
    return jsonify({"status": "found", "size": size})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
