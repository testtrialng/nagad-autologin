from flask import Flask, request, jsonify
import os

app = Flask(__name__)

API_KEY = os.environ.get("API_KEY", "mySecretKey_12345")

# App 2 এর জন্য শেষ SMS
latest_sms = {"raw": "", "id": 0}


@app.route("/", methods=["GET"])
def home():
    return "Nagad AutoLogin Server ✅"


# ========================================
# 📩 App 1 → SMS পাঠাবে এখানে
# সার্ভার সাথে সাথে App 2 এর জন্য রাখবে
# ========================================
@app.route("/push-sms", methods=["POST"])
def push_sms():
    key = request.headers.get("X-API-KEY", "")
    if key != API_KEY:
        return jsonify({"status": "error"}), 401

    data = request.get_json(force=True, silent=True) or {}
    full_sms = data.get("raw", "")

    if not full_sms:
        return jsonify({"status": "error"}), 400

    # সাথে সাথে App 2 এর জন্য রেখে দাও
    latest_sms["raw"] = full_sms
    latest_sms["id"] += 1

    print("📩 SMS Saved for App 2:", full_sms)

    # App 1 কে শুধু "ok" জানাও (দরকার নেই, তবুও)
    return jsonify({"status": "ok"}), 200


# ========================================
# 📤 App 2 → এখান থেকে SMS নেবে
# ========================================
@app.route("/get-sms", methods=["GET"])
def get_sms():
    key = request.headers.get("X-API-KEY", "")
    if key != API_KEY:
        return jsonify({"status": "error"}), 401

    last_id = request.args.get("last_id", "0")
    try:
        last_id = int(last_id)
    except:
        last_id = 0

    # নতুন SMS থাকলে সাথে সাথে দাও
    if latest_sms["id"] > last_id and latest_sms["raw"]:
        return jsonify({
            "status": "ok",
            "id": latest_sms["id"],
            "sms": latest_sms["raw"]
        }), 200

    # নতুন SMS নেই
    return jsonify({"status": "empty", "id": latest_sms["id"]}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
