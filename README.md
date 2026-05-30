# Clause Extractor

This folder has been upgraded into a **standalone real GUI project**.

Run the project GUI:

```bash
./run_gui.sh
```

Windows:

```powershell
.\run_gui_windows.ps1
```

Default local URL: `http://127.0.0.1:9106`

This project includes its own FastAPI backend, browser GUI, provider settings, local/cloud LLM routing, encrypted API-key storage, file uploads, job history, exports, and a project-specific plugin configuration.

See `PROJECT_IMPLEMENTATION.md` and `project_config.json` for the applied project-specific features and customization controls.

---

## Original README

# clause-extractor

> **Any contract → all key clauses extracted, explained, and risk-rated.** Termination, liability cap, IP ownership, non-compete, arbitration, payment terms — in plain English with risk scores.

[![PyPI](https://img.shields.io/pypi/v/clause-extractor?style=flat)](https://pypi.org/project/clause-extractor/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Quickstart

```bash
pip install clause-extractor
python -m clause_extractor contract.pdf
python -m clause_extractor nda.txt --json
cat contract.txt | python -m clause_extractor -
```

## Extracted clauses

Termination · Liability cap · IP ownership · Payment terms · Confidentiality ·
Non-compete · Non-solicitation · Indemnification · Dispute resolution · Warranty · Auto-renewal

## Example output

```
🔴 IP OWNERSHIP
   All work you create under this contract becomes the client's property,
   including any pre-existing tools or code you use in the project.
   ⚠ Watch out: "pre-existing IP" language is unusually broad

🟡 NON COMPETE
   Cannot work for competitors for 12 months after contract ends.
   Geographic scope: United States only.

MISSING CLAUSES
○ Limitation of liability
○ Governing law
```

## Supports

Works on any contract type: NDA, MSA, employment agreements, SaaS terms,
freelance contracts, lease agreements. PDF and plain text.

## License
MIT © [Alper Nabil Gabra Zakher](https://github.com/AlperNab)
