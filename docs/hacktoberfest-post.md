---
title: "FreelanceFlow AI: 100% Private, Zero-Cost Invoice & Expense Copilot Powered by Local Gemma & Ollama"
published: true
tags: devchallenge, hf26challenge, python, opensource, ai
canonical_url: false
---

*This is a submission for the [Hacktoberfest Open-Source AI Challenge Week 2: Side Hustle](https://dev.to/challenges/hacktoberfest-week2-2026-10-12)*

## What I Built

**FreelanceFlow AI** is a 100% local, privacy-first invoice and expense manager designed specifically for freelancers, solopreneurs, and independent contractors. 

### The Problem
At the end of every month or tax season, freelancers face a painful chore: hunting down dozens of digital receipts and PDF invoices scattered across email inboxes and downloads folders (GitHub Copilot, Figma, AWS, Vercel, WeWork, Zoom, client dinners, and hardware purchases). Today, they have two frustrating choices:
1. **The Manual Spreadsheet Grind:** Manually typing invoice numbers, dates, tax amounts, and vendors into Excel or Google Sheets. It takes hours, leads to typos, and frequently causes missed tax write-offs.
2. **Expensive Cloud SaaS Apps:** Paying $20–$50/month for tools like Expensify, Dext, or QuickBooks that upload confidential financial documents, client names, and bank statements to proprietary cloud LLM APIs.

### Who Would Use & Pay for It?
Freelancers and solopreneurs running lean side hustles who care deeply about:
- **Financial Data Confidentiality:** Keeping client billing records, NDAs, and receipts strictly on their own machines.
- **Eliminating Recurring SaaS Fees:** Paying zero monthly AI token or subscription fees.
- **Tax Readiness:** Getting clean, categorized summaries and 1-click CSV exports ready for tax deductions and accountant handoffs.

---

## Demo

The app features a modern, responsive SaaS-style interface powered by Streamlit and Plotly:

- **📊 Financial Health Dashboard:** 4 real-time KPI metric cards (Total Spend, Invoices Logged, Average Expense, and Top Category), plus interactive Plotly visualizations for monthly spending trends and category distribution.
- **📄 Smart Document Ingestion:** Drag-and-drop support for PDF invoices and receipt images (PNG, JPG, WEBP).
- **🛡️ Instant Duplicate Detection:** Computes a cryptographic SHA-256 hash on upload and alerts you immediately if a document was already entered, preventing double deductions.
- **🤖 Gemma AI Extraction with Human-in-the-Loop:** Automatically parses Vendor, Invoice #, Date, Currency, Subtotal, Tax, Total, and Category into an editable confirmation form.
- **💼 Full Expense Manager:** Filter by category, search by vendor/notes, adjust records in-place, and export clean CSVs.
- **🧪 1-Click Demo Mode:** Includes 12 pre-loaded fictional freelance expenses (Figma, GitHub, AWS, WeWork, Zoom, etc.) so judges can test every feature instantly without needing an active Ollama instance.

A ready-to-test sample invoice ([`sample_invoice.pdf`](https://github.com/snehalghadge59-blip/freelanceflow-ai/blob/main/sample_invoice.pdf)) is included in the repository.

---

## Code

{% github https://github.com/snehalghadge59-blip/freelanceflow-ai %}

The repository includes the full source code, test suite, and Windows setup instructions:
- `app.py`: Modern SaaS UI, interactive charts, and review forms
- `database.py`: Parameterized SQLite queries, duplicate hash checks, and demo data generator
- `ai_service.py`: Local Ollama REST client, Gemma prompt engineer, and Pydantic validation
- `invoice_parser.py`: PyMuPDF native PDF text extraction, Tesseract OCR wrapper, and SHA-256 hashing
- `tests/`: 13 passing unit tests verifying ACID compliance, Pydantic normalization, and document parsing

---

## How I Built It

FreelanceFlow AI is built entirely on open-source technologies and local-first architecture:

```
[ PDF / Image Receipts ]
           │
           ▼
  [ invoice_parser.py ] ──► Computes SHA-256 Hash ──► Duplicate Check
  ├── PyMuPDF (Native PDF Text Extraction)
  └── Tesseract OCR (Image Text Extraction)
           │
           ▼ Raw Document Text
    [ ai_service.py ]
  └── Ollama REST API (http://localhost:11434)
        └── Google Gemma 2 (gemma2:2b / gemma:2b)
           │
           ▼ Strict JSON Extraction
    [ Pydantic Validation ]
  └── Cleans currency symbols ($/€/£), formats dates (YYYY-MM-DD), validates totals
           │
           ▼
    [ Streamlit UI (app.py) ] ◄── Human Verification & Edit
           │
           ▼ Parameterized SQL (Zero Injection)
    [ SQLite database.py ] ──► Plotly Visualizations & CSV Export
```

### Key Components:
1. **Open-Weight AI Model:** Google's **Gemma 2 (`gemma2:2b`)** served locally via **Ollama**. Gemma's compact size and high reasoning quality allow it to reliably extract structured financial JSON on standard laptops without requiring a discrete GPU.
2. **Deterministic Data Validation:** All LLM outputs are piped into a strict **Pydantic** model (`InvoiceExtractionResult`) that normalizes currency symbols, enforces `YYYY-MM-DD` ISO dates, rounds monetary figures, and maps vendors to standardized tax expense categories.
3. **Local Text Extraction:** **PyMuPDF (`pymupdf`)** extracts clean text from multi-page PDF invoices in milliseconds, while **Pillow + Tesseract OCR** provides scanned receipt parsing.
4. **Relational Storage:** **SQLite** with parameterized queries (`?`) guarantees data safety and SQL injection protection.

---

## Why Does Open Innovation Matter?

Open innovation is essential for personal financial software:

1. **Complete Data Sovereignty & Confidentiality:** Financial receipts contain sensitive client names, business addresses, tax IDs, and bank account snippets. Sending this data to closed cloud APIs risks leakage and unauthorized training on user financial habits. Open-weight models like Gemma run entirely on your local machine with zero external network requests.
2. **Zero Marginal Operating Costs:** Closed AI APIs charge per token and impose rate limits. Open-source local models allow freelancers to parse thousands of invoices completely free of charge.
3. **Offline Reliability:** Freelancers frequently travel and work from airplanes, trains, or remote spots with intermittent connectivity. Because both SQLite and Gemma run locally, FreelanceFlow AI works seamlessly completely off-grid.
4. **Resilience to Deprecation:** Closed APIs change pricing, modify model behaviors, or shut down endpoints at will. With open-source code and local weights, your expense tool will function predictably for years.

---

## My First User

I shared the MVP with a freelance web designer who typically accumulates 15–20 software and client-meeting receipts every month. 

They tested it with their recent invoices (DigitalOcean hosting, Figma subscription, and an ergonomic keyboard purchase). Their feedback:
> *"The duplicate warning alone saved me from logging the same $12 cloud invoice twice. I love that it doesn't require a monthly subscription like QuickBooks, and having an instant CSV ready for tax prep at the end of the year is a lifesaver."*

---

## Prize Categories

- **Hacktoberfest Open-Source AI Challenge Week 2: Side Hustle**

---

<!-- Thanks for participating! -->
