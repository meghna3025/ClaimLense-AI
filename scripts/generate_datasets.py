"""
generate_datasets.py
─────────────────────
Generates all synthetic datasets required for ClaimSense AI:
  1. Repair cost database (JSON)
  2. Insurance policies (Markdown → PDF)
  3. Historical claims (JSON)
  4. Fraud rules (JSON)

Run: python scripts/generate_datasets.py
"""

import json
import random
from pathlib import Path
from datetime import datetime, timedelta

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"
RAG_DIR = ROOT / "rag"
POLICIES_DIR = RAG_DIR / "policies"
REPAIR_DIR = RAG_DIR / "repair_catalog"
FRAUD_DIR = RAG_DIR / "fraud_rules"
CLAIMS_DIR = RAG_DIR / "claims_history"

for d in [DATA_DIR, POLICIES_DIR, REPAIR_DIR, FRAUD_DIR, CLAIMS_DIR]:
    d.mkdir(parents=True, exist_ok=True)


# ═══════════════════════════════════════════════════════════════
#  1. REPAIR COST DATABASE
# ═══════════════════════════════════════════════════════════════

REPAIR_DATA = {
    "metadata": {
        "version": "1.0",
        "currency": "INR",
        "last_updated": "2024-01-01",
        "note": "Prices include OEM parts. Labour charged separately."
    },
    "vehicles": {
        "Toyota Corolla": {
            "Front Bumper": {"parts_cost": 18000, "labour_cost": 4000, "action": "REPLACE"},
            "Rear Bumper": {"parts_cost": 17000, "labour_cost": 3500, "action": "REPLACE"},
            "Front Bumper Repair": {"parts_cost": 3000, "labour_cost": 2500, "action": "REPAIR"},
            "Headlight (Left)": {"parts_cost": 9500, "labour_cost": 1500, "action": "REPLACE"},
            "Headlight (Right)": {"parts_cost": 9500, "labour_cost": 1500, "action": "REPLACE"},
            "Taillight (Left)": {"parts_cost": 7500, "labour_cost": 1200, "action": "REPLACE"},
            "Taillight (Right)": {"parts_cost": 7500, "labour_cost": 1200, "action": "REPLACE"},
            "Bonnet": {"parts_cost": 22000, "labour_cost": 6000, "action": "REPLACE"},
            "Bonnet Repair": {"parts_cost": 4000, "labour_cost": 3000, "action": "REPAIR"},
            "Front Door (Left)": {"parts_cost": 32000, "labour_cost": 8000, "action": "REPLACE"},
            "Front Door (Right)": {"parts_cost": 32000, "labour_cost": 8000, "action": "REPLACE"},
            "Rear Door (Left)": {"parts_cost": 28000, "labour_cost": 7000, "action": "REPLACE"},
            "Rear Door (Right)": {"parts_cost": 28000, "labour_cost": 7000, "action": "REPLACE"},
            "Windshield": {"parts_cost": 14000, "labour_cost": 3000, "action": "REPLACE"},
            "Rear Windshield": {"parts_cost": 11000, "labour_cost": 2500, "action": "REPLACE"},
            "Side Mirror (Left)": {"parts_cost": 4500, "labour_cost": 800, "action": "REPLACE"},
            "Side Mirror (Right)": {"parts_cost": 4500, "labour_cost": 800, "action": "REPLACE"},
            "Fender (Left)": {"parts_cost": 12000, "labour_cost": 4000, "action": "REPLACE"},
            "Fender (Right)": {"parts_cost": 12000, "labour_cost": 4000, "action": "REPLACE"},
            "Radiator": {"parts_cost": 18000, "labour_cost": 5000, "action": "REPLACE"},
            "Airbag Replacement": {"parts_cost": 45000, "labour_cost": 12000, "action": "REPLACE"},
            "Wheel Alignment": {"parts_cost": 0, "labour_cost": 2500, "action": "REPAIR"},
            "Dent Removal (Minor)": {"parts_cost": 0, "labour_cost": 3500, "action": "REPAIR"},
        },
        "Honda City": {
            "Front Bumper": {"parts_cost": 16500, "labour_cost": 4000, "action": "REPLACE"},
            "Rear Bumper": {"parts_cost": 15500, "labour_cost": 3500, "action": "REPLACE"},
            "Headlight (Left)": {"parts_cost": 11000, "labour_cost": 1800, "action": "REPLACE"},
            "Headlight (Right)": {"parts_cost": 11000, "labour_cost": 1800, "action": "REPLACE"},
            "Bonnet": {"parts_cost": 20000, "labour_cost": 5500, "action": "REPLACE"},
            "Windshield": {"parts_cost": 13000, "labour_cost": 2800, "action": "REPLACE"},
            "Front Door (Left)": {"parts_cost": 30000, "labour_cost": 7500, "action": "REPLACE"},
            "Front Door (Right)": {"parts_cost": 30000, "labour_cost": 7500, "action": "REPLACE"},
            "Rear Door (Left)": {"parts_cost": 26000, "labour_cost": 6500, "action": "REPLACE"},
            "Side Mirror (Left)": {"parts_cost": 5000, "labour_cost": 900, "action": "REPLACE"},
            "Fender (Left)": {"parts_cost": 11000, "labour_cost": 3800, "action": "REPLACE"},
            "Airbag Replacement": {"parts_cost": 48000, "labour_cost": 13000, "action": "REPLACE"},
        },
        "Hyundai i20": {
            "Front Bumper": {"parts_cost": 14000, "labour_cost": 3500, "action": "REPLACE"},
            "Rear Bumper": {"parts_cost": 13000, "labour_cost": 3000, "action": "REPLACE"},
            "Headlight (Left)": {"parts_cost": 8500, "labour_cost": 1400, "action": "REPLACE"},
            "Bonnet": {"parts_cost": 17000, "labour_cost": 5000, "action": "REPLACE"},
            "Windshield": {"parts_cost": 10500, "labour_cost": 2500, "action": "REPLACE"},
            "Front Door (Left)": {"parts_cost": 25000, "labour_cost": 6500, "action": "REPLACE"},
            "Fender (Left)": {"parts_cost": 9000, "labour_cost": 3200, "action": "REPLACE"},
        },
        "Maruti Swift": {
            "Front Bumper": {"parts_cost": 11000, "labour_cost": 3000, "action": "REPLACE"},
            "Rear Bumper": {"parts_cost": 10500, "labour_cost": 2800, "action": "REPLACE"},
            "Headlight (Left)": {"parts_cost": 6500, "labour_cost": 1200, "action": "REPLACE"},
            "Bonnet": {"parts_cost": 14000, "labour_cost": 4500, "action": "REPLACE"},
            "Windshield": {"parts_cost": 8500, "labour_cost": 2200, "action": "REPLACE"},
            "Front Door (Left)": {"parts_cost": 20000, "labour_cost": 5500, "action": "REPLACE"},
            "Fender (Left)": {"parts_cost": 7500, "labour_cost": 2800, "action": "REPLACE"},
        },
        "Tata Nexon": {
            "Front Bumper": {"parts_cost": 19000, "labour_cost": 4500, "action": "REPLACE"},
            "Rear Bumper": {"parts_cost": 17500, "labour_cost": 4000, "action": "REPLACE"},
            "Headlight (Left)": {"parts_cost": 13000, "labour_cost": 2000, "action": "REPLACE"},
            "Bonnet": {"parts_cost": 24000, "labour_cost": 6500, "action": "REPLACE"},
            "Windshield": {"parts_cost": 15000, "labour_cost": 3200, "action": "REPLACE"},
            "Front Door (Left)": {"parts_cost": 34000, "labour_cost": 8500, "action": "REPLACE"},
        },
    }
}


