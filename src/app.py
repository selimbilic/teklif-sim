import os
import sys
import html
from typing import Any
# Add project root directory to sys.path to resolve ModuleNotFoundError in Streamlit
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
import streamlit as st
import importlib
import src.estimation
import src.pricing
import src.extract
import src.gaps
import src.draft_email
import src.summarize
import src.__version__

importlib.reload(src.estimation)
importlib.reload(src.pricing)
importlib.reload(src.extract)
importlib.reload(src.gaps)
importlib.reload(src.draft_email)
importlib.reload(src.summarize)
importlib.reload(src.__version__)

from src.extract import extract_facts, extract_facts_cached
from src.gaps import check_gaps, get_field_description
from src.draft_email import draft_clarification_email
from src.pricing import calculate_quote, load_data_files, get_urgency_surcharge
from src.summarize import generate_proposal_summary
from src.__version__ import __version__
from src.estimation import resolve_cert_basis, classify_part21_change

def safe_html(val: Any) -> str:
    """Sanitizes user and LLM string inputs against HTML injection / XSS attacks."""
    if val is None:
        return "N/A"
    return html.escape(str(val))

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
st.markdown(f"""
<div class="corporate-header" style="display: flex; justify-content: space-between; align-items: center;">
    <div>
        <h1 class="header-title-text" style="display: inline-block; margin-right: 10px;">AeroDesign Engineering Portal</h1>
        <span style="color: #64748b; font-size: 0.85rem;">Aircraft Modification Proposal Assistant</span>
    </div>
    <span style="background-color: #f1f5f9; color: #475569; padding: 4px 10px; border-radius: 12px; font-size: 0.78rem; font-weight: 600; border: 1px solid #cbd5e1;">v{__version__}</span>
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
    st.caption("🔒 **Privacy & Data Security Notice:** This system uses public Gemini API for extraction. Do NOT input confidential or personal customer data. Use synthetic data only.")

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
    
    clean_email = email_input.strip()
    is_new_click = bool(analyze_click and clean_email)
    is_already_analyzed = bool(st.session_state.get("analyzed_email") == clean_email and clean_email)
    
    if is_new_click or is_already_analyzed:
        if is_new_click and not is_already_analyzed:
            with st.spinner("Analyzing request facts with Gemini 3.1 Flash Lite..."):
                facts = extract_facts_cached(clean_email)
                st.session_state["analyzed_facts"] = facts
                st.session_state["analyzed_email"] = clean_email
        else:
            facts = st.session_state.get("analyzed_facts") or extract_facts_cached(clean_email)
            
        err_type = getattr(facts, "error_type", None)
        err_msg = getattr(facts, "error_message", None)
        
        if err_type == "missing_api_key":
            st.markdown(f"""
            <div class="banner-danger" style="padding: 1rem; line-height: 1.5;">
                🔑 <b>CONFIG WARNING: GEMINI_API_KEY NOT FOUND</b><br>
                <span style="font-size: 0.85rem; color: #7f1d1d;">{safe_html(err_msg) if err_msg else 'GEMINI_API_KEY is not configured in your environment variables or .env file.'}</span><br>
                <span style="font-size: 0.82rem; color: #991b1b; display: block; margin-top: 4px;">Please create a <code>.env</code> file in the project root with <code>GEMINI_API_KEY=your_key_here</code> to enable AI extraction.</span>
            </div>
            """, unsafe_allow_html=True)
        elif err_type == "quota_exceeded":
            st.markdown(f"""
            <div class="banner-danger" style="padding: 1rem; line-height: 1.5;">
                ⏳ <b>RATE LIMIT / QUOTA EXHAUSTED (429)</b><br>
                <span style="font-size: 0.85rem; color: #7f1d1d;">{safe_html(err_msg) if err_msg else 'Gemini API rate limit or quota exceeded.'}</span><br>
                <span style="font-size: 0.82rem; color: #991b1b; display: block; margin-top: 4px;">The free API rate limit or quota has been reached. Please wait a few moments before trying again or verify your Gemini API plan.</span>
            </div>
            """, unsafe_allow_html=True)
        elif err_type == "api_error":
            st.markdown(f"""
            <div class="banner-danger" style="padding: 1rem; line-height: 1.5;">
                🌐 <b>API COMMUNICATION ERROR</b><br>
                <span style="font-size: 0.85rem; color: #7f1d1d;">{safe_html(err_msg) if err_msg else 'Failed to communicate with Gemini API service.'}</span><br>
                <span style="font-size: 0.82rem; color: #991b1b; display: block; margin-top: 4px;">Please check your network connection or verify API service status.</span>
            </div>
            """, unsafe_allow_html=True)
        elif not facts.is_valid:
            st.markdown("""
            <div class="banner-danger" style="padding: 1rem; line-height: 1.5;">
                ❌ <b>INVALID REQUEST: NON-AVIATION / SPAM</b><br>
                <span style="font-size: 0.85rem; color: #7f1d1d;">The submitted e-mail inquiry does not appear to be an aircraft engineering modification request (e.g. spam, catering, marketing, personal). Proposal generation halted.</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            # 2. Gap Checking
            gaps = check_gaps(facts)
            
            # Load rates and classes for bands
            rates, customer_classes = load_data_files()
            c_class = facts.customer_class if (facts.customer_class in customer_classes) else "third_party"
            class_band = customer_classes[c_class]
            
            # 3. Calculate Base Quote (ONLY if no gaps exist)
            fleet_sz = facts.fleet_size if (facts.fleet_size and facts.fleet_size > 0) else 1
            manhours_dict = facts.manhours.model_dump() if facts.manhours else {}
            complexity_val = getattr(facts, "complexity", "standard") or "standard"
            
            if not gaps:
                base_quote = calculate_quote(
                    manhours=manhours_dict,
                    customer_class=c_class,
                    strategy_string=pricing_strategy,
                    fleet_size=fleet_sz,
                    modification_type=facts.modification_type,
                    complexity=complexity_val,
                    scope_text=facts.scope,
                    aircraft_type=facts.aircraft_type,
                    dal_level=getattr(facts, "dal_level", None)
                )
                mh_used = base_quote["manhours_used"]
                mh_source = base_quote["manhour_source"]
                total_hours = sum([v for v in mh_used.values() if v is not None])
                margin_pct_str = f"{base_quote['margin_applied']*100:.1f}%"
                total_quote_str = f"${base_quote['total_cost']:,.2f}"
                quote_color = "#c8102e"
                urgency_mult = base_quote.get("urgency_multiplier", 1.0)
            else:
                base_quote = None
                mh_used = {}
                mh_source = "Pending Gaps"
                total_hours = 0.0
                margin_pct_str = "Pending Gaps"
                total_quote_str = "PENDING GAPS"
                quote_color = "#d97706"
                
            # Render 4 Executive KPI Cards
            kpi1, kpi2, kpi3, kpi4 = st.columns(4)
            with kpi1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Aircraft / Fleet</div>
                    <div class="metric-value">{safe_html(facts.aircraft_type)} ({safe_html(facts.fleet_size)})</div>
                </div>
                """, unsafe_allow_html=True)
            with kpi2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Manhours ({'DOA Est.' if 'DOA' in mh_source else ('Customer' if not gaps else 'Pending')})</div>
                    <div class="metric-value">{"Pending Gaps" if gaps else f"{total_hours:.0f} hrs"}</div>
                </div>
                """, unsafe_allow_html=True)
            with kpi3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Margin</div>
                    <div class="metric-value">{margin_pct_str}</div>
                </div>
                """, unsafe_allow_html=True)
            with kpi4:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Total Quote</div>
                    <div class="metric-value" style="color:{quote_color};">{total_quote_str}</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<div style='margin-bottom: 0.75rem;'></div>", unsafe_allow_html=True)
                
            # Status Banner
            if gaps:
                st.markdown(f"""
                <div class="banner-warning">
                    ⚠️ GAPS DETECTED: {len(gaps)} missing field(s) required to generate a proposal. Pricing is locked until details are clarified.
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
                st.markdown("###### Extracted Request & Regulatory Metadata:")
                cert_basis = getattr(facts, "cert_basis", None) or resolve_cert_basis(facts.aircraft_type)
                part21_info = classify_part21_change(facts.scope, facts.modification_type or "", facts.complexity or "standard")
                dal_str = getattr(facts, "dal_level", None) or "DAL D"
                
                f_col1, f_col2 = st.columns(2)
                with f_col1:
                    st.write(f"**Airline:** {facts.customer_name or 'N/A'}")
                    st.write(f"**Class:** `{facts.customer_class or 'N/A'}`")
                    st.write(f"**Aircraft:** {facts.aircraft_type or 'N/A'}")
                    st.write(f"**Cert Basis:** `{cert_basis}` (Fixed-Wing)")
                with f_col2:
                    st.write(f"**Mod Category:** `{facts.modification_type or 'N/A'}`")
                    st.write(f"**EASA Part 21:** `{part21_info['clause']}`")
                    st.write(f"**Safety DAL Level:** `{dal_str}`")
                    st.write(f"**Scope:** {facts.scope or 'N/A'}")
                
                if gaps:
                    st.markdown("---")
                    st.markdown("###### ⚠️ Missing Required Fields Checklist:")
                    for gap in gaps:
                        st.write(f"- ❌ **{gap}**: {get_field_description(gap)}")
                        
                    st.markdown("###### ✉️ Draft Clarification Email (Send to Customer):")
                    draft_body = draft_clarification_email(
                        original_email=email_input,
                        missing_fields=gaps,
                        language=draft_lang
                    )
                    st.text_area("Copyable Reply Draft for Client:", value=draft_body, height=220)
                else:
                    st.markdown("---")
                    st.markdown(f"###### ⏱️ Engineering Manhour Allocation (`{mh_source}`):")
                    mh_col1, mh_col2 = st.columns(2)
                    with mh_col1:
                        st.write(f"- **Cabin Design Engineer:** {(mh_used.get('cabin_design_engineer') or 0.0):.1f} hrs")
                        st.write(f"- **Structural Engineer:** {(mh_used.get('structural_engineer') or 0.0):.1f} hrs")
                        st.write(f"- **Avionics Design Engineer (incl. EWIS):** {(mh_used.get('avionics_design_engineer') or 0.0):.1f} hrs")
                    with mh_col2:
                        if mh_source == "Customer Provided" and facts.manhours and facts.manhours.certification_engineer is not None:
                            cert_hrs = facts.manhours.certification_engineer
                        else:
                            cert_base = (mh_used.get('certification_engineer') or 0.0) - part21_info['cve_hours'] - part21_info.get('ica_hours', 0.0)
                            cert_hrs = max(0.0, cert_base)
                        st.write(f"- **Certification Engineer:** {cert_hrs:.1f} hrs")
                        st.write(f"- **Project Manager:** {(mh_used.get('project_manager') or 0.0):.1f} hrs")
                        st.write(f"- **Independent CVE (21.A.239):** `{part21_info['cve_hours']:.1f} hrs`")
                        st.write(f"- **ICA Preparation (CS-25.1529):** `{part21_info.get('ica_hours', 0.0):.1f} hrs`")
                        st.write(f"- **Total Estimated Hours:** `{total_hours:.1f} hrs`")

            # TAB 2: Pricing & Interactive Margin Sandbox
            with tab_pricing:
                if gaps:
                    st.markdown(f"""
                    <div class="banner-warning" style="padding: 1.5rem; text-align: center;">
                        <h4 style="margin-top:0; color: #92400e;">🔒 PRICING LOCKED</h4>
                        <p><b>{len(gaps)} missing field(s)</b> are required to calculate a valid DOA engineering quote.</p>
                        <p style="font-size: 0.88rem; color: #78350f;">Please send the generated clarification email (see <i>Extracted Facts & Gaps</i> tab) to the customer to collect the required project scope and aircraft details.</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
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
                    urgency_m = base_quote.get("urgency_multiplier", 1.0)
                    base_labor_adj = base_quote.get("base_labor_cost_adjusted", base_labor)
                    margin_amt = round(base_labor_adj * sandbox_margin, 2)
                    contingency_r = base_quote.get("contingency_rate", 0.05)
                    contingency = round(base_labor_adj * contingency_r, 2)
                    testing = base_quote["testing_fee"]
                    materials = base_quote["material_allowance"]
                    subtotal = round(base_labor_adj + margin_amt + contingency + testing + materials, 2)
                    vol_disc_rate = base_quote.get("volume_discount_rate", 0.0)
                    vol_disc = round(subtotal * vol_disc_rate, 2)
                    final_total = round(subtotal - vol_disc, 2)
                    
                    st.markdown("###### Itemized Cost Breakdown:")
                    
                    line_items = ["Engineering Base Labor"]
                    descriptions = [f"Total {total_hours:.0f} engineering hours"]
                    costs = [f"${base_labor:,.2f}"]
                    
                    if urgency_m > 1.0:
                        line_items.append(f"Urgency Surcharge ({urgency_m:.0%})")
                        descriptions.append("AOG/Rush overtime & mobilization")
                        costs.append(f"${round(base_labor_adj - base_labor, 2):,.2f}")
                    
                    line_items += [
                        f"Customer Margin ({custom_margin_pct:.1f}%)",
                        f"Contingency ({contingency_r*100:.0f}% risk-based)",
                        "Testing & Certification Fee",
                        f"Material Allowance ({fleet_sz} a/c)"
                    ]
                    descriptions += [
                        f"Target margin for {c_class}",
                        f"Risk profile: {'STC' if base_quote.get('contingency_rate', 0.05) >= 0.10 else 'Standard'}",
                        f"{(facts.modification_type or 'cabin').upper()} / {complexity_val}",
                        f"Per-aircraft kit × {fleet_sz}"
                    ]
                    costs += [
                        f"${margin_amt:,.2f}",
                        f"${contingency:,.2f}",
                        f"${testing:,.2f}",
                        f"${materials:,.2f}"
                    ]
                    
                    if vol_disc > 0:
                        line_items.append(f"Volume Discount ({vol_disc_rate*100:.0f}%)")
                        descriptions.append(f"Fleet {fleet_sz} aircraft discount")
                        costs.append(f"-${vol_disc:,.2f}")
                    
                    breakdown_df = pd.DataFrame({
                        "Line Item": line_items,
                        "Description": descriptions,
                        "Cost (USD)": costs
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
                if gaps:
                    summary_text = generate_proposal_summary(
                        facts=facts,
                        gaps=gaps,
                        quote=None,
                        email_draft=draft_clarification_email(email_input, gaps, draft_lang)
                    )
                else:
                    summary_text = generate_proposal_summary(
                        facts=facts,
                        gaps=gaps,
                        quote={
                            "base_labor_cost": base_labor,
                            "urgency_multiplier": urgency_m,
                            "base_labor_cost_adjusted": base_labor_adj,
                            "margin_applied": sandbox_margin,
                            "margin_amount": margin_amt,
                            "contingency_rate": contingency_r,
                            "contingency": contingency,
                            "testing_fee": testing,
                            "material_allowance": materials,
                            "volume_discount_rate": vol_disc_rate,
                            "volume_discount": vol_disc,
                            "total_cost": final_total
                        },
                        email_draft=""
                    )
                
                st.markdown(summary_text)
                st.download_button(
                    label="📥 Download Proposal Summary (.md)",
                    data=summary_text,
                    file_name="proposal_summary.md",
                    mime="text/markdown"
                )
    elif clean_email:
        st.info("👈 Click **🔍 Analyze & Calculate Proposal** to process this modification inquiry.")
    else:
        st.info("👈 Paste a customer inquiry email on the left to begin analysis.")
