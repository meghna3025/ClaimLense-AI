"""
sample_client.py
─────────────────
Example script showing how to call the ClaimSense AI API.

Usage:
  python scripts/sample_client.py --image path/to/accident.jpg \
         --policy POL-STANDARD-1234 \
         --vehicle "Toyota Corolla" \
         --description "Front collision at traffic signal"
"""

import argparse
import json
import sys
from pathlib import Path

import httpx

BASE_URL = "http://localhost:8000"


def process_claim(
    image_path: str,
    policy_number: str,
    vehicle_model: str,
    description: str,
) -> dict:
    image = Path(image_path)
    if not image.exists():
        print(f"❌ Image not found: {image_path}")
        sys.exit(1)

    print(f"📤 Sending claim for {vehicle_model} ({policy_number})…")

    with open(image, "rb") as f:
        response = httpx.post(
            f"{BASE_URL}/api/v1/claims/process",
            files={"image": (image.name, f, "image/jpeg")},
            data={
                "description": description,
                "policy_number": policy_number,
                "vehicle_model": vehicle_model,
            },
            timeout=120.0,
        )

    if response.status_code != 200:
        print(f"❌ Error {response.status_code}: {response.text}")
        sys.exit(1)

    return response.json()


def print_result(result: dict) -> None:
    print("\n" + "=" * 60)
    print(f"  CLAIMSENSE AI RESULT — {result['claim_id']}")
    print("=" * 60)

    decision = result.get("decision", {})
    if decision:
        d = decision["decision"]
        emoji = {"APPROVE": "✅", "REJECT": "❌", "HUMAN_REVIEW": "👁"}
        print(f"\n  DECISION: {emoji.get(d, '?')} {d}")
        print(f"  Approved Amount: ₹{decision.get('approved_amount', 0):,.0f}")
        print(f"  Confidence: {decision.get('confidence', 0):.0%}")
        print(f"\n  Summary: {decision.get('summary', '')}")

    vision = result.get("vision", {})
    if vision:
        print(f"\n  📸 Vision Analysis")
        print(f"     Accident Type : {vision.get('accident_type')}")
        print(f"     Severity      : {vision.get('overall_severity')}")
        for part in vision.get("damaged_parts", []):
            print(f"     • {part['part_name']} ({part['severity']}, {part['confidence']:.0%})")

    repair = result.get("repair_estimation", {})
    if repair:
        print(f"\n  🔧 Repair Estimation")
        print(f"     Grand Total   : ₹{repair.get('grand_total', 0):,.0f}")
        for est in repair.get("estimates", []):
            print(f"     • {est['part_name']}: ₹{est['total_cost']:,.0f} ({est['action']})")

    fraud = result.get("fraud_risk", {})
    if fraud:
        risk_emoji = {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🔴"}
        level = fraud.get("fraud_risk_level", "LOW")
        print(f"\n  🔍 Fraud Risk: {risk_emoji.get(level, '?')} {level} (score: {fraud.get('fraud_score', 0):.2f})")

    errors = result.get("processing_errors", [])
    if errors:
        print(f"\n  ⚠️  Processing Errors:")
        for e in errors:
            print(f"     • {e}")

    print("\n" + "=" * 60)
    print("  Full JSON saved to: claim_result.json")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ClaimSense AI client")
    parser.add_argument("--image", required=True, help="Path to accident image")
    parser.add_argument("--policy", required=True, help="Policy number")
    parser.add_argument("--vehicle", required=True, help="Vehicle model")
    parser.add_argument("--description", required=True, help="Accident description")
    args = parser.parse_args()

    result = process_claim(args.image, args.policy, args.vehicle, args.description)
    print_result(result)

    with open("claim_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