def generate_repair_catalog():
    path = DATA_DIR / "repair_costs.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(REPAIR_DATA, f, indent=2, ensure_ascii=False)
    # Also save to RAG repair catalog dir
    rag_path = REPAIR_DIR / "repair_costs.json"
    with open(rag_path, "w", encoding="utf-8") as f:
        json.dump(REPAIR_DATA, f, indent=2, ensure_ascii=False)
    print(f"✅ Repair catalog → {path}")


# ═══════════════════════════════════════════════════════════════
#  2. INSURANCE POLICIES (Markdown)
# ═══════════════════════════════════════════════════════════════

POLICIES = [
    {
        "id": "BASIC",
        "name": "Basic Motor Insurance",
        "policy_prefix": "POL-BASIC",
        "monthly_premium": 850,
        "deductible": 10000,
        "max_payout": 75000,
        "coverage_pct": 60,
        "content": """# Basic Motor Insurance Policy

**Policy Type:** Basic  
**Policy Prefix:** POL-BASIC-XXXX  
**Monthly Premium:** ₹850  
**Annual Premium:** ₹9,800  

---

## Section 1 — Coverage

### 1.1 Covered Damages
- Third-party property damage (mandatory by law)
- Accidental damage to own vehicle caused by collision
- Fire damage to vehicle
- Theft of vehicle (partial, up to 60% IDV)
- Natural calamities (flood, earthquake) — limited to ₹25,000

### 1.2 Coverage Limits
- **Maximum Payout:** ₹75,000 per claim
- **Coverage Percentage:** 60% of assessed repair cost
- **Deductible:** ₹10,000 per claim (compulsory)
- **Maximum Claims per Year:** 2

---

## Section 2 — Exclusions

### 2.1 What is NOT Covered
- Damage caused while driving under influence of alcohol or drugs
- Intentional damage or staged accidents
- Wear and tear, mechanical breakdown
- Damage to tyres unless vehicle is also damaged
- Electrical/mechanical failures not caused by accident
- Consequential losses (rental car, loss of income)
- Damage outside India
- Racing, speed testing, or motorsport events
- Vehicles used for commercial purposes not declared at policy inception
- Pre-existing damage claimed as accident damage

### 2.2 Geographic Exclusions
- Only valid within India

---

## Section 3 — Claims Process

### 3.1 Required Documents
1. Duly filled claim form
2. Copy of driving licence (valid at time of accident)
3. Copy of Registration Certificate (RC)
4. FIR (for theft, third-party claims, or accidents with injury)
5. Original repair bills and payment receipts
6. Photographs of the damaged vehicle (minimum 4 angles)
7. Policy document copy

### 3.2 Claim Timeline
- Report claim within **48 hours** of accident
- Survey must be completed within **7 working days**
- Settlement within **30 days** of document submission

---

## Section 4 — Deductible

### 4.1 Compulsory Deductible
- ₹10,000 applied to every own-damage claim
- Deductible is non-refundable regardless of claim outcome

### 4.2 Voluntary Deductible
- Additional voluntary deductible options available for premium discount

---

## Section 5 — Special Conditions

- Zero Depreciation NOT included in Basic plan
- No add-ons included
- Roadside assistance NOT included
- Engine protection NOT included
""",
    },
    {
        "id": "STANDARD",
        "name": "Standard Motor Insurance",
        "policy_prefix": "POL-STANDARD",
        "monthly_premium": 1500,
        "deductible": 5000,
        "max_payout": 150000,
        "coverage_pct": 80,
        "content": """# Standard Motor Insurance Policy

**Policy Type:** Standard  
**Policy Prefix:** POL-STANDARD-XXXX  
**Monthly Premium:** ₹1,500  
**Annual Premium:** ₹17,500  

---

## Section 1 — Coverage

### 1.1 Covered Damages
- Own vehicle accidental damage (collision, overturn, impact)
- Third-party liability (bodily injury + property damage)
- Fire, explosion, self-ignition damage
- Theft (total or partial) — up to IDV
- Natural calamities (flood, cyclone, earthquake, landslide)
- Malicious damage by third parties
- Damage during transit (rail, road, air, inland waterway)

### 1.2 Coverage Limits
- **Maximum Payout:** ₹1,50,000 per claim
- **Coverage Percentage:** 80% of assessed repair cost
- **Deductible:** ₹5,000 per claim (compulsory)
- **Maximum Claims per Year:** 3

---

## Section 2 — Exclusions

### 2.1 What is NOT Covered
- Driving under influence (DUI) — claim will be fully rejected
- Intentional damage or fraud (claim rejected + policy cancelled)
- Wear and tear, gradual deterioration
- Mechanical or electrical breakdown not linked to an insured event
- Depreciation on parts (unless Zero-Dep add-on is purchased)
- Tyres and tubes (unless vehicle sustains additional damage simultaneously)
- Damage to accessories not declared at inception
- Consequential losses
- Nuclear, war, or civil commotion risks

### 2.2 Depreciation Schedule (Standard Parts)
| Part Type | Depreciation |
|-----------|-------------|
| Rubber/nylon/plastic parts | 50% |
| Fibreglass components | 30% |
| Wooden components | 5% per year |
| All other parts | As per vehicle age schedule |

---

## Section 3 — Claims Process

### 3.1 Required Documents
1. Duly filled and signed claim form
2. Valid driving licence
3. Vehicle RC and fitness certificate (if applicable)
4. FIR (mandatory for accidents involving third parties or theft)
5. Photographs — minimum 6 photos from different angles
6. Original repair bills, parts invoices, and payment receipts
7. Survey report from approved surveyor
8. Bank account details for NEFT transfer
9. Subrogation letter (if applicable)

### 3.2 Cashless Garage Network
- 5,000+ network garages across India
- Cashless facility available at network garages
- Reimbursement within 21 days for non-network garages

---

## Section 4 — No-Claim Bonus (NCB)

| Consecutive Claim-Free Years | NCB Discount |
|------------------------------|-------------|
| 1 year | 20% |
| 2 years | 25% |
| 3 years | 35% |
| 4 years | 45% |
| 5+ years | 50% |

NCB is forfeited upon any claim during the policy year.

---

## Section 5 — Add-ons Available

- Zero Depreciation Cover (additional premium)
- Roadside Assistance (additional premium)
- Engine Protection Cover (additional premium)
- Return to Invoice Cover (additional premium)
""",
    },
    {
        "id": "PREMIUM",
        "name": "Premium Motor Insurance",
        "policy_prefix": "POL-PREMIUM",
        "monthly_premium": 2800,
        "deductible": 2500,
        "max_payout": 300000,
        "coverage_pct": 90,
        "content": """# Premium Motor Insurance Policy

**Policy Type:** Premium  
**Policy Prefix:** POL-PREMIUM-XXXX  
**Monthly Premium:** ₹2,800  
**Annual Premium:** ₹32,000  

---

## Section 1 — Coverage

### 1.1 Covered Damages
- All Standard plan covers PLUS:
- Zero depreciation on all parts (no depreciation deduction)
- Engine and gearbox damage due to water ingression/oil leak damage
- Return to Invoice (RTI) value on total loss or theft
- Key replacement cover (up to ₹15,000)
- Emergency roadside assistance (24x7)
- Tyre damage even without concurrent vehicle damage

### 1.2 Coverage Limits
- **Maximum Payout:** ₹3,00,000 per claim
- **Coverage Percentage:** 90% of assessed repair cost
- **Deductible:** ₹2,500 per claim (compulsory)
- **Maximum Claims per Year:** 5

---

## Section 2 — Exclusions

### 2.1 What is NOT Covered
- DUI (driving under influence) — absolute exclusion, claim rejected
- Intentional/fraudulent damage
- Racing or competitive driving events
- Nuclear/bio/chemical war risks
- Gradual wear and tear (covered only if caused by insured event)

---

## Section 3 — Claims Process

### 3.1 Priority Claim Service
- Dedicated claim relationship manager
- 24-hour claim registration (call/app/website)
- On-site surveyor dispatch within 4 hours in metro cities
- Cashless facility at 7,500+ authorised workshops
- Claim settlement within 14 working days
- Direct bank transfer or cheque

### 3.2 Required Documents
1. Claim form (digital signature accepted)
2. Driving licence
3. RC and PUC certificate
4. FIR (if applicable)
5. Photographs/video of damage scene
6. Original repair estimate and bills

---

## Section 4 — Towing and Roadside Assistance

- Free towing up to 100 km from breakdown location
- Battery jumpstart service
- Fuel delivery (up to 5 litres)
- Flat tyre change assistance
- Minor on-road repairs
- Hotel accommodation if vehicle immobilised overnight (up to ₹3,000/night)

---

## Section 5 — Premium Perks

- Annual free vehicle health check at partner workshop
- Loyalty bonus: 5% additional NCB after 3 claim-free years
- Family floater: Cover spouse's vehicle at 15% discount
""",
    },
    {
        "id": "COMPREHENSIVE",
        "name": "Comprehensive Motor Insurance",
        "policy_prefix": "POL-COMP",
        "monthly_premium": 4500,
        "deductible": 0,
        "max_payout": 1000000,
        "coverage_pct": 100,
        "content": """# Comprehensive Motor Insurance Policy

**Policy Type:** Comprehensive  
**Policy Prefix:** POL-COMP-XXXX  
**Monthly Premium:** ₹4,500  
**Annual Premium:** ₹52,000  

---

## Section 1 — Coverage

### 1.1 All-Inclusive Coverage
The Comprehensive policy provides maximum protection including ALL Premium
plan benefits PLUS:

- **Zero Deductible** — no out-of-pocket expense for any approved claim
- **Consumables Cover** — nuts, bolts, engine oil, coolant, etc. included
- **Passenger Cover** — up to ₹1,00,000 per passenger (up to 4 passengers)
- **Personal Accident Cover** — ₹15,00,000 for owner-driver
- **Loss of Baggage** — up to ₹25,000 per incident
- **Rental Car Cover** — up to ₹3,000/day for 15 days during repair
- **New Vehicle Replacement** — if total loss within 12 months of purchase
- **Depreciation Waiver** — all parts covered at full value, no deductions

### 1.2 Coverage Limits
- **Maximum Payout:** ₹10,00,000 per claim
- **Coverage Percentage:** 100% of assessed repair cost
- **Deductible:** ₹0 (zero deductible)
- **Maximum Claims per Year:** Unlimited

---

## Section 2 — Exclusions (Minimal)

### 2.1 Absolute Exclusions
- Intentional damage, fraud, or staged accidents
- Driving under influence of alcohol/drugs (BAC > 0.03%)
- Nuclear, radiological, chemical, or biological war risks
- Vehicles used for illegal purposes at time of loss

---

## Section 3 — Claims Process

### 3.1 Elite Claims Service
- Dedicated personal claims manager (direct mobile number)
- Claim registration within 1 hour via app
- Surveyor on-site within 2 hours in major cities, 6 hours elsewhere
- Cashless at 10,000+ authorised repair centres across India
- Guaranteed settlement within 7 working days
- Option for vehicle pickup and delivery during repair

---

## Section 4 — Additional Benefits

### 4.1 Complimentary Services
- Annual inspection by certified engineer
- Free minor dent/scratch repair (1 per year, up to ₹5,000)
- VIP towing (flatbed truck) up to 200 km
- Car wash and detailing after each repair at network garage

### 4.2 Depreciation Schedule
- **Zero Depreciation** applies to all parts and labour
- No deduction for age, condition, or part type

---

## Section 5 — Policy Terms

- Policy period: 1 year (renewable)
- Grace period for renewal: 30 days
- Mid-term cancellation refund: Pro-rata basis minus ₹2,500 processing fee
""",
    },
]


