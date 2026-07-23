import os
import sys
# Add project root directory to sys.path to resolve ModuleNotFoundError in Streamlit
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
import streamlit as st
from src.extract import extract_facts
from src.gaps import check_gaps, get_field_description
from src.draft_email import draft_clarification_email
from src.pricing import calculate_quote, load_data_files
from src.summarize import generate_proposal_summary

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="AeroDesign DOA | Proposal Portal",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Corporate Light Styling (Compact & Clean)
st.markdown("""
<style>
    /* Google Fonts import */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Fira+Code:wght@400;500&display=swap');

    /* Global background & text */
    header[data-testid="stHeader"] {
        background-color: #f8fafc !important;
    }
    .stApp {
        background-color: #f8fafc !important;
        color: #0f172a !important;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    
    /* Compact Corporate Header */
    .corporate-header {
        background-color: #ffffff;
        border-bottom: 3px solid #c8102e;
        padding: 1rem 1.5rem;
        margin-bottom: 1.25rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
    }
    .header-title-text {
        color: #0f172a;
        font-size: 1.45rem;
        font-weight: 700;
        margin: 0;
    }
    
    /* Compact Metric Cards */
    .metric-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-top: 3px solid #c8102e;
        border-radius: 6px;
        padding: 0.75rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
    }
    .metric-label {
        font-size: 0.72rem;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-value {
        font-size: 1.2rem;
        font-weight: 700;
        color: #0f172a;
        margin-top: 0.15rem;
    }

    /* Force Light Theme on Streamlit Input Widgets */
    .stTextArea label p, .stSelectbox label p, .stSlider label p, .stRadio label p {
        color: #0f172a !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }
    
    .stTextArea > div > div > textarea {
        background-color: #ffffff !important;
        color: #0f172a !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 6px !important;
        font-family: 'Fira Code', monospace !important;
        font-size: 0.85rem !important;
        line-height: 1.4 !important;
    }
    .stTextArea > div > div > textarea:focus {
        border-color: #c8102e !important;
        box-shadow: 0 0 0 1px #c8102e !important;
    }

    div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #0f172a !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 6px !important;
    }
    div[data-baseweb="select"] span {
        color: #0f172a !important;
        font-weight: 500 !important;
    }

    /* Tabs Styling */
    div[data-baseweb="tab-list"] {
        background-color: transparent !important;
        border-bottom: 2px solid #e2e8f0 !important;
        gap: 1rem !important;
    }
    button[data-baseweb="tab"] {
        background-color: transparent !important;
        color: #64748b !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        padding: 0.4rem 0.6rem !important;
        border: none !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #c8102e !important;
        border-bottom: 3px solid #c8102e !important;
    }

    /* Primary Action Buttons */
    div.stButton > button {
        background-color: #c8102e !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        padding: 0.55rem 1.4rem !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button:hover {
        background-color: #a70d26 !important;
        box-shadow: 0 4px 10px rgba(200, 16, 46, 0.2) !important;
    }
    
    /* Status banners */
    .banner-success {
        background-color: #f0fdf4;
        border: 1px solid #bbf7d0;
        color: #166534;
        padding: 0.75rem 1rem;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.9rem;
        margin-bottom: 0.85rem;
    }
    .banner-warning {
        background-color: #fffbeb;
        border: 1px solid #fef3c7;
        color: #92400e;
        padding: 0.75rem 1rem;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.9rem;
        margin-bottom: 0.85rem;
    }
    .banner-danger {
        background-color: #fef2f2;
        border: 1px solid #fecaca;
        color: #991b1b;
        padding: 0.75rem 1rem;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.9rem;
        margin-bottom: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# Compact Header
st.markdown("""
<div class="corporate-header">
    <h1 class="header-title-text">AeroDesign Engineering Portal</h1>
    <span style="color: #64748b; font-size: 0.85rem;">Aircraft Modification Proposal Assistant</span>
</div>
""", unsafe_allow_html=True)

# Main 2-Column Layout
col_input, col_dashboard = st.columns([1, 1])

with col_input:
    st.markdown("##### 📧 Customer Request Email")
    
    email_input = st.text_area(
        "Paste the customer's modification inquiry email below:",
        value="",
        height=240,
        placeholder="Paste customer email text here...",
        key="main_email_textarea"
    )
    
    st.markdown("##### ⚙️ Configuration:")
    cfg_col1, cfg_col2 = st.columns(2)
    
    with cfg_col1:
        pricing_strategy = st.selectbox(
            "Pricing Strategy",
            options=["cheapest possible", "competitive", "premium / rush", "standard default"],
            index=1,
            key="sb_pricing_strategy"
        )
    with cfg_col2:
        draft_lang = st.radio(
            "Reply Language",
            options=["TR", "EN"],
            horizontal=True,
            key="rb_draft_lang"
        )
        
    analyze_click = st.button("🔍 Analyze & Calculate Proposal", key="btn_analyze")

with col_dashboard:
    st.markdown("##### 📊 Executive Dashboard")
    
    if email_input.strip():
        with st.spinner("Analyzing request facts with Gemini 3.1 Flash Lite..."):
            # 1. Fact Extraction
            facts = extract_facts(email_input)
            
            if not facts.is_valid:
                st.markdown("""
                <div class="banner-danger">
                    ❌ INVALID REQUEST: Flagged as non-aviation / spam. Proposal generation halted.
                </div>
                """, unsafe_allow_html=True)
            else:
                # 2. Gap Checking
                gaps = check_gaps(facts)
                
                # Load rates and classes for bands
                rates, customer_classes = load_data_files()
                c_class = facts.customer_class if (facts.customer_class in customer_classes) else "third_party"
                class_band = customer_classes[c_class]
                
                # 3. Calculate Base Quote
                fleet_sz = facts.fleet_size if (facts.fleet_size and facts.fleet_size > 0) else 1
                manhours_dict = facts.manhours.model_dump() if facts.manhours else {}
                complexity_val = getattr(facts, "complexity", "standard") or "standard"
                
                # Base calculation (falls back to DOA Estimation Engine if customer manhours are empty)
                base_quote = calculate_quote(
                    manhours=manhours_dict,
                    customer_class=c_class,
                    strategy_string=pricing_strategy,
                    fleet_size=fleet_sz,
                    modification_type=facts.modification_type,
                    complexity=complexity_val,
                    scope_text=facts.scope
                )
                
                mh_used = base_quote["manhours_used"]
                mh_source = base_quote["manhour_source"]
                total_hours = sum([v for v in mh_used.values() if v is not None])
                
                # Render 4 Executive KPI Cards
                kpi1, kpi2, kpi3, kpi4 = st.columns(4)
                with kpi1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Aircraft / Fleet</div>
                        <div class="metric-value">{facts.aircraft_type or 'N/A'} ({fleet_sz})</div>
                    </div>
                    """, unsafe_allow_html=True)
                with kpi2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Manhours ({'DOA Est.' if 'DOA' in mh_source else 'Customer'})</div>
                        <div class="metric-value">{total_hours:.0f} hrs</div>
                    </div>
                    """, unsafe_allow_html=True)
                with kpi3:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Margin</div>
                        <div class="metric-value">{base_quote['margin_applied']*100:.1f}%</div>
                    </div>
                    """, unsafe_allow_html=True)
                with kpi4:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Total Quote</div>
                        <div class="metric-value" style="color:#c8102e;">${base_quote['total_cost']:,.2f}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("<div style='margin-bottom: 0.75rem;'></div>", unsafe_allow_html=True)
                
                # Status Banner
                if gaps:
                    st.markdown(f"""
                    <div class="banner-warning">
                        ⚠️ GAPS DETECTED: {len(gaps)} missing field(s) required to finalize proposal.
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="banner-success">
                        ✅ READY FOR PROPOSAL: All facts verified. Itemized quote generated.
                    </div>
                    """, unsafe_allow_html=True)
                    
                # Streamlined 3 Tabs Section
                tab_facts, tab_pricing, tab_summary = st.tabs([
                    "📋 Extracted Facts & Gaps",
                    "💰 Pricing & Margin Sandbox",
                    "📄 Proposal Document"
                ])
                
                # TAB 1: Facts & Gaps
                with tab_facts:
                    st.markdown("###### Extracted Request Metadata:")
                    f_col1, f_col2 = st.columns(2)
                    with f_col1:
                        st.write(f"**Airline:** {facts.customer_name or 'N/A'}")
                        st.write(f"**Class:** `{facts.customer_class or 'N/A'}`")
                        st.write(f"**Aircraft:** {facts.aircraft_type or 'N/A'}")
                    with f_col2:
                        st.write(f"**Mod Category:** `{facts.modification_type or 'N/A'}`")
                        st.write(f"**Fleet Size:** {facts.fleet_size or 'N/A'}")
                        st.write(f"**Scope:** {facts.scope or 'N/A'}")
                    
                    st.markdown("---")
                    st.markdown(f"###### ⏱️ Engineering Manhour Allocation (`{mh_source}`):")
                    mh_col1, mh_col2 = st.columns(2)
                    with mh_col1:
                        st.write(f"- **Cabin Design Engineer:** {mh_used.get('cabin_design_engineer', 0):.1f} hrs")
                        st.write(f"- **Structural Engineer:** {mh_used.get('structural_engineer', 0):.1f} hrs")
                        st.write(f"- **Avionics Design Engineer:** {mh_used.get('avionics_design_engineer', 0):.1f} hrs")
                    with mh_col2:
                        st.write(f"- **Certification Engineer:** {mh_used.get('certification_engineer', 0):.1f} hrs")
                        st.write(f"- **Project Manager:** {mh_used.get('project_manager', 0):.1f} hrs")
                        st.write(f"- **Total Estimated Hours:** `{total_hours:.1f} hrs`")
                        
                    if gaps:
                        st.markdown("---")
                        st.markdown("###### ⚠️ Missing Fields Checklist:")
                        for gap in gaps:
                            st.write(f"- ❌ **{gap}**: {get_field_description(gap)}")
                            
                        st.markdown("###### ✉️ Draft Clarification Email:")
                        draft_body = draft_clarification_email(
                            original_email=email_input,
                            missing_fields=gaps,
                            language=draft_lang
                        )
                        st.text_area("Draft Reply to Customer:", value=draft_body, height=180)

                # TAB 2: Pricing & Interactive Margin Sandbox
                with tab_pricing:
                    st.markdown("###### 🎛️ Interactive Margin Sandbox")
                    st.caption(f"Adjust margin live within customer class band (`{c_class}`: {class_band['min_margin']*100:.0f}% to {class_band['max_margin']*100:.0f}%):")
                    
                    custom_margin_pct = st.slider(
                        "Live Margin Adjustment (%)",
                        min_value=float(class_band["min_margin"] * 100),
                        max_value=float(class_band["max_margin"] * 100),
                        value=float(base_quote["margin_applied"] * 100),
                        step=0.5
                    )
                    
                    # Recalculate quote with sandbox margin
                    sandbox_margin = round(custom_margin_pct / 100.0, 4)
                    base_labor = base_quote["base_labor_cost"]
                    margin_amt = round(base_labor * sandbox_margin, 2)
                    contingency = base_quote["contingency"]
                    testing = base_quote["testing_fee"]
                    materials = base_quote["material_allowance"]
                    final_total = round(base_labor + margin_amt + contingency + testing + materials, 2)
                    
                    st.markdown("###### Itemized Cost Breakdown:")
                    breakdown_df = pd.DataFrame({
                        "Line Item": [
                            "Engineering Base Labor",
                            f"Customer Margin ({custom_margin_pct:.1f}%)",
                            "Contingency Allowance (5.0%)",
                            "Testing & Certification Fee",
                            "Material Allowance"
                        ],
                        "Description": [
                            f"Total {total_hours:.0f} engineering hours",
                            f"Target margin for {c_class}",
                            "Unforeseen technical risks",
                            "Fixed authority approval package",
                            f"Allowance for {fleet_sz} aircraft"
                        ],
                        "Cost (USD)": [
                            f"${base_labor:,.2f}",
                            f"${margin_amt:,.2f}",
                            f"${contingency:,.2f}",
                            f"${testing:,.2f}",
                            f"${materials:,.2f}"
                        ]
                    })
                    st.table(breakdown_df)
                    
                    st.markdown(f"""
                    <div style="background-color: #ffffff; border: 2px solid #c8102e; border-radius: 6px; padding: 0.85rem; text-align: center;">
                        <span style="color: #64748b; font-size: 0.85rem; font-weight: 600;">FINAL NET QUOTE (SANDBOX ADJUSTED)</span>
                        <h3 style="color: #c8102e; margin: 0; font-weight: 800;">${final_total:,.2f} USD</h3>
                    </div>
                    """, unsafe_allow_html=True)

                # TAB 3: Proposal Summary Document
                with tab_summary:
                    summary_text = generate_proposal_summary(
                        facts=facts,
                        gaps=gaps,
                        quote={
                            "base_labor_cost": base_labor,
                            "margin_applied": sandbox_margin,
                            "margin_amount": margin_amt,
                            "contingency": contingency,
                            "testing_fee": testing,
                            "material_allowance": materials,
                            "total_cost": final_total
                        },
                        email_draft="" if not gaps else draft_clarification_email(email_input, gaps, draft_lang)
                    )
                    
                    st.markdown(summary_text)
                    st.download_button(
                        label="📥 Download Proposal Summary (.md)",
                        data=summary_text,
                        file_name="proposal_summary.md",
                        mime="text/markdown"
                    )
    else:
        st.info("👈 Paste a customer inquiry email on the left to begin analysis.")
