# Mobile Money Fraud Detection System

A machine learning system that detects fraudulent mobile money destination accounts on the Senegalese +221 network.

## Problem Statement
Fraudsters use social engineering and SIM swap attacks to deceive victims into transferring money to criminal-controlled accounts. This system identifies HIGH-RISK destination accounts before a transfer is completed.

## Dataset
- **Source:** FraudulenttransfertoKYC2_2024-9.xlsx
- **Records:** 34,178 transactions (December 2021 – September 2024)
- **Unique victims:** 4,809 | **Unique fraud accounts:** 4,264
- **Country:** Senegal (+221 network)

## Project Structure
## How to Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the notebook
```bash
jupyter notebook notebooks/01_eda_and_modelling.ipynb
```

### 3. Start the API
```bash
python api/risk_status_api.py
```

### 4. Open the demo
- `demo/user_transaction/index.html`
- `demo/analyst_dashboard/index.html`

## Models
| Model | ROC-AUC | F1-Score |
|-------|---------|----------|
| Random Forest | TBD | TBD |
| MLP Neural Network | TBD | TBD |

## Author
Mobile Money Fraud Detection — Senegal +221 Network
