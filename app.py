"""
app.py - FreelanceFlow AI Streamlit Application
AI-powered invoice and expense manager for freelancers.
Built for the Hacktoberfest 2026 Week 2 Side Hustle challenge.
"""

import io
import os
from datetime import date, datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import ai_service
import database
import invoice_parser

# Page configuration
st.set_page_config(
    page_title="FreelanceFlow AI",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize database
database.init_db()

# Custom Styling for modern SaaS look
st.markdown(
    """
    <style>
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 18px 20px;
        margin-bottom: 12px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25);
    }
    .metric-title {
        font-size: 0.85rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94a3b8;
        margin-bottom: 4px;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #f8fafc;
        line-height: 1.2;
    }
    .metric-sub {
        font-size: 0.75rem;
        color: #38bdf8;
        margin-top: 4px;
    }
    /* Status Badges */
    .status-badge-green {
        display: inline-block;
        background-color: rgba(34, 197, 94, 0.15);
        color: #4ade80;
        border: 1px solid rgba(34, 197, 94, 0.3);
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .status-badge-red {
        display: inline-block;
        background-color: rgba(239, 68, 68, 0.15);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.3);
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .status-badge-amber {
        display: inline-block;
        background-color: rgba(245, 158, 11, 0.15);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.3);
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    /* Header hero */
    .hero-container {
        padding: 10px 0 20px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        margin-bottom: 24px;
    }
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 6px;
    }
    .hero-sub {
        font-size: 0.95rem;
        color: #94a3b8;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --- Helper functions for formatting ---
def format_currency(amount: float, currency: str = "USD") -> str:
    syms = {"USD": "$", "EUR": "€", "GBP": "£", "INR": "₹", "CAD": "CA$"}
    sym = syms.get(currency.upper(), f"{currency} ")
    return f"{sym}{amount:,.2f}"


# --- Sidebar Setup ---
st.sidebar.markdown("### 💼 **FreelanceFlow AI**")
st.sidebar.caption("Private Invoice & Expense Copilot")

# Navigation
page = st.sidebar.radio(
    "Navigation",
    ["📊 Dashboard", "📄 Upload & Extract", "💼 Expense Manager", "🧪 Demo Mode & Data"],
    index=0,
)

st.sidebar.markdown("---")
st.sidebar.markdown("#### ⚙️ **AI Engine & System Status**")

# Ollama Diagnostics in Sidebar
ollama_url = os.environ.get("OLLAMA_BASE_URL", ai_service.DEFAULT_OLLAMA_URL)
ollama_online, available_models, status_note = ai_service.check_ollama_status(ollama_url)

if ollama_online:
    st.sidebar.markdown(
        f'<span class="status-badge-green">● Ollama Connected</span>',
        unsafe_allow_html=True,
    )
    if available_models:
        selected_model = st.sidebar.selectbox(
            "Gemma Model",
            options=available_models,
            index=0 if ai_service.DEFAULT_GEMMA_MODEL not in available_models else available_models.index(ai_service.DEFAULT_GEMMA_MODEL),
        )
    else:
        selected_model = ai_service.DEFAULT_GEMMA_MODEL
        st.sidebar.warning("No models found in Ollama. Run: `ollama pull gemma2:2b`")
else:
    st.sidebar.markdown(
        f'<span class="status-badge-red">● Ollama Offline</span>',
        unsafe_allow_html=True,
    )
    st.sidebar.caption("Run `ollama serve` or use manual entry & Demo Mode.")
    selected_model = ai_service.DEFAULT_GEMMA_MODEL

# OCR Status
ocr_ready, ocr_note = invoice_parser.is_ocr_available()
if ocr_ready:
    st.sidebar.markdown(
        f'<span class="status-badge-green">● OCR Ready</span>',
        unsafe_allow_html=True,
    )
else:
    st.sidebar.markdown(
        f'<span class="status-badge-amber">● PDF Mode (No Tesseract)</span>',
        unsafe_allow_html=True,
    )

st.sidebar.markdown("---")
st.sidebar.caption("🔒 **Data Privacy:** 100% Local SQLite & local Gemma. Zero external APIs, zero data leaks.")


# ==============================================================================
# TAB 1: DASHBOARD
# ==============================================================================
if page == "📊 Dashboard":
    st.markdown(
        """
        <div class="hero-container">
            <div class="hero-title">Financial Dashboard</div>
            <div class="hero-sub">Real-time breakdown of your freelance expenses, tax deductions, and category distribution.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    stats = database.get_summary_stats()
    all_expenses = database.list_expenses()

    if not all_expenses:
        st.info("👋 Welcome to **FreelanceFlow AI**! No expenses have been logged yet.")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🧪 Load Fictional Sample Expenses (Instant Demo)", type="primary", use_container_width=True):
                count = database.load_demo_data()
                st.success(f"Loaded {count} sample expenses! Refreshing...")
                st.rerun()
        with c2:
            st.markdown("Or go to **📄 Upload & Extract** in the sidebar to upload your receipts.")
    else:
        # KPI Cards
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        with kpi1:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-title">Total Spend</div>
                    <div class="metric-value">{format_currency(stats['total_amount'])}</div>
                    <div class="metric-sub">{stats['total_count']} verified invoices</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with kpi2:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-title">Invoices Logged</div>
                    <div class="metric-value">{stats['total_count']}</div>
                    <div class="metric-sub">Across {stats['category_count']} categories</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with kpi3:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-title">Average Expense</div>
                    <div class="metric-value">{format_currency(stats['avg_amount'])}</div>
                    <div class="metric-sub">Per transaction</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with kpi4:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-title">Top Category</div>
                    <div class="metric-value" style="font-size: 1.25rem; text-overflow: ellipsis; overflow: hidden; white-space: nowrap;">
                        {stats['top_category']}
                    </div>
                    <div class="metric-sub">{format_currency(stats['top_category_amount'])} allocated</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        df = pd.DataFrame(all_expenses)
        df["date"] = pd.to_datetime(df["date"])
        df["month_year"] = df["date"].dt.strftime("%Y-%m")

        # Charts Row
        col_chart1, col_chart2 = st.columns([3, 2])

        with col_chart1:
            st.markdown("##### 📈 **Monthly Spending Trend**")
            monthly_df = df.groupby("month_year")["total"].sum().reset_index()
            monthly_df = monthly_df.sort_values("month_year")

            fig_bar = px.bar(
                monthly_df,
                x="month_year",
                y="total",
                labels={"month_year": "Month", "total": "Total Amount ($)"},
                color_discrete_sequence=["#38bdf8"],
                text_auto=".2f",
            )
            fig_bar.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=10, r=10, t=20, b=10),
                height=320,
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        with col_chart2:
            st.markdown("##### 🍩 **Category Distribution**")
            cat_df = df.groupby("category")["total"].sum().reset_index()
            fig_pie = px.pie(
                cat_df,
                names="category",
                values="total",
                hole=0.55,
                color_discrete_sequence=px.colors.qualitative.Prism,
            )
            fig_pie.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=10, r=10, t=20, b=10),
                height=320,
                showlegend=False,
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        # Recent Invoices Table
        st.markdown("##### 🕒 **Recent Invoices**")
        display_df = df[["date", "merchant", "invoice_number", "category", "currency", "total", "notes"]].copy()
        display_df["date"] = display_df["date"].dt.strftime("%Y-%m-%d")
        display_df.rename(
            columns={
                "date": "Date",
                "merchant": "Merchant",
                "invoice_number": "Invoice #",
                "category": "Category",
                "currency": "Cur",
                "total": "Total ($)",
                "notes": "Notes",
            },
            inplace=True,
        )
        st.dataframe(display_df.head(8), use_container_width=True, hide_index=True)


