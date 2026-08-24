# AI-Powered National Professor Research Matching & Cold Email Agent

A zero-cost, locally-hosted academic cold email and research matching agent built with **FastAPI, SQLite, ReportLab, Ollama, and n8n**.

Targeting premier faculty across **IIT, IIIT, IISc, NIT, IISER, ISB, and IIM** institutes.

---

## 🏛️ Supported National Institutes & Faculty Tiers

* **IITs (23 Indian Institutes of Technology):** IIT Bombay, IIT Delhi, IIT Madras, IIT Kanpur, IIT Kharagpur, IIT Roorkee, IIT Guwahati, IIT Hyderabad, IIT BHU, IIT Indore, IIT Gandhinagar, IIT Ropar, IIT Patna, IIT Jodhpur, IIT Mandi, IIT Bhubaneswar, IIT Tirupati, IIT Palakkad, IIT Goa, IIT Dharwad, IIT Jammu, IIT Bhilai, IIT ISM Dhanbad.
* **IIITs (Premier Information Technology Institutes):** IIIT Hyderabad (CVIT, LTRC, RRC), IIIT Delhi, IIIT Bangalore, IIIT Allahabad, ABV-IIITM Gwalior, IIITDM Jabalpur, IIITDM Kancheepuram, IIIT Sri City, IIIT Guwahati, IIIT Vadodara, IIIT Pune, IIIT Lucknow, etc.
* **IISc Bangalore:** CSA (Computer Science & Automation), CDS (Computational & Data Sciences), EE, ECE, RBCCPS.
* **NITs (National Institutes of Technology):** NIT Warangal, NIT Trichy, NIT Surathkal, NIT Calicut, NIT Rourkela, VNIT Nagpur, MNIT Jaipur, MNNIT Allahabad, SVNIT Surat, etc.
* **IISERs (Science Education & Research):** IISER Pune, IISER Kolkata, IISER Mohali, IISER Bhopal, IISER Thiruvananthapuram, IISER Tirupati, IISER Berhampur.
* **ISB (Business & Analytics):** ISB Hyderabad, ISB Mohali (Applied AI, Big Data & Quantitative Decision Analytics).
* **IIMs (Indian Institutes of Management):** IIM Bangalore (DCAL), IIM Ahmedabad, IIM Calcutta, IIM Lucknow, IIM Kozhikode, IIM Indore, IIM Mumbai (Decision Sciences, AI & Analytics).

---

## 📁 Project Structure

```text
iit_cold_email_agent/
│
├── data/
│   ├── candidate_profile.json      # Master candidate profile (pre-seeded with verified CV)
│   └── agent.db                    # SQLite database (auto-created on first run)
│
├── assets/
│   └── your_Resume.pdf     # Master candidate resume PDF
│
├── generated_cover_letters/        # Formatted Cover_Letter_Prof_<Name>.pdf files
│
├── src/
│   ├── __init__.py
│   ├── database.py                 # SQLite schema & duplicate protection queries
│   ├── scraper.py                  # Comprehensive Multi-Tier National Faculty Catalog & Name Resolver
│   ├── matching_engine.py          # Multi-factor score calculator (40/25/20/10/5)
│   ├── research_analyzer.py        # Deep paper synergy and publication alignment engine
│   ├── ollama_client.py            # Local Ollama connector for research alignment
│   ├── email_generator.py          # Dynamic email body & cover letter payload generator
│   ├── pdf_generator.py            # ReportLab PDF engine matching master layout
│   ├── gmail_sender.py             # Gmail SMTP SSL dispatcher with attachments
│   ├── followup_engine.py          # Automated polite follow-up generator (7-day trigger)
│   └── main.py                     # FastAPI REST server & Review Dashboard
│
├── n8n_workflow.json               # Ready-to-import n8n orchestration workflow
├── requirements.txt                # Python dependencies
├── test_pipeline.py                # End-to-end multi-tier integration test
└── README.md
```

---

## 🚀 Quick Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Multi-Tier Integration Test
Run the automated test to verify discovery across IIT, IIIT, IISc, NIT, IISER, ISB, and IIM:
```bash
python test_pipeline.py
```

### 3. Start the FastAPI Backend & Review Dashboard
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

* **Interactive API Docs:** `http://localhost:8000/docs`
* **Visual Review Dashboard:** `http://localhost:8000/dashboard`

---

## 🎯 API Discovery Parameters

You can query specific tiers or all national institutes:
```json
POST /api/professors/discover-and-rank
{
  "institution_type": "ALL",       // Options: "ALL", "IIT", "IIIT", "IISc", "NIT", "IISER", "ISB", "IIM"
  "institution_name": "Hyderabad", // Optional filter (e.g. "IIIT Hyderabad", "IIT Bombay")
  "research": "Machine Learning Computer Vision Deep Learning",
  "threshold": 70.0
}
```
