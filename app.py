from flask import Flask, request, jsonify
import requests, os

app = Flask(__name__)
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

# ensure folder exists at runtime
os.makedirs("audio", exist_ok=True)

@app.route("/upload_raw", methods=["POST"])
def upload_raw():
    data = request.get_data()
    save_path = os.path.join("audio", "audio.wav")
    try:
        with open(save_path, "wb") as f:
            f.write(data)
        app.logger.info(f"✅ Saved raw upload to {save_path}")
        return jsonify({"status": "uploaded"}), 200
    except Exception as e:
        app.logger.error(f"❌ Save failed: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/stt", methods=["POST"])
def stt_proxy():
    body = request.get_json() or {}
    fn = body.get("filename")
    if not fn:
        return jsonify({"error": "missing filename"}), 400

    path = os.path.join("audio", fn)
    if not os.path.isfile(path):
        return jsonify({"error": f"'{fn}' not found"}), 404

    headers = {"Authorization": f"Token {DEEPGRAM_API_KEY}"}
    with open(path, "rb") as wav:
        dg = requests.post("https://api.deepgram.com/v1/listen",
                           headers=headers, data=wav)
    try:
        txt = dg.json()["results"]["channels"][0]["alternatives"][0]["transcript"]
        return jsonify({"text": txt}), 200
    except Exception as e:
        return jsonify({"error": "parse_failed", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