# ==============================================================================
# TAB 2: UPLOAD & EXTRACT
# ==============================================================================
elif page == "📄 Upload & Extract":
    st.markdown(
        """
        <div class="hero-container">
            <div class="hero-title">Upload & AI Extraction</div>
            <div class="hero-sub">Extract merchant, line amounts, tax, and category with local Gemma via Ollama.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Initialize extraction state in session
    if "extracted_data" not in st.session_state:
        st.session_state["extracted_data"] = None
    if "uploaded_file_hash" not in st.session_state:
        st.session_state["uploaded_file_hash"] = None
    if "uploaded_file_name" not in st.session_state:
        st.session_state["uploaded_file_name"] = None
    if "document_raw_text" not in st.session_state:
        st.session_state["document_raw_text"] = None

    uploaded_file = st.file_uploader(
        "Upload Invoice or Receipt (PDF, PNG, JPG)",
        type=["pdf", "png", "jpg", "jpeg", "webp"],
        help="Files are parsed in-memory on your machine. Documents are never transmitted to external servers.",
    )

    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        file_hash = invoice_parser.compute_file_hash(file_bytes)
        st.session_state["uploaded_file_hash"] = file_hash
        st.session_state["uploaded_file_name"] = uploaded_file.name

        # Duplicate Hash Detection
        existing_duplicate = database.check_duplicate_hash(file_hash)
        if existing_duplicate:
            st.warning(
                f"⚠️ **Duplicate Document Detected!** A document with this exact SHA-256 hash was previously saved on "
                f"**{existing_duplicate['date']}** for **{existing_duplicate['merchant']}** "
                f"({format_currency(existing_duplicate['total'], existing_duplicate['currency'])}). "
                f"You can continue if this is an intentional re-entry."
            )

        # Parse text from file
        try:
            with st.spinner("Parsing document text..."):
                parse_res = invoice_parser.parse_document(uploaded_file.name, file_bytes)
                extracted_text = parse_res["text"]
                parse_method = parse_res["method"]
                st.session_state["document_raw_text"] = extracted_text

            st.success(f"Text extracted successfully via **{parse_method}** ({len(extracted_text)} characters)")

            with st.expander("🔍 View Raw Extracted Document Text", expanded=False):
                st.text_area("Extracted Text", extracted_text, height=180, disabled=True)

            # Trigger AI Extraction
            c_ai1, c_ai2 = st.columns([2, 1])
            with c_ai1:
                extract_btn = st.button(
                    "✨ Extract Invoice Details with Gemma AI",
                    type="primary",
                    disabled=not bool(extracted_text.strip()),
                )

            with c_ai2:
                if not ollama_online:
                    st.caption("🔴 Ollama is offline. Click button below to manually enter details.")

            if extract_btn:
                if not ollama_online:
                    st.error(
                        "❌ Cannot run AI extraction because Ollama is not running. "
                        "Please launch Ollama (`ollama serve`) and pull Gemma (`ollama pull gemma2:2b`). "
                        "Alternatively, you can edit and save the fields manually in the form below."
                    )
                else:
                    with st.spinner(f"Sending text to local Gemma model ({selected_model})..."):
                        try:
                            result = ai_service.extract_invoice_data(
                                raw_text=extracted_text,
                                model=selected_model,
                                base_url=ollama_url,
                            )
                            st.session_state["extracted_data"] = result.model_dump()
                            st.success("🎉 AI extraction complete! Please review and confirm the fields below.")
                        except ai_service.OllamaServiceError as e:
                            st.error(f"AI Extraction Failed: {str(e)}")
                            st.info("You can still fill in the details manually and save to the database.")

        except Exception as e:
            st.error(f"Failed to process uploaded file: {str(e)}")
            st.info("You may enter invoice details manually below.")

    st.markdown("---")
    st.markdown("#### 📝 **Review & Save Expense**")

    # Current values for form fields
    data = st.session_state.get("extracted_data") or {}

    def parse_default_date(date_str: str) -> date:
        if date_str:
            try:
                return datetime.strptime(date_str, "%Y-%m-%d").date()
            except Exception:
                pass
        return date.today()

    with st.form("expense_review_form"):
        r1_c1, r1_c2, r1_c3 = st.columns([2, 2, 1])
        with r1_c1:
            form_merchant = st.text_input("Merchant / Vendor *", value=data.get("merchant", ""))
        with r1_c2:
            form_invoice_no = st.text_input("Invoice / Receipt #", value=data.get("invoice_number") or "")
        with r1_c3:
            form_currency = st.selectbox(
                "Currency",
                ["USD", "EUR", "GBP", "CAD", "INR", "AUD", "JPY"],
                index=["USD", "EUR", "GBP", "CAD", "INR", "AUD", "JPY"].index(data.get("currency", "USD"))
                if data.get("currency", "USD") in ["USD", "EUR", "GBP", "CAD", "INR", "AUD", "JPY"]
                else 0,
            )

        r2_c1, r2_c2, r2_c3, r2_c4 = st.columns(4)
        with r2_c1:
            form_date = st.date_input("Invoice Date *", value=parse_default_date(data.get("date")))
        with r2_c2:
            form_subtotal = st.number_input("Subtotal", min_value=0.0, value=float(data.get("subtotal") or 0.0), step=1.0)
        with r2_c3:
            form_tax = st.number_input("Tax / VAT", min_value=0.0, value=float(data.get("tax") or 0.0), step=1.0)
        with r2_c4:
            form_total = st.number_input("Total Amount *", min_value=0.0, value=float(data.get("total") or 0.0), step=1.0)

        r3_c1, r3_c2 = st.columns([2, 3])
        with r3_c1:
            cat_list = database.EXPENSE_CATEGORIES
            default_cat_idx = cat_list.index(data.get("category", "Other")) if data.get("category") in cat_list else cat_list.index("Other")
            form_category = st.selectbox("Category", cat_list, index=default_cat_idx)
        with r3_c2:
            form_notes = st.text_input("Notes / Description", value=data.get("notes") or "")

        submit_save = st.form_submit_button("💾 Save Expense to Database", type="primary", use_container_width=True)

        if submit_save:
            errors = []
            if not form_merchant.strip():
                errors.append("Merchant / Vendor name is required.")
            if form_total <= 0.0:
                errors.append("Total Amount must be greater than $0.00.")

            if errors:
                for err in errors:
                    st.error(f"⚠️ {err}")
            else:
                new_id = database.add_expense(
                    merchant=form_merchant,
                    invoice_number=form_invoice_no,
                    date=form_date.strftime("%Y-%m-%d"),
                    currency=form_currency,
                    subtotal=form_subtotal,
                    tax=form_tax,
                    total=form_total,
                    category=form_category,
                    file_hash=st.session_state.get("uploaded_file_hash"),
                    file_name=st.session_state.get("uploaded_file_name"),
                    notes=form_notes,
                    is_demo=0,
                )
                st.success(f"✅ Expense #{new_id} from **{form_merchant}** saved successfully!")
                # Reset extraction state
                st.session_state["extracted_data"] = None
                st.session_state["uploaded_file_hash"] = None
                st.session_state["uploaded_file_name"] = None


# ==============================================================================
# TAB 3: EXPENSE MANAGER
# ==============================================================================
elif page == "💼 Expense Manager":
    st.markdown(
        """
        <div class="hero-container">
            <div class="hero-title">Expense Manager</div>
            <div class="hero-sub">Filter, edit, delete, and export your expense records for tax prep and accounting.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Filter Bar
    f_c1, f_c2, f_c3, f_c4 = st.columns([3, 2, 2, 2])
    with f_c1:
        search_query = st.text_input("🔍 Search Merchant, Invoice #, Notes", placeholder="e.g. AWS, Figma, Zoom...")
    with f_c2:
        cat_filter = st.selectbox("Category Filter", ["All"] + database.EXPENSE_CATEGORIES)
    with f_c3:
        start_d = st.date_input("Start Date", value=None)
    with f_c4:
        end_d = st.date_input("End Date", value=None)

    start_str = start_d.strftime("%Y-%m-%d") if start_d else None
    end_str = end_d.strftime("%Y-%m-%d") if end_d else None

    filtered_expenses = database.list_expenses(
        search=search_query if search_query else None,
        category=cat_filter if cat_filter != "All" else None,
        start_date=start_str,
        end_date=end_str,
    )

    # Export Bar
    col_exp1, col_exp2 = st.columns([3, 1])
    with col_exp1:
        st.caption(f"Showing **{len(filtered_expenses)}** records matching current filters.")
    with col_exp2:
        if filtered_expenses:
            export_df = pd.DataFrame(filtered_expenses)
            # Exclude internal file_hash for clean CSV export
            cols_to_export = ["id", "date", "merchant", "invoice_number", "currency", "subtotal", "tax", "total", "category", "notes", "file_name", "created_at"]
            available_cols = [c for c in cols_to_export if c in export_df.columns]
            csv_data = export_df[available_cols].to_csv(index=False).encode("utf-8")

            st.download_button(
                label="📥 Export to CSV",
                data=csv_data,
                file_name=f"freelanceflow_expenses_{date.today().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True,
            )

    if not filtered_expenses:
        st.info("No expenses found matching the selected filters.")
    else:
        df_view = pd.DataFrame(filtered_expenses)
        cols_display = ["id", "date", "merchant", "invoice_number", "category", "currency", "total", "notes"]
        st.dataframe(df_view[cols_display], use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("##### ✏️ **Edit or Delete an Expense**")

        e_col1, e_col2 = st.columns([2, 3])
        with e_col1:
            expense_options = {f"#{exp['id']} - {exp['merchant']} ({format_currency(exp['total'], exp['currency'])})": exp['id'] for exp in filtered_expenses}
            selected_label = st.selectbox("Select Record to Modify", list(expense_options.keys()))
            selected_id = expense_options[selected_label]
            target_record = database.get_expense(selected_id)

        with e_col2:
            if target_record:
                with st.expander(f"Edit Expense #{selected_id}", expanded=True):
                    with st.form(f"edit_form_{selected_id}"):
                        ed1, ed2 = st.columns(2)
                        with ed1:
                            e_merchant = st.text_input("Merchant", value=target_record["merchant"])
                            e_inv = st.text_input("Invoice #", value=target_record["invoice_number"] or "")
                            e_cat = st.selectbox(
                                "Category",
                                database.EXPENSE_CATEGORIES,
                                index=database.EXPENSE_CATEGORIES.index(target_record["category"])
                                if target_record["category"] in database.EXPENSE_CATEGORIES
                                else 0,
                            )
                        with ed2:
                            e_date = st.date_input("Date", value=datetime.strptime(target_record["date"], "%Y-%m-%d").date())
                            e_cur = st.selectbox(
                                "Currency",
                                ["USD", "EUR", "GBP", "CAD", "INR", "AUD"],
                                index=["USD", "EUR", "GBP", "CAD", "INR", "AUD"].index(target_record["currency"])
                                if target_record["currency"] in ["USD", "EUR", "GBP", "CAD", "INR", "AUD"]
                                else 0,
                            )
                            e_sub = st.number_input("Subtotal", min_value=0.0, value=float(target_record["subtotal"] or 0.0))
                            e_tax = st.number_input("Tax", min_value=0.0, value=float(target_record["tax"] or 0.0))
                            e_tot = st.number_input("Total Amount", min_value=0.0, value=float(target_record["total"]))

                        e_notes = st.text_input("Notes", value=target_record["notes"] or "")

                        b_save, b_del = st.columns(2)
                        with b_save:
                            save_edit = st.form_submit_button("💾 Save Updates", type="primary", use_container_width=True)
                        with b_del:
                            del_record = st.form_submit_button("🗑️ Delete Record", use_container_width=True)

                        if save_edit:
                            database.update_expense(
                                expense_id=selected_id,
                                merchant=e_merchant,
                                invoice_number=e_inv,
                                date=e_date.strftime("%Y-%m-%d"),
                                currency=e_cur,
                                subtotal=e_sub,
                                tax=e_tax,
                                total=e_tot,
                                category=e_cat,
                                notes=e_notes,
                            )
                            st.success(f"Expense #{selected_id} updated successfully!")
                            st.rerun()

                        if del_record:
                            database.delete_expense(selected_id)
                            st.warning(f"Expense #{selected_id} deleted.")
                            st.rerun()


# ==============================================================================
# TAB 4: DEMO MODE & DATA
# ==============================================================================
elif page == "🧪 Demo Mode & Data":
    st.markdown(
        """
        <div class="hero-container">
            <div class="hero-title">Demo Mode & Database Controls</div>
            <div class="hero-sub">Test FreelanceFlow AI without requiring local Ollama or live invoice uploads.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        **About Demo Mode:**
        Demo Mode populates the local SQLite database with 12 realistic freelance expenses:
        - SaaS tools (Figma, GitHub Copilot, Notion, Google Workspace)
        - Cloud infrastructure (AWS, Vercel)
        - Workspace & equipment (WeWork, Keychron Keyboard)
        - Professional legal advisory & client travel

        This allows judges and hackathon evaluators to test all visualizations, category breakdown, duplicate detection, and CSV export instantly without having an active Ollama instance.
        """
    )

    col_d1, col_d2 = st.columns(2)

    with col_d1:
        st.markdown("#### 🚀 Populate Demo Records")
        if st.button("Load 12 Fictional Sample Expenses", type="primary", use_container_width=True):
            loaded = database.load_demo_data()
            if loaded > 0:
                st.success(f"Successfully inserted {loaded} sample records!")
            else:
                st.info("Demo records are already loaded in database.")
            st.rerun()

    with col_d2:
        st.markdown("#### 🗑️ Reset Database")
        if st.button("Clear All Expenses (Reset)", use_container_width=True):
            deleted = database.clear_all_expenses()
            st.warning(f"Cleared {deleted} expenses from the database.")
            st.rerun()

    st.markdown("---")
    st.markdown("#### 🛡️ Privacy & Local AI Guarantee")
    st.write(
        """
        FreelanceFlow AI was engineered around strict local-first principles:
        1. **Zero Cloud API Subscriptions:** No OpenAI, Anthropic, or external API keys needed.
        2. **Complete Client Data Privacy:** Your financial documents and expenses are never uploaded to any cloud server.
        3. **Deterministic Verification:** The human is always in the loop to review and approve extracted values before saving.
        """
    )