def generate_policies():
    """Write policy markdown files and a metadata JSON."""
    metadata = []
    for policy in POLICIES:
        md_path = POLICIES_DIR / f"policy_{policy['id'].lower()}.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(policy["content"])
        print(f"  📄 {md_path.name}")
        metadata.append({
            "id": policy["id"],
            "name": policy["name"],
            "prefix": policy["policy_prefix"],
            "monthly_premium": policy["monthly_premium"],
            "deductible": policy["deductible"],
            "max_payout": policy["max_payout"],
            "coverage_pct": policy["coverage_pct"],
            "file": md_path.name,
        })
    meta_path = POLICIES_DIR / "policy_metadata.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"✅ Policies → {POLICIES_DIR}")


# ═══════════════════════════════════════════════════════════════
#  3. FRAUD RULES
# ═══════════════════════════════════════════════════════════════

FRAUD_RULES = {
    "version": "1.0",
    "rules": [
        {"id": "FR001", "name": "Description-Damage Mismatch",
         "description": "Accident description does not match visible damage location/type",
         "weight": 0.8, "category": "Inconsistency"},
        {"id": "FR002", "name": "Severity Inflation",
         "description": "Claimed severity far exceeds what is visible in photos",
         "weight": 0.9, "category": "Fraud"},
        {"id": "FR003", "name": "Pre-existing Damage",
         "description": "Damage shows signs of age, rust, or previous repair inconsistent with recent accident",
         "weight": 0.85, "category": "Pre-existing"},
        {"id": "FR004", "name": "Estimate Inflation",
         "description": "Repair estimate significantly exceeds market rate for the damage described",
         "weight": 0.75, "category": "Financial"},
        {"id": "FR005", "name": "Policy Timing Suspicious",
         "description": "Major claim filed within 30 days of policy inception",
         "weight": 0.7, "category": "Timing"},
        {"id": "FR006", "name": "Multiple Claims Pattern",
         "description": "More than 2 claims in 12 months for same vehicle",
         "weight": 0.65, "category": "Pattern"},
        {"id": "FR007", "name": "Vague Accident Description",
         "description": "Accident description lacks specific details (location, time, circumstances)",
         "weight": 0.5, "category": "Documentation"},
        {"id": "FR008", "name": "Unrelated Parts Claimed",
         "description": "Parts claimed do not correspond to the type of accident described",
         "weight": 0.8, "category": "Inconsistency"},
        {"id": "FR009", "name": "No FIR Filed",
         "description": "High-value claim without police FIR when legally required",
         "weight": 0.6, "category": "Documentation"},
        {"id": "FR010", "name": "Witness Inconsistency",
         "description": "Witness accounts contradict the claimant's description",
         "weight": 0.85, "category": "Inconsistency"},
        {"id": "FR011", "name": "Total Loss on Old Vehicle",
         "description": "Total loss claim on vehicle near end of depreciation life",
         "weight": 0.55, "category": "Financial"},
        {"id": "FR012", "name": "Airbag Without Impact Damage",
         "description": "Airbag deployment claimed without corresponding major impact damage",
         "weight": 0.9, "category": "Fraud"},
        {"id": "FR013", "name": "Image Metadata Manipulation",
         "description": "Photo EXIF data suggests images not taken at claimed date/location",
         "weight": 0.95, "category": "Fraud"},
        {"id": "FR014", "name": "Duplicate Claim",
         "description": "Similar claim filed with another insurer for same incident",
         "weight": 1.0, "category": "Fraud"},
        {"id": "FR015", "name": "Repair Bill Discrepancy",
         "description": "Repair bills show different amounts or parts than surveyor assessment",
         "weight": 0.85, "category": "Financial"},
    ]
}


def generate_fraud_rules():
    path = FRAUD_DIR / "fraud_rules.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(FRAUD_RULES, f, indent=2)
    print(f"✅ Fraud rules → {path}")


# ═══════════════════════════════════════════════════════════════
#  4. HISTORICAL CLAIMS (200 synthetic records)
# ═══════════════════════════════════════════════════════════════

random.seed(42)

VEHICLES = [
    ("Toyota", "Corolla"), ("Honda", "City"), ("Hyundai", "i20"),
    ("Maruti", "Swift"), ("Tata", "Nexon"), ("Ford", "EcoSport"),
    ("Kia", "Seltos"), ("MG", "Hector"), ("Skoda", "Octavia"),
    ("Volkswagen", "Polo"), ("Renault", "Kwid"), ("Datsun", "redi-GO"),
]

DAMAGE_TYPES = [
    "Front Collision", "Rear-End Collision", "Side Impact",
    "Rollover", "Multi-Point Impact", "Parking Damage",
    "Hail Damage", "Flood Damage", "Fire Damage",
]

DAMAGED_PARTS = [
    "Front Bumper", "Rear Bumper", "Headlight", "Taillight",
    "Bonnet", "Boot Lid", "Front Door", "Rear Door",
    "Windshield", "Rear Windshield", "Side Mirror",
    "Fender", "Radiator", "Engine", "Chassis",
]

POLICY_TYPES = ["Basic", "Standard", "Premium", "Comprehensive"]

SEVERITIES = ["MINOR", "MODERATE", "SEVERE", "TOTAL_LOSS"]
SEVERITY_WEIGHTS = [0.35, 0.40, 0.18, 0.07]

DECISIONS = ["APPROVE", "REJECT", "HUMAN_REVIEW"]
FRAUD_LEVELS = ["LOW", "MEDIUM", "HIGH"]

CLAIM_TEMPLATES = [
    "Vehicle was {verb} by another car at a {location}. {part} was damaged.",
    "While parking, another vehicle collided with my {part}.",
    "Skidded on wet road, vehicle hit a divider causing {part} damage.",
    "Another vehicle ran a red light and hit the {side} side of my vehicle.",
    "Vehicle was damaged in a hailstorm near {location}.",
    "Rear-ended at slow speed in heavy traffic; {part} damaged.",
    "Vehicle hit a pothole at speed, causing {part} damage.",
    "Vandalism in parking lot — multiple parts damaged including {part}.",
    "Flash flood caused water ingression and {part} damage.",
]

LOCATIONS = ["traffic signal", "highway", "parking lot", "roundabout", "bridge", "T-junction"]
VERBS = ["hit", "struck", "sideswiped", "rear-ended", "T-boned"]
SIDES = ["left", "right", "front", "rear"]


