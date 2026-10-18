---
title: "FreelanceFlow AI: Zero-Cost, 100% Private Invoice & Expense Copilot Powered by Local Gemma & Ollama"
published: true
tags: devchallenge, hf26challenge, python, opensource, ai
canonical_url: false
cover_image: https://raw.githubusercontent.com/username/freelanceflow-ai/main/docs/banner.png
---

## The Problem: The Freelancer's Financial Headache

As a freelancer or side-hustler, keeping track of business expenses is a tedious tax-time chore. Every month, you receive dozens of PDF invoices and email receipts from SaaS tools (GitHub, Figma, Notion, Slack), cloud providers (AWS, Vercel), co-working desks, and hardware purchases.

Most freelancers solve this in one of two suboptimal ways:
1. **The Manual Spreadsheet Grind:** Typing vendors, dates, tax amounts, and invoice IDs into Excel or Google Sheets by hand. It's error-prone, draining, and easily falls behind.
2. **Paid Cloud Expense Apps:** Tools like Expensify or QuickBooks that charge monthly subscription fees and send your confidential client invoices, bank statements, and receipts to third-party cloud LLM APIs.

When you're running a lean side hustle, paying $30/month for expense management and leaking client invoice data to proprietary cloud models is a dealbreaker.

---

## Enter FreelanceFlow AI: Your Local AI Financial Copilot

**FreelanceFlow AI** is an open-source, local-first invoice and expense manager built for the **Hacktoberfest 2026 Week 2 Side Hustle challenge**.

It runs entirely on your local machine using:
- **Python + Streamlit** for a modern, responsive SaaS-style web interface.
- **Ollama + Google Gemma (gemma2:2b)** for local, zero-cost AI invoice field extraction.
- **PyMuPDF & Tesseract OCR** for parsing native PDF invoices and scanned receipts.
- **SQLite with Parameterized Queries** for safe, relational, ACID-compliant local storage.
- **Pydantic** for rigorous data validation (dates, currencies, float amounts).
- **Plotly** for real-time monthly spending trends and category distribution charts.

No paid APIs. No cloud token bills. 100% data privacy.

---

## What We Built

### 1. Real-Time Financial Dashboard
Get instant visibility into your side hustle cash flow:
- **Core KPI Cards:** Total Spend, Number of Logged Invoices, Average Transaction Cost, and Top Spending Category.
- **Monthly Trend Chart:** Interactive Plotly bar chart tracking monthly deductible spend.
- **Category Donut Chart:** Visual breakdown across 10 standard expense categories (Software, Cloud Hosting, Hardware, Meals, Travel, etc.).
- **Recent Invoices Ledger:** Fast preview of the latest verified expenses.

### 2. Multi-Format Ingestion with Duplicate Detection
Upload any PDF, PNG, or JPG receipt. FreelanceFlow AI:
- Computes an immediate **SHA-256 cryptographic hash** of the file to protect you against accidental double-billing or duplicate deductions.
- Extracts native PDF text with **PyMuPDF** or optical character recognition via **Tesseract OCR**.

### 3. Local Gemma AI Extraction via Ollama
The raw invoice text is sent to a locally running Gemma model through Ollama's REST API. Gemma extracts structured JSON containing:
- Merchant / Vendor name
- Invoice or receipt number
- Normalized transaction date (`YYYY-MM-DD`)
- Currency code (`USD`, `EUR`, `GBP`, `CAD`, etc.)
- Subtotal, Tax/VAT, and Total amount
- Categorization mapped to tax-friendly categories
- Short itemized notes

### 4. Deterministic Human-in-the-Loop Review
AI is great, but financial ledgers require 100% accuracy. Extracted fields populate an interactive form where you can adjust any value with validation guards before committing to SQLite.

### 5. Search, Filter, Edit & CSV Export
Easily search through your receipts by merchant or invoice number, filter by date range, edit records on the fly, and download a complete **CSV export** ready for your accountant or tax software.

### 6. Instant Demo Mode
No Ollama installed yet? No problem! FreelanceFlow AI includes a 1-click **Demo Mode** populated with 12 fictional freelance transactions (Figma, AWS, Copilot, WeWork, Zoom), allowing evaluators to experience the full dashboard immediately.

---

## Architecture Overview

```
┌────────────────────────────────┐
│   Invoice (PDF / PNG / JPG)    │
└───────────────┬────────────────┘
                │
                ▼
┌────────────────────────────────┐
│      invoice_parser.py         │
│  - SHA-256 Duplicate Check     │
│  - PyMuPDF Native PDF Text     │
│  - Tesseract OCR for Images    │
└───────────────┬────────────────┘
                │ Raw Text
                ▼
┌────────────────────────────────┐
│        ai_service.py           │
│  - Ollama REST API Endpoint    │
│  - Google Gemma (gemma2:2b)    │
│  - Pydantic Schema Validation  │
└───────────────┬────────────────┘
                │ Structured JSON
                ▼
┌────────────────────────────────┐
│     Streamlit UI (app.py)      │
│  - Human Review & Edit Form    │
│  - Parameterized SQLite Save   │
│  - Plotly Charts & CSV Export  │
└────────────────────────────────┘
```

---

## The Power of Open-Source Local AI for Freelancers

FreelanceFlow AI demonstrates why the future of developer tools is local:
1. **Confidentiality:** Client names, billing rates, and company tax identifiers never leave your laptop.
2. **Zero Operating Cost:** Once downloaded, Gemma 2 runs for free on commodity hardware (even laptops without dedicated GPUs using Gemma 2B quantized).
3. **Offline Capability:** You can process expenses while working from an airplane, train, or remote coffee shop with no internet connection.

---

## Try It Out!

The complete codebase, documentation, and automated test suite are available on GitHub:

```powershell
# Clone the repo
git clone https://github.com/your-username/freelanceflow-ai.git
cd freelanceflow-ai

# Install dependencies
pip install -r requirements.txt

# Run test suite
python -m pytest tests -v

# Start FreelanceFlow AI
streamlit run app.py
```

Built with ❤️ for Hacktoberfest 2026. Let's keep local open-source AI flourishing!

#devchallenge #hf26challenge #opensource #python #ai
