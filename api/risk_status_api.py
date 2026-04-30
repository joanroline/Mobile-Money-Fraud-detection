# Imports
 
from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
import joblib
import os


# App setup and file loading
app = Flask(__name__)
CORS(app)

# Build paths relative to this file's location
# This means the API works regardless of which folder you run it from
BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
REGISTRY_PATH = os.path.join(BASE_DIR, '..', 'models', 'risk_registry.csv')
MODEL_PATH    = os.path.join(BASE_DIR, '..', 'models', 'random_forest.pkl')
FEATURES_PATH = os.path.join(BASE_DIR, '..', 'models', 'feature_cols.pkl')

# Load everything once when the server starts (not on every request)
print("Loading risk registry...")
registry = pd.read_csv(REGISTRY_PATH)
registry['DEST_MOBILE'] = registry['DEST_MOBILE'].astype(str).str.strip()
print(f"  {len(registry):,} accounts loaded")

print("Loading model...")
model        = joblib.load(MODEL_PATH)
feature_cols = joblib.load(FEATURES_PATH)
print("  Model ready")

#Phone number Lookup Function
def lookup_account(phone_number):
    """
    Search the risk registry for a phone number.
    Tries exact match first, then suffix match to handle
    variations like '221771234001' vs '771234001'.
    Returns the row as a dict, or None if not found.
    """
    # Clean the input — remove spaces, +, dashes
    phone = str(phone_number).strip().replace(' ', '').replace('+', '').replace('-', '')

    # Try exact match first
    match = registry[registry['DEST_MOBILE'] == phone]
    if not match.empty:
        return match.iloc[0].to_dict()

    # Try suffix match — handles country code variations
    for _, row in registry.iterrows():
        stored = str(row['DEST_MOBILE'])
        if phone.endswith(stored) or stored.endswith(phone):
            return row.to_dict()

    return None

# Build Response function
def build_response(account, phone_number):
    is_high_risk  = account['risk_status'] == 'HIGH_RISK'
    # Registry already stores correct confidence scores
    # HIGH RISK = probability of fraud, LOW RISK = probability of being safe
    confidence = round(float(account['confidence_score']), 4)
    victim_count  = int(account['victim_count'])
    total_amount  = int(account['total_amount'])
    device_count  = int(account['device_count'])

    if is_high_risk:
        flag_reason        = (
            f"Account linked to {victim_count} unique victim(s) "
            f"with CFA {total_amount:,} total in fraudulent transfers "
            f"across {device_count} device(s)."
        )
        recommended_action = "BLOCK_AND_WARN"
    else:
        flag_reason        = "No fraudulent activity detected for this account."
        recommended_action = "ALLOW"

    return {
        "phone_number":       phone_number,
        "account_name":       str(account.get('dest_name', 'Unknown')),
        "status":             account['risk_status'],     # HIGH_RISK or LOW_RISK
        "confidence_score":   confidence,                 # 0.0 to 1.0
        "flag_reason":        flag_reason,                # human-readable explanation
        "recommended_action": recommended_action,         # BLOCK_AND_WARN or ALLOW
        "account_stats": {
            "victim_count":  victim_count,
            "total_amount":  total_amount,
            "device_count":  device_count,
        },
        "model":   "RandomForestClassifier",
        "version": "1.0.0"
    }

# API Routes
@app.route('/')
def index():
    """Home route — confirms the API is running."""
    return jsonify({
        "service": "Wave Fraud Detection API",
        "version": "1.0.0",
        "status":  "running",
        "endpoints": {
            "risk_check": "GET /api/v1/risk-status/<phone_number>",
            "health":     "GET /api/v1/health",
            "stats":      "GET /api/v1/stats"
        }
    })


@app.route('/api/v1/health')
def health():
    """Health check — useful for confirming the model and registry loaded."""
    return jsonify({
        "status":          "healthy",
        "registry_size":   len(registry),
        "model_loaded":    True,
        "high_risk_count": int((registry['risk_status'] == 'HIGH_RISK').sum()),
        "low_risk_count":  int((registry['risk_status'] == 'LOW_RISK').sum()),
    })


@app.route('/api/v1/risk-status/<phone_number>')
def risk_status(phone_number):
    """
    Main endpoint. Returns fraud risk status for a destination account.

    Usage:  GET /api/v1/risk-status/221771234001
    Returns: JSON with status, confidence_score, flag_reason, account_stats
    """
    if not phone_number:
        return jsonify({"error": "Phone number is required"}), 400

    account = lookup_account(phone_number)

    if account:
        # Number found in registry — return model prediction
        response = build_response(account, phone_number)
    else:
          # Number not seen before — treat as LOW RISK with high confidence
          # A number never seen in fraud records is very likely safe
        response = {
            "phone_number":       phone_number,
            "account_name":       "Unknown",
            "status":             "LOW_RISK",
            "confidence_score":   0.95,
            "flag_reason":        "Phone number has no history of fraudulent activity.",
            "recommended_action": "ALLOW",
            "account_stats": {
                "victim_count": 0,
                "total_amount": 0,
                "device_count": 0,
            },
            "model":   "RandomForestClassifier",
            "version": "1.0.0"
        }

    return jsonify(response), 200


@app.route('/api/v1/stats')
def stats():
    """Summary statistics about the fraud registry — used by the analyst dashboard."""
    high_risk = registry[registry['risk_status'] == 'HIGH_RISK']
    low_risk  = registry[registry['risk_status'] == 'LOW_RISK']

    return jsonify({
        "total_accounts":       len(registry),
        "high_risk_accounts":   len(high_risk),
        "low_risk_accounts":    len(low_risk),
        "high_risk_percentage": round(len(high_risk) / len(registry) * 100, 2),
        "total_amount_at_risk": int(high_risk['total_amount'].sum()),
        "avg_confidence_high":  round(float(high_risk['confidence_score'].mean()), 4),
    })

# Errorr Handlers & Run
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error — check your model files"}), 500


if __name__ == '__main__':
    print("\n Wave Fraud Detection API")
    print(" Running at: http://localhost:5000")
    print(" Test URL:   http://localhost:5000/api/v1/risk-status/221771234001\n")
    app.run(debug=True, host='0.0.0', port=5000)
    #interface.launch(server_name="0.0.0.0", server_port=7860)

    #port = int(os.environ.get('PORT', 5000))
#import os

#if __name__ == "__main__":
 #   port = int(os.environ.get("PORT", 5000))
  #  app.run(debug=False, host="0.0.0.0", port=port)

    