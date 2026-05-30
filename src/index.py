#!/usr/bin/env python3
"""
clause-extractor — pull key clauses from any contract
Extracts: termination, liability, IP ownership, payment, governing law,
confidentiality, non-compete, indemnification, dispute resolution, warranties
"""
import anthropic
import base64
import json
import re
import sys
from pathlib import Path


SYSTEM = """You are a senior contracts lawyer specializing in contract analysis and risk assessment.

Extract and analyze all key clauses from this contract.
For each clause: quote the relevant text (under 80 words), explain it in plain English,
and rate its risk level.

Return ONLY valid JSON — no markdown, no explanation.

Format:
{
  "contract_type": "NDA|MSA|Employment|SaaS|Lease|Service|Other",
  "parties": [
    { "role": "Client|Vendor|Employee|...", "name": "string or null" }
  ],
  "effective_date": "YYYY-MM-DD or null",
  "term": "contract duration e.g. '12 months' or null",
  "governing_law": "jurisdiction string or null",
  "clauses": {
    "termination": {
      "present": true,
      "quote": "relevant text under 80 words",
      "plain_english": "what this means",
      "notice_period": "e.g. 30 days or null",
      "for_cause_only": true or false,
      "risk": "low|medium|high",
      "notes": "anything unusual"
    },
    "liability_cap": {
      "present": true,
      "quote": "...",
      "plain_english": "...",
      "cap_amount": "e.g. '12 months fees' or null",
      "excludes": ["consequential damages", "..."],
      "risk": "low|medium|high",
      "notes": "..."
    },
    "ip_ownership": {
      "present": true,
      "quote": "...",
      "plain_english": "...",
      "work_for_hire": true or false,
      "you_retain": ["list of what you keep"],
      "they_get": ["list of what they get"],
      "risk": "low|medium|high",
      "notes": "..."
    },
    "payment": {
      "present": true,
      "quote": "...",
      "plain_english": "...",
      "amount": "string or null",
      "schedule": "string or null",
      "late_fees": "string or null",
      "risk": "low|medium|high",
      "notes": "..."
    },
    "confidentiality": {
      "present": true,
      "quote": "...",
      "plain_english": "...",
      "duration": "string or null",
      "exceptions": ["public knowledge", "..."],
      "risk": "low|medium|high",
      "notes": "..."
    },
    "non_compete": {
      "present": true,
      "quote": "...",
      "plain_english": "...",
      "duration": "string or null",
      "geographic_scope": "string or null",
      "scope": "string or null",
      "risk": "low|medium|high",
      "notes": "..."
    },
    "non_solicitation": {
      "present": true,
      "quote": "...",
      "plain_english": "...",
      "duration": "string or null",
      "risk": "low|medium|high",
      "notes": "..."
    },
    "indemnification": {
      "present": true,
      "quote": "...",
      "plain_english": "...",
      "mutual": true or false,
      "risk": "low|medium|high",
      "notes": "..."
    },
    "dispute_resolution": {
      "present": true,
      "quote": "...",
      "plain_english": "...",
      "method": "litigation|arbitration|mediation",
      "arbitration_provider": "string or null",
      "class_action_waiver": true or false,
      "risk": "low|medium|high",
      "notes": "..."
    },
    "warranty": {
      "present": true,
      "quote": "...",
      "plain_english": "...",
      "disclaimer": true or false,
      "risk": "low|medium|high",
      "notes": "..."
    },
    "auto_renewal": {
      "present": true,
      "quote": "...",
      "plain_english": "...",
      "notice_required": "string or null",
      "risk": "low|medium|high",
      "notes": "..."
    }
  },
  "missing_clauses": ["list of important clauses NOT present"],
  "red_flags": [
    { "issue": "description", "severity": "critical|high|medium", "recommendation": "string" }
  ],
  "overall_risk": "low|medium|high|critical",
  "summary": "3-4 sentence plain-English summary of this contract",
  "confidence": 0.0
}"""


def read_doc(path: Path) -> list:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        data = base64.standard_b64encode(path.read_bytes()).decode("ascii")
        return [
            {"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": data}},
            {"type": "text", "text": "Extract all key clauses from this contract."}
        ]
    text = path.read_text(encoding="utf-8", errors="replace")
    if len(text) > 60000:
        text = text[:60000] + "\n[truncated]"
    return [{"type": "text", "text": f"Extract all key clauses from this contract:\n\n{text}"}]


def extract(file_path: str) -> dict:
    client = anthropic.Anthropic()
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Not found: {file_path}")

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=SYSTEM,
        messages=[{"role": "user", "content": read_doc(path)}]
    )

    raw = response.content[0].text.strip()
    raw = re.sub(r'^```(?:json)?\s*', '', raw, flags=re.MULTILINE)
    raw = re.sub(r'\s*```$', '', raw, flags=re.MULTILINE)
    return json.loads(raw)


def extract_from_text(text: str) -> dict:
    client = anthropic.Anthropic()
    if len(text) > 60000:
        text = text[:60000]
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=SYSTEM,
        messages=[{"role": "user", "content": f"Extract all key clauses:\n\n{text}"}]
    )
    raw = response.content[0].text.strip()
    raw = re.sub(r'^```(?:json)?\s*', '', raw, flags=re.MULTILINE)
    raw = re.sub(r'\s*```$', '', raw, flags=re.MULTILINE)
    return json.loads(raw)


RISK_ICON = {"low": "🟢", "medium": "🟡", "high": "🔴", "critical": "💀"}

def print_report(result: dict):
    overall = result.get("overall_risk", "medium")
    print(f"\n{'═'*60}")
    print(f"  CLAUSE EXTRACTOR — {result.get('contract_type','Contract')}")
    print(f"  Overall Risk: {RISK_ICON.get(overall,'')} {overall.upper()}")
    print(f"{'═'*60}")

    parties = result.get("parties", [])
    if parties:
        print(f"\n  Parties: {', '.join(f\"{p.get('role','?')}: {p.get('name','?')}\" for p in parties)}")
    if result.get("effective_date"):
        print(f"  Effective: {result['effective_date']}")
    if result.get("term"):
        print(f"  Term: {result['term']}")
    if result.get("governing_law"):
        print(f"  Governing law: {result['governing_law']}")

    print(f"\n  Summary: {result.get('summary','')}")

    clauses = result.get("clauses", {})
    present = {k: v for k, v in clauses.items() if v and v.get("present")}
    if present:
        print(f"\n{'─'*60}")
        print(f"  KEY CLAUSES ({len(present)} found)")
        print(f"{'─'*60}")
        for name, clause in present.items():
            risk = clause.get("risk", "low")
            print(f"\n  {RISK_ICON.get(risk,'')} {name.upper().replace('_',' ')}")
            print(f"     {clause.get('plain_english','')}")
            if clause.get("notes"):
                print(f"     ⚠ {clause['notes']}")
            if clause.get("quote"):
                q = clause["quote"]
                print(f"     \"{q[:100]}{'...' if len(q)>100 else ''}\"")

    missing = result.get("missing_clauses", [])
    if missing:
        print(f"\n{'─'*60}")
        print(f"  MISSING CLAUSES")
        for m in missing:
            print(f"  ○ {m}")

    flags = result.get("red_flags", [])
    if flags:
        print(f"\n{'─'*60}")
        print(f"  RED FLAGS")
        sev_icon = {"critical": "🚨", "high": "🔴", "medium": "🟠"}
        for f in flags:
            print(f"  {sev_icon.get(f.get('severity','medium'),'')} {f.get('issue','')}")
            if f.get("recommendation"):
                print(f"     → {f['recommendation']}")

    print(f"\n  Confidence: {int(result.get('confidence',0)*100)}%")
    print(f"{'═'*60}\n")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print("Usage: python -m clause_extractor <contract.txt|.pdf> [--json]")
        sys.exit(0)

    if args[0] == "-":
        result = extract_from_text(sys.stdin.read())
    else:
        result = extract(args[0])

    if "--json" in args:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print_report(result)
