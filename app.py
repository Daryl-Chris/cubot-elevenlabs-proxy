from flask import Flask, request, jsonify
import os, requests

app = Flask(__name__)
UPLOAD_PATH = "audio/audio.wav"
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
os.makedirs("audio", exist_ok=True)

@app.route("/upload_raw", methods=["POST"])
def upload_raw():
    try:
        file = request.files.get("file")
        if not file:
            return jsonify({"error": "No file part"}), 400

        file.save(UPLOAD_PATH)
        size = os.path.getsize(UPLOAD_PATH)
        print(f"✅ Uploaded: {UPLOAD_PATH} ({size} bytes)")
        return jsonify({"status": "uploaded", "size": size}), 200

    except Exception as e:
        print("❌ Upload error:", e)
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
        print("📨 Response:", res.text[:300])
        res.raise_for_status()

        text = res.json()["results"]["channels"][0]["alternatives"][0].get("transcript", "")
        print("🧠 Returning:", {"text": text})
        return jsonify({"text": text}), 200

    except Exception as e:
        print("💥 STT error:", e)
        return jsonify({"error": "STT failed", "details": str(e)}), 500

@app.route("/debug", methods=["GET"])
def debug():
    if not os.path.exists(UPLOAD_PATH):
        return jsonify({"status": "missing"})
    return jsonify({"status": "found", "size": os.path.getsize(UPLOAD_PATH)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
