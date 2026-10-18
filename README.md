# 💼 FreelanceFlow AI — Private AI Expense & Invoice Copilot

> Built for the **Hacktoberfest 2026 Week 2 Side Hustle challenge** (#devchallenge, #hf26challenge).

**FreelanceFlow AI** is a 100% local, privacy-first invoice and expense manager designed specifically for freelancers, solopreneurs, and contractors. It turns messy PDF invoices and receipt images into structured, categorized tax-ready expense records using a locally running **Google Gemma** model served through **Ollama** and a local **SQLite** database.

---

## 🌟 Why FreelanceFlow AI?

As a freelancer, keeping track of deductible business expenses usually means juggling PDF receipts, taking screenshots of SaaS invoices, and spending hours each quarter manually typing numbers into spreadsheets.

Cloud AI alternatives exist, but they have major drawbacks:
1. **Financial Privacy Risks:** Uploading bank statements, NDA-bound invoices, and personal receipts to third-party cloud LLM APIs poses severe confidentiality issues.
2. **Recurring Token Costs:** Monthly SaaS fees and API bills eat away at freelance margins.
3. **Vendor Lock-In:** Your expense history is trapped behind someone else's walled garden.

**FreelanceFlow AI solves this with 100% Local AI:**
- **Zero Cloud API Subscriptions:** Powered by local Gemma via Ollama.
- **Complete Data Sovereignty:** All database records and parsed documents stay on your machine in a single SQLite file.
- **Deterministic Human-in-the-Loop:** AI extracts, but you review and approve before anything is committed to your books.
- **Instant Demo Mode:** Works out of the box with realistic fictional freelancer expenses even before configuring Ollama.

---

## 🚀 Key Features

| Feature | Description |
| :--- | :--- |
| **📊 Real-Time Dashboard** | Visual breakdown of total spend, invoice counts, average transaction, top spending categories, monthly trend bar charts, and category donut charts using Plotly. |
| **📄 Multi-Format Ingestion** | Extracts text from native PDF invoices using **PyMuPDF** and scanned receipt images (PNG, JPG, WEBP) using **Tesseract OCR**. |
| **🤖 Local Gemma AI Extraction** | Prompts local Gemma via Ollama with strict JSON schema enforcement to extract Merchant, Invoice #, Date, Currency, Subtotal, Tax, Total, and Category. |
| **🛡️ Duplicate Detection** | Computes cryptographic **SHA-256** digests on upload to warn you immediately if an invoice was already processed. |
| **✏️ Review & Save** | Interactive editable form with date/currency validation and automated error checking before inserting into SQLite with parameterized queries. |
| **💼 Expense Manager** | Real-time search by merchant/invoice/notes, filter by category and date range, with full in-place record editing and deletion. |
| **📥 CSV Export** | 1-click export of all filtered expense records ready for accountant review or import into QuickBooks / Excel. |
| **🧪 Demo Mode** | Pre-loaded with 12 realistic fictional freelance expenses (Figma, AWS, GitHub Copilot, WeWork, Zoom, etc.) so judges can test without installing Ollama. |

---

## 🏗️ Architecture

```
[ PDF Invoices / Receipts (PNG/JPG) ]
                  │
                  ▼
         [ invoice_parser.py ]
   ├── SHA-256 Duplicate Check ──> [ SQLite expenses.db ]
   ├── PyMuPDF (Native PDF Text)
   └── Tesseract OCR (Image Text)
                  │
                  ▼ Raw Extracted Text
         [ ai_service.py ]
   └── Ollama REST API (http://localhost:11434)
         └── Gemma 2 (e.g. gemma2:2b / gemma:2b)
                  │
                  ▼ JSON Extraction
         [ Pydantic Validation ]
   └── (Validates currency, date YYYY-MM-DD, float amounts)
                  │
                  ▼
         [ Streamlit UI (app.py) ] ◄── Human Review & Approval
                  │
                  ▼ Parameterized SQL
         [ database.py (SQLite) ]
                  │
                  ▼
    [ Plotly Charts & CSV Export ]
```

---

## 💻 Windows Setup & Installation

### Prerequisites
- **Python 3.10+** (Tested on Python 3.12.1 Windows 64-bit)
- **Git**
- *(Optional for AI)* **Ollama for Windows**
- *(Optional for image OCR)* **Tesseract OCR for Windows**

---

### Step 1: Clone or Navigate to the Repository

```powershell
cd C:\Users\snehal\.gemini\antigravity-ide\scratch\freelanceflow-ai
```

### Step 2: Set up a Python Virtual Environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Step 3: Install Python Dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

### Step 4: Configure Local AI with Ollama (Optional for Live AI Extraction)

If you wish to use live Gemma AI extraction:
1. Download and install Ollama from [ollama.com/download/windows](https://ollama.com/download/windows).
2. Pull the Gemma model in your terminal:
   ```powershell
   ollama pull gemma2:2b
   ```
3. Start the Ollama server (it typically runs automatically in the Windows system tray):
   ```powershell
   ollama serve
   ```
4. Verify by browsing to `http://localhost:11434/api/tags`.

> **Note:** If Ollama is not installed or running, FreelanceFlow AI gracefully falls back to manual entry mode and provides a 1-click **Demo Mode** populated with realistic freelance transactions!

---

### Step 5: (Optional) Install Tesseract OCR for Image Receipts

For scanning JPG/PNG receipts:
1. Download the Windows installer from [UB-Mannheim Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki).
2. Install to the default directory (`C:\Program Files\Tesseract-OCR`).
3. FreelanceFlow AI will automatically detect `tesseract.exe`. Native PDF text extraction using PyMuPDF works out-of-the-box without Tesseract!

---

### Step 6: Launch FreelanceFlow AI

Run the Streamlit application:

```powershell
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`.

---

## 🧪 Running the Test Suite

We provide a comprehensive unit test suite covering database ACID operations, duplicate SHA-256 detection, Pydantic schema validation, and PDF parser routines:

```powershell
python -m pytest tests -v
```

All 13 unit tests should pass with 100% green status.

---

## 📁 Project Structure

```
freelanceflow-ai/
├── app.py                 # Streamlit UI with SaaS layout, dashboard, forms, and charts
├── database.py            # SQLite database schema, CRUD, parameterized queries & demo data
├── ai_service.py          # Ollama REST client, Gemma prompt engineer, & Pydantic validation
├── invoice_parser.py      # PyMuPDF PDF extractor, Tesseract OCR wrapper & SHA-256 hashing
├── requirements.txt       # Project dependencies
├── .env.example           # Example configuration variables
├── .gitignore             # Git ignore file excluding DBs, virtualenvs, and uploaded files
├── README.md              # Documentation and Windows setup guide
├── tests/                 # Unit test suite
│   ├── test_database.py
│   ├── test_ai_service.py
│   └── test_invoice_parser.py
└── docs/
    └── hacktoberfest-post.md # DEV Community submission draft (#devchallenge #hf26challenge)
```

---

## 🔒 Security & Privacy

- **SQL Injection Prevention:** All SQL queries strictly use parameterized queries (`?` placeholders).
- **Zero Cloud Leakage:** Documents are processed in-memory. Database records live only in `freelanceflow.db`.
- **Duplicate Prevention:** SHA-256 checksums warn users against accidental double-billing or duplicate deductions.

---

## 📜 License
MIT License. Built with ❤️ for open-source AI and the freelance developer community.
