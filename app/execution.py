from fastapi import APIRouter
import sqlite3
import json

router = APIRouter()

conn = sqlite3.connect("manthan.db", check_same_thread=False)

# =========================
# DATABASE
# =========================

conn.execute("""
CREATE TABLE IF NOT EXISTS audit_logs (
    input TEXT,
    decision TEXT,
    reason TEXT
)
""")

conn.execute("""
CREATE TABLE IF NOT EXISTS contracts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version TEXT,
    contract_json TEXT
)
""")

conn.commit()


# =========================
# INIT CONTRACT
# =========================

def init_contract():
    cursor = conn.execute("SELECT COUNT(*) FROM contracts")
    count = cursor.fetchone()[0]

    if count == 0:
        conn.execute(
            "INSERT INTO contracts (version, contract_json) VALUES (?, ?)",
            (
                "v1",
                json.dumps({
                    "rules": [
                        {"condition": "amount <= 5000", "action": "auto_approve"},
                        {"condition": "amount > 5000", "action": "require_manager"}
                    ]
                })
            )
        )
        conn.commit()

init_contract()


# =========================
# LOAD CONTRACT
# =========================

def get_contract():
    cursor = conn.execute(
        "SELECT contract_json FROM contracts ORDER BY id DESC LIMIT 1"
    )
    row = cursor.fetchone()

    if not row:
        return {"rules": []}

    return json.loads(row[0])


# =========================
# VALIDATION (SAMIKSHA)
# =========================

def validate_contract(contract):
    if not contract:
        return False, "Contract missing"

    if "rules" not in contract:
        return False, "Missing 'rules'"

    if not isinstance(contract["rules"], list) or len(contract["rules"]) == 0:
        return False, "Rules must be non-empty list"

    for i, rule in enumerate(contract["rules"]):
        if "condition" not in rule:
            return False, f"Rule {i} missing condition"

        if "action" not in rule:
            return False, f"Rule {i} missing action"

        if not isinstance(rule["condition"], str):
            return False, f"Rule {i} condition must be string"

    return True, "valid"


# =========================
# ENGINE (NIRMIT RUNTIME)
# =========================

def evaluate(contract, data):
    for rule in contract["rules"]:
        if eval(rule["condition"], {}, data):
            return {
                "decision": rule["action"],
                "reason": rule["condition"]
            }

    return {"decision": "no_match", "reason": "no rule matched"}


# =========================
# EXECUTION API
# =========================

@router.post("/execute/expense_approval")
def execute(data: dict):
    contract = get_contract()
    result = evaluate(contract, data)

    conn.execute(
        "INSERT INTO audit_logs VALUES (?, ?, ?)",
        (json.dumps(data), result["decision"], result["reason"])
    )
    conn.commit()

    return result


# =========================
# AUDIT API
# =========================

@router.get("/audit")
def get_audit_logs():
    cursor = conn.execute("SELECT * FROM audit_logs")
    rows = cursor.fetchall()

    return [
        {
            "input": row[0],
            "decision": row[1],
            "reason": row[2]
        }
        for row in rows
    ]


# =========================
# CONTRACT APIs
# =========================

@router.get("/contract")
def get_current_contract():
    cursor = conn.execute(
        "SELECT version, contract_json FROM contracts ORDER BY id DESC LIMIT 1"
    )
    row = cursor.fetchone()

    if not row:
        return {"message": "No contract found"}

    return {
        "version": row[0],
        "contract": json.loads(row[1])
    }


@router.post("/contract")
def create_contract(data: dict):
    version = data.get("version", "v_unknown")
    contract = data.get("contract")

    is_valid, message = validate_contract(contract)

    if not is_valid:
        return {
            "status": "rejected",
            "reason": message
        }

    conn.execute(
        "INSERT INTO contracts (version, contract_json) VALUES (?, ?)",
        (version, json.dumps(contract))
    )
    conn.commit()

    return {
        "status": "contract_created",
        "version": version
    }