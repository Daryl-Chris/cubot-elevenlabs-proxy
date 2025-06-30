from flask import Flask, request, jsonify
import os, requests

app = Flask(__name__)
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
UPLOAD_PATH = "audio/audio.wav"

# Ensure the audio folder exists
os.makedirs("audio", exist_ok=True)

@app.route("/upload_raw", methods=["POST"])
def upload_raw():
    try:
        with open(UPLOAD_PATH, "wb") as f:
            f.write(request.get_data())
        size = os.path.getsize(UPLOAD_PATH)
        print(f"✅ Saved: {UPLOAD_PATH} ({size} bytes)")
        return jsonify({"status": "uploaded"}), 200
    except Exception as e:
        print("❌ Upload failed:", e)
        return jsonify({"error": str(e)}), 500

@app.route("/stt", methods=["POST"])
def stt():
    try:
        if not os.path.exists(UPLOAD_PATH):
            return jsonify({"error": "File not found"}), 404

        size = os.path.getsize(UPLOAD_PATH)
        if size < 1000:
            return jsonify({"error": "File too small"}), 400

        headers = {
            "Authorization": f"Token {DEEPGRAM_API_KEY}",
            "Content-Type": "audio/wav"
        }

        with open(UPLOAD_PATH, "rb") as f:
            res = requests.post("https://api.deepgram.com/v1/listen", headers=headers, data=f)

        print("📨 Deepgram status:", res.status_code)
        print("📨 Deepgram response:", res.text[:300])
        res.raise_for_status()

        data = res.json()
        text = data["results"]["channels"][0]["alternatives"][0]["transcript"]
        return jsonify({"text": text}), 200

    except Exception as e:
        print("💥 STT error:", str(e))
        return jsonify({"error": "STT failed", "details": str(e)}), 500

@app.route("/debug", methods=["GET"])
def debug():
    try:
        if not os.path.exists(UPLOAD_PATH):
            return jsonify({"error": "File not found"}), 404
        size = os.path.getsize(UPLOAD_PATH)
        return jsonify({"status": "found", "size": size}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
