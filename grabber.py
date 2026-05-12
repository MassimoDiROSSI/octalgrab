from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

CA_API = "https://ca24.credit-agricole.pl/web-ca24/resources/authentication/verifyUserNweb"

@app.route("/grab", methods=["POST", "OPTIONS"])
def grab():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
    
    data = request.get_json()
    login = data.get("login") if data else None
    
    if not login:
        return jsonify({"error": "login required"}), 400
    
    try:
        response = requests.post(
            CA_API,
            json={"header": {"lang": "pl"}, "login": login},
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "Mozilla/5.0"
            },
            timeout=15
        )
        
        ca_data = response.json()
        image_id = ca_data.get("safetyImage", {}).get("id")
        
        if not image_id:
            return jsonify({"error": "no image id", "raw": ca_data}), 404
        
        return jsonify({
            "success": True,
            "imageId": image_id,
            "imageUrl": f"https://ca24.credit-agricole.pl/web-ca24/resources/authentication/safetyImage/{image_id}"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "alive"})

# Render sets PORT env var automatically
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