def generate_claim_description(damage_type: str, parts: list[str]) -> str:
    tmpl = random.choice(CLAIM_TEMPLATES)
    return tmpl.format(
        verb=random.choice(VERBS),
        location=random.choice(LOCATIONS),
        part=random.choice(parts) if parts else "front section",
        side=random.choice(SIDES),
    )


def estimate_repair_cost(severity: str, num_parts: int) -> float:
    base = {"MINOR": 8000, "MODERATE": 35000, "SEVERE": 90000, "TOTAL_LOSS": 200000}[severity]
    multiplier = 1 + (num_parts - 1) * 0.3
    noise = random.uniform(0.8, 1.25)
    return round(base * multiplier * noise, -2)  # round to nearest 100


def decide_claim(policy_type: str, fraud_level: str, severity: str, repair_cost: float) -> str:
    if fraud_level == "HIGH":
        return "REJECT"
    if severity == "TOTAL_LOSS" and policy_type in ("Basic",):
        return "REJECT"
    if fraud_level == "MEDIUM" or repair_cost > 200000:
        return "HUMAN_REVIEW"
    return "APPROVE"


def generate_historical_claims(n: int = 200) -> list[dict]:
    claims = []
    base_date = datetime(2023, 1, 1)

    for i in range(n):
        make, model = random.choice(VEHICLES)
        vehicle = f"{make} {model}"
        damage_type = random.choice(DAMAGE_TYPES)
        severity = random.choices(SEVERITIES, weights=SEVERITY_WEIGHTS)[0]
        policy_type = random.choice(POLICY_TYPES)
        num_parts = random.randint(1, 5)
        damaged_parts = random.sample(DAMAGED_PARTS, min(num_parts, len(DAMAGED_PARTS)))
        repair_cost = estimate_repair_cost(severity, num_parts)
        fraud_level = random.choices(FRAUD_LEVELS, weights=[0.70, 0.20, 0.10])[0]
        decision = decide_claim(policy_type, fraud_level, severity, repair_cost)
        confidence = round(random.uniform(0.65, 0.98), 2)
        claim_date = base_date + timedelta(days=random.randint(0, 700))

        policy_prefixes = {
            "Basic": "POL-BASIC", "Standard": "POL-STANDARD",
            "Premium": "POL-PREMIUM", "Comprehensive": "POL-COMP"
        }
        policy_number = f"{policy_prefixes[policy_type]}-{random.randint(1000, 9999):04d}"

        approved_amount = 0.0
        if decision == "APPROVE":
            coverage_pct = {"Basic": 60, "Standard": 80, "Premium": 90, "Comprehensive": 100}[policy_type]
            deductible = {"Basic": 10000, "Standard": 5000, "Premium": 2500, "Comprehensive": 0}[policy_type]
            max_payout = {"Basic": 75000, "Standard": 150000, "Premium": 300000, "Comprehensive": 1000000}[policy_type]
            approved_amount = min(repair_cost * coverage_pct / 100 - deductible, max_payout)
            approved_amount = max(0, round(approved_amount, -2))

        claims.append({
            "claim_id": f"CLM-HIST-{i+1:04d}",
            "date": claim_date.strftime("%Y-%m-%d"),
            "policy_number": policy_number,
            "policy_type": policy_type,
            "vehicle_make": make,
            "vehicle_model": model,
            "vehicle_full": vehicle,
            "damage_type": damage_type,
            "damaged_parts": damaged_parts,
            "severity": severity,
            "estimated_repair_cost": repair_cost,
            "approved_amount": approved_amount,
            "claim_description": generate_claim_description(damage_type, damaged_parts),
            "final_decision": decision,
            "fraud_risk": fraud_level,
            "confidence": confidence,
        })

    return claims


def generate_claims_history():
    claims = generate_historical_claims(200)
    path = DATA_DIR / "historical_claims.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"total": len(claims), "claims": claims}, f, indent=2)
    # Also copy to RAG dir
    rag_path = CLAIMS_DIR / "historical_claims.json"
    with open(rag_path, "w", encoding="utf-8") as f:
        json.dump({"total": len(claims), "claims": claims}, f, indent=2)
    print(f"✅ Historical claims ({len(claims)} records) → {path}")


# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n🚀 ClaimSense AI — Generating Datasets\n" + "=" * 50)
    generate_repair_catalog()
    generate_policies()
    generate_fraud_rules()
    generate_claims_history()
    print("\n✨ All datasets generated successfully.")
    print(f"   Data directory : {DATA_DIR}")
    print(f"   RAG directory  : {RAG_DIR}")
    print("\nNext step: python scripts/build_rag.py")
