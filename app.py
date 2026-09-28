from flask import Flask, request, jsonify
import os, json

app = Flask(__name__)

# ========================================
# 🔴 কনফিগারেশন
# ========================================
API_KEY = os.environ.get("API_KEY", "myNewSecretKey_2024")
SMS_FILE = "latest_sms.json"


# ========================================
# 🏠 Home
# ========================================
@app.route("/", methods=["GET"])
def home():
    return "SMS Provider Server is Running ✅"


# ========================================
# 📩 SMS Receive Endpoint
# ========================================
@app.route("/push-sms", methods=["POST"])
def push_sms():
    try:
        key = request.headers.get("X-API-KEY", "")
        if key != API_KEY:
            return jsonify({"status": "error", "msg": "Unauthorized"}), 401

        data = request.get_json(force=True, silent=True) or {}
        full_sms = data.get("raw", "")

        if not full_sms:
            return jsonify({"status": "error", "msg": "Empty SMS"}), 400

        # Save latest SMS
        with open(SMS_FILE, "w") as f:
            json.dump({"sms": full_sms}, f, ensure_ascii=False)

        print("📩 SMS Received:", full_sms)

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500


# ========================================
# 📤 Get Latest SMS Endpoint
# ========================================
@app.route("/get-sms", methods=["GET"])
def get_sms():
    try:
        key = request.headers.get("X-API-KEY", "")
        if key != API_KEY:
            return jsonify({"status": "error", "msg": "Unauthorized"}), 401

        if not os.path.exists(SMS_FILE):
            return jsonify({"status": "empty"}), 200

        with open(SMS_FILE) as f:
            data = json.load(f)

        # Read once then delete
        os.remove(SMS_FILE)

        return jsonify({"status": "ok", "sms": data.get("sms", "")}), 200

    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500


# ========================================
# 🚀 Run
# ========================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
