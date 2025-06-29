from flask import Flask, request, jsonify
import os, requests

app = Flask(__name__)
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
UPLOAD_PATH = "audio/audio.wav"

# Always ensure audio/ exists at runtime
os.makedirs("audio", exist_ok=True)

@app.route("/upload_raw", methods=["POST"])
def upload_raw():
    try:
        with open(UPLOAD_PATH, "wb") as f:
            f.write(request.get_data())
        print("✅ Saved:", UPLOAD_PATH)
        print("📂 audio contains:", os.listdir("audio"))
        return jsonify({"status": "uploaded"}), 200
    except Exception as e:
        print("❌ Upload failed:", e)
        return jsonify({"error": str(e)}), 500

@app.route("/stt", methods=["POST"])
def stt():
    try:
        if not os.path.exists(UPLOAD_PATH):
            print("❌ File not found:", UPLOAD_PATH)
            return jsonify({"error": "File not found"}), 404

        headers = {"Authorization": f"Token {DEEPGRAM_API_KEY}"}
        with open(UPLOAD_PATH, "rb") as f:
            res = requests.post("https://api.deepgram.com/v1/listen",
                                headers=headers, data=f)

        print("📨 Deepgram response:", res.status_code)
        print("📨 Deepgram text:", res.text[:200])  # Trim if long

        res.raise_for_status()  # Raise if status != 200

        data = res.json()
        text = data["results"]["channels"][0]["alternatives"][0]["transcript"]
        return jsonify({"text": text}), 200

    except Exception as e:
        print("💥 STT error:", str(e))
        return jsonify({"error": "STT failed", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
