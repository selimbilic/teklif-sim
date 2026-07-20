import os
import streamlit as st
from src.extract import extract_facts
from src.gaps import check_gaps
from src.draft_email import draft_clarification_email
from src.pricing import calculate_quote
from src.summarize import generate_proposal_summary

# Set Streamlit Page Configuration with SEO-friendly titles
st.set_page_config(
    page_title="TEKLİF-Sim | AI Proposal Assistant",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium Styling (Glassmorphism & Gradients)
st.markdown("""
<style>
    /* Main container background */
    .stApp {
        background: radial-gradient(circle at top right, #1a233a 0%, #0d1117 100%);
        color: #c9d1d9;
    }
    
    /* Header Gradient banner */
    .header-banner {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #1d4ed8 100%);
        padding: 2rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        margin-bottom: 2rem;
    }
    .header-title {
        color: #ffffff !important;
        font-family: 'Outfit', 'Inter', sans-serif;
        font-weight: 800;
        letter-spacing: -1px;
        margin: 0;
    }
    .header-subtitle {
        color: #93c5fd !important;
        font-weight: 400;
        margin-top: 0.5rem;
    }
    
    /* Card design for outputs */
    .fact-card {
        background-color: rgba(22, 27, 34, 0.7);
        border: 1px solid rgba(48, 54, 61, 0.8);
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        margin-bottom: 1rem;
    }
    
    /* Highlight styles */
    .highlight-val {
        color: #58a6ff;
        font-weight: bold;
    }
    
    /* Button custom hover */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        font-weight: bold;
        border-radius: 8px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
    }
    div.stButton > button:first-child:hover {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4);
    }
    
    /* Table headers */
    thead tr th {
        background-color: #161b22 !important;
        color: #58a6ff !important;
    }
</style>
""", unsafe_allow_html=True)

# Render Page Header
st.markdown("""
<div class="header-banner">
    <h1 class="header-title" id="main-app-title">TEKLİF-Sim ✈️</h1>
    <p class="header-subtitle">Standalone AI Proposal Assistant for Aircraft Modifications</p>
</div>
""", unsafe_allow_html=True)

# Load Sample Emails
sample_emails_dir = "data/sample_emails"
sample_emails = {}
if os.path.exists(sample_emails_dir):
    for f in sorted(os.listdir(sample_emails_dir)):
        if f.endswith(".txt"):
            with open(os.path.join(sample_emails_dir, f), "r", encoding="utf-8") as file:
                sample_emails[f] = file.read()

# Sidebar Configuration
with st.sidebar:
    st.markdown("### ⚙️ Options / Ayarlar")
    
    # 1. Sample Email Selector
    selected_sample = st.selectbox(
        "Load Sample Email / Örnek E-posta",
        options=["-- Write Custom Email / Kendin Yaz --"] + list(sample_emails.keys())
    )
    
    # 2. Pricing Strategy Selector
    pricing_strategy = st.selectbox(
        "Pricing Strategy / Fiyat Stratejisi",
        options=["cheapest possible", "competitive", "premium / rush", "standard default"],
        index=1
    )
    
    # 3. Drafting Language
    draft_lang = st.radio(
        "Draft Reply Language / Yanıt E-posta Dili",
        options=["TR", "EN"],
        horizontal=True
    )
    
    st.markdown("---")
    st.markdown("*TEKLİF-Sim v1.0. Clean-room synthetic demo environment.*")

# Layout Split: 2 Columns
col_left, col_right = st.columns([1, 1])

# Left Column: Email input
with col_left:
    st.markdown("### 📧 Customer Email / Müşteri E-postası")
    
    # Determine default text based on sample selector
    default_text = ""
    if selected_sample != "-- Write Custom Email / Kendin Yaz --":
        default_text = sample_emails[selected_sample]
        
    email_input = st.text_area(
        "Paste the customer's modification request email here:",
        value=default_text,
        height=350,
        key="customer_email_input"
    )
    
    analyze_btn = st.button(
        "Analyze Email & Generate Quote", 
        key="btn_analyze_email"
    )

# Right Column: Analysis & Costing Output
with col_right:
    st.markdown("### 📊 Output Panel / Sonuç Paneli")
    
    if analyze_btn or (selected_sample != "-- Write Custom Email / Kendin Yaz --" and default_text):
        if not email_input.strip():
            st.warning("Please paste or load an email first!")
        else:
            with st.spinner("Extracting facts and analyzing gaps..."):
                # 1. Fact Extraction (Gemini 3.5 Flash)
                facts = extract_facts(email_input)
                
                # Check validity
                if not facts.is_valid:
                    st.error("❌ The request was classified as INVALID (e.g. spam or unrelated request). No proposal can be generated.")
                else:
                    # 2. Gap analysis (Pure Python)
                    gaps = check_gaps(facts)
                    
                    # 3. Pricing Calculation (Deterministic Pure Python, if no gaps)
                    quote = None
                    if not gaps:
                        # Convert manhours model to dict
                        manhours_dict = facts.manhours.model_dump() if facts.manhours else {}
                        fleet_size = facts.fleet_size if facts.fleet_size else 1
                        
                        quote = calculate_quote(
                            manhours=manhours_dict,
                            customer_class=facts.customer_class,
                            strategy_string=pricing_strategy,
                            fleet_size=fleet_size
                        )
                    
                    # 4. Draft Clarification Email (LLM + Fallback, if gaps exist)
                    draft_email = ""
                    if gaps:
                        draft_email = draft_clarification_email(
                            original_email=email_input,
                            missing_fields=gaps,
                            language=draft_lang
                        )
                        
                    # 5. Proposal Summary (Markdown)
                    summary_md = generate_proposal_summary(
                        facts=facts,
                        gaps=gaps,
                        quote=quote,
                        email_draft=draft_email
                    )
                    
                    # Display Results in Polished Tabs
                    tab_facts, tab_gaps, tab_pricing, tab_summary = st.tabs([
                        "Facts / Olgular", 
                        "Gaps / Eksikler", 
                        "Pricing / Fiyatlandırma", 
                        "Proposal Summary / Teklif Özeti"
                    ])
                    
                    # Tab 1: Extracted Facts Card
                    with tab_facts:
                        st.markdown(f"""
                        <div class="fact-card">
                            <h4>Extracted Request Facts</h4>
                            <hr style="margin: 0.5rem 0 1rem 0; border-color: #30363d;"/>
                            <p><b>Airline Name:</b> <span class="highlight-val">{facts.customer_name}</span></p>
                            <p><b>Customer Class:</b> <span class="highlight-val">{facts.customer_class}</span></p>
                            <p><b>Aircraft Type:</b> <span class="highlight-val">{facts.aircraft_type}</span></p>
                            <p><b>Fleet Size:</b> <span class="highlight-val">{facts.fleet_size}</span></p>
                            <p><b>Modification Category:</b> <span class="highlight-val">{facts.modification_type}</span></p>
                            <p><b>Scope:</b> {facts.scope}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if facts.manhours:
                            st.write("**Extracted Engineering Hours:**")
                            st.json({k: v for k, v in facts.manhours.model_dump().items() if v is not None})
                    
                    # Tab 2: Gaps & Draft Email
                    with tab_gaps:
                        if gaps:
                            st.warning("⚠️ Missing fields detected. Proposal cannot be priced yet.")
                            for gap in gaps:
                                st.checkbox(f"**Missing:** {gap}", value=False, disabled=True, key=f"cb_{gap}")
                                
                            st.markdown("#### Draft Reply Email to Client:")
                            st.text_area("Copy/paste to send:", value=draft_email, height=250, key="ta_draft_email")
                        else:
                            st.success("✅ All information is complete. No gaps detected.")
                            
                    # Tab 3: Pricing Output
                    with tab_pricing:
                        if gaps:
                            st.info("Pricing will be available once the gaps checklist is complete.")
                        else:
                            st.markdown("#### Itemized Quotation Details")
                            st.markdown(f"**Selected Strategy:** `{pricing_strategy}`")
                            
                            # Build a beautiful dataframe
                            cost_table = {
                                "Kalem / Proposal Line": [
                                    "Base Labor / Temel İşçilik",
                                    f"Customer Margin / Kâr Marjı ({quote['margin_applied']*100:.1f}%)",
                                    "Contingency / Beklenmedik Durum Payı (5.0%)",
                                    "Testing & Certification / Sertifikasyon Ücreti",
                                    "Material Allowance / Malzeme Payı"
                                ],
                                "Cost / Tutar": [
                                    f"${quote['base_labor_cost']:,.2f}",
                                    f"${quote['margin_amount']:,.2f}",
                                    f"${quote['contingency']:,.2f}",
                                    f"${quote['testing_fee']:,.2f}",
                                    f"${quote['material_allowance']:,.2f}"
                                ]
                            }
                            st.table(cost_table)
                            
                            st.markdown(f"""
                            <div style="background-color: rgba(56, 139, 253, 0.15); border: 1px solid #388bfd; border-radius: 8px; padding: 1rem; text-align: center;">
                                <h3 style="margin: 0; color: #58a6ff;">TOTAL QUOTE: ${quote['total_cost']:,.2f}</h3>
                            </div>
                            """, unsafe_allow_html=True)
                            
                    # Tab 4: Markdown Proposal Summary
                    with tab_summary:
                        st.markdown(summary_md)
    else:
        st.info("👈 Paste an email on the left or select a sample email to begin analysis.")
