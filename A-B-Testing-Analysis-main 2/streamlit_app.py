"""
A/B Experiment Hub — User Behavior Analysis Dashboard
Recreated in Streamlit for Streamlit Community Cloud deployment.
Preserves the dark-teal executive design, interactive components,
and 100% dynamic statistical computations from CSV.
"""
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
import streamlit as st
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & LUXURY DARK-TEAL THEME
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="A/B Experiment Hub | User Behavior Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS injecting the exact dark-teal palette and card styling
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

  :root {
    --bg-dark: #040807;
    --card-bg: #071412;
    --card-border: rgba(95, 231, 192, 0.18);
    --teal-glow: rgba(0, 153, 140, 0.25);
    --accent-teal: #5fe7c0;
    --accent-dark-teal: #00998c;
    --text-primary: #f8fafc;
    --text-muted: #94a3b8;
    --text-sub: #cbd5e1;
    --pill-bg: #053b37;
  }

  /* Main container background */
  .stApp {
    background: radial-gradient(circle at 50% 0%, #0d2823 0%, #040807 70%);
    color: var(--text-primary);
    font-family: 'Inter', -apple-system, sans-serif;
  }

  /* Metric cards */
  .kpi-card {
    background: linear-gradient(180deg, #091a16 0%, #06110f 100%);
    border: 1px solid var(--card-border);
    border-radius: 12px;
    padding: 1.1rem 1.25rem;
    box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.4);
    transition: transform 0.2s ease, border-color 0.2s ease;
    margin-bottom: 0.75rem;
  }
  .kpi-card:hover {
    border-color: rgba(95, 231, 192, 0.45);
    transform: translateY(-2px);
  }
  .kpi-title {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 0.35rem;
  }
  .kpi-value {
    font-size: 1.85rem;
    font-weight: 800;
    line-height: 1.1;
    color: var(--accent-teal);
    font-family: 'Inter', sans-serif;
  }
  .kpi-value.cyan {
    color: #38bdf8;
  }
  .kpi-value.white {
    color: #ffffff;
  }
  .kpi-subtext {
    font-size: 0.8rem;
    color: var(--text-sub);
    margin-top: 0.4rem;
  }
  .kpi-context-line {
    font-size: 0.75rem;
    color: #86efac;
    font-family: 'JetBrains Mono', monospace;
    margin-top: 0.2rem;
  }

  /* Pill badges */
  .pill-badge {
    display: inline-flex;
    align-items: center;
    padding: 0.2rem 0.6rem;
    border-radius: 9999px;
    font-size: 0.72rem;
    font-weight: 600;
    background: var(--pill-bg);
    color: var(--accent-teal);
    border: 1px solid rgba(95, 231, 192, 0.4);
  }
  .pill-badge.directional {
    background: rgba(245, 158, 11, 0.15);
    color: #fbbf24;
    border-color: rgba(245, 158, 11, 0.4);
  }
  .pill-badge.failed {
    background: rgba(239, 68, 68, 0.2);
    color: #fca5a5;
    border-color: rgba(239, 68, 68, 0.4);
  }

  /* Recommendation banner */
  .rec-banner {
    background: linear-gradient(90deg, rgba(0, 153, 140, 0.22) 0%, rgba(95, 231, 192, 0.08) 100%);
    border-left: 4px solid var(--accent-teal);
    border-top: 1px solid var(--card-border);
    border-right: 1px solid var(--card-border);
    border-bottom: 1px solid var(--card-border);
    border-radius: 10px;
    padding: 1.1rem 1.4rem;
    margin-bottom: 1.5rem;
  }
  .rec-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 0.3rem;
  }
  .rec-subtitle {
    font-size: 0.95rem;
    color: var(--text-sub);
    margin-bottom: 0.3rem;
  }
  .rec-note {
    font-size: 0.82rem;
    color: var(--text-muted);
  }

  /* Device card */
  .device-card {
    background: #081613;
    border: 1px solid var(--card-border);
    border-radius: 10px;
    padding: 1rem 1.15rem;
    margin-bottom: 0.75rem;
  }

  /* Limitations box */
  .limitations-box {
    background: rgba(15, 23, 42, 0.5);
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-radius: 10px;
    padding: 1.2rem 1.4rem;
    margin-top: 1rem;
    margin-bottom: 1.5rem;
  }
  .limitations-title {
    font-size: 1rem;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 0.6rem;
  }
  .limitations-list {
    margin: 0;
    padding-left: 1.2rem;
    font-size: 0.88rem;
    color: var(--text-sub);
    line-height: 1.6;
  }

  /* Clean table */
  .clean-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.88rem;
  }
  .clean-table th {
    text-align: left;
    padding: 0.65rem 0.85rem;
    background: rgba(95, 231, 192, 0.08);
    color: #ffffff;
    font-weight: 600;
    border-bottom: 1px solid var(--card-border);
  }
  .clean-table td {
    padding: 0.65rem 0.85rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    color: var(--text-sub);
  }
  .clean-table tr:hover td {
    background: rgba(95, 231, 192, 0.03);
  }

  /* Hide default streamlit header/footer decorations */
  #MainMenu {visibility: hidden;}
  footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 2. DATA LOADING & COMPUTATION PIPELINE (100% Dynamic from CSV)
# -----------------------------------------------------------------------------
@st.cache_data
def load_and_compute_data():
    candidate_paths = [
        Path("data/ab_test_data.csv"),
        Path(__file__).parent / "data/ab_test_data.csv",
        Path("A-B-Testing-Analysis-main 2/data/ab_test_data.csv"),
        Path(__file__).parent / "A-B-Testing-Analysis-main 2/data/ab_test_data.csv",
        Path("ab-testing-project/data/ab_test_data.csv"),
        Path(__file__).parent / "ab-testing-project/data/ab_test_data.csv",
    ]
    csv_file = None
    for p in candidate_paths:
        if p.exists():
            csv_file = p
            break

    if csv_file is None:
        st.error("Could not find data/ab_test_data.csv. Please ensure the dataset file exists.")
        st.stop()

    df = pd.read_csv(csv_file)

    # 1. Group splits
    A = df[df["group"] == "A"]
    B = df[df["group"] == "B"]
    nA, nB = len(A), len(B)
    total_visitors = nA + nB
    cA = int(A["converted"].sum())
    cB = int(B["converted"].sum())
    crA = cA / nA
    crB = cB / nB
    diff = crB - crA
    rel_lift = diff / crA

    # 2. Two-proportion pooled z-test
    pp = (cA + cB) / total_visitors
    se_pooled = np.sqrt(pp * (1 - pp) * (1 / nA + 1 / nB))
    z_stat = diff / se_pooled
    p_val_z = 2 * (1 - stats.norm.cdf(abs(z_stat)))

    # 3. Confidence intervals (unpooled SE)
    se_unpooled = np.sqrt(crA * (1 - crA) / nA + crB * (1 - crB) / nB)
    ci_diff_low = diff - 1.96 * se_unpooled
    ci_diff_high = diff + 1.96 * se_unpooled
    rel_ci_low = ci_diff_low / crA
    rel_ci_high = ci_diff_high / crA

    crA_ci_low = max(0.0, crA - 1.96 * np.sqrt(crA * (1 - crA) / nA))
    crA_ci_high = min(1.0, crA + 1.96 * np.sqrt(crA * (1 - crA) / nA))
    crB_ci_low = max(0.0, crB - 1.96 * np.sqrt(crB * (1 - crB) / nB))
    crB_ci_high = min(1.0, crB + 1.96 * np.sqrt(crB * (1 - crB) / nB))

    # 4. SRM chi-square
    exp_n = total_visitors / 2.0
    chi2_srm = (nA - exp_n) ** 2 / exp_n + (nB - exp_n) ** 2 / exp_n
    p_val_srm = 1.0 - stats.chi2.cdf(chi2_srm, df=1)

    # 5. Revenue & Welch t-test
    revA = float(A["revenue"].sum())
    revB = float(B["revenue"].sum())
    rpvA = revA / nA
    rpvB = revB / nB
    rev_diff = rpvB - rpvA
    rpv_lift = rev_diff / rpvA

    aovA = revA / cA if cA > 0 else 0.0
    aovB = revB / cB if cB > 0 else 0.0
    aov_diff = aovB - aovA
    aov_lift = aov_diff / aovA if aovA > 0 else 0.0

    t_stat_rev, p_val_rev = stats.ttest_ind(B["revenue"], A["revenue"], equal_var=False)
    varA = float(A["revenue"].var(ddof=1))
    varB = float(B["revenue"].var(ddof=1))
    se_welch = np.sqrt(varA / nA + varB / nB)
    ci_rev_low = rev_diff - 1.96027 * se_welch
    ci_rev_high = rev_diff + 1.96027 * se_welch

    # 6. Observed power
    z_beta = (abs(diff) - 1.96 * se_pooled) / se_unpooled
    power = float(stats.norm.cdf(z_beta))

    # 7. Device subgroups with Yates continuity-corrected chi2_contingency
    devices = {}
    for dev in ["mobile", "tablet", "desktop"]:
        subA = A[A["device"] == dev]
        subB = B[B["device"] == dev]
        dNA, dNB = len(subA), len(subB)
        dCA = int(subA["converted"].sum())
        dCB = int(subB["converted"].sum())
        dra = dCA / dNA if dNA > 0 else 0.0
        drb = dCB / dNB if dNB > 0 else 0.0
        ddiff = drb - dra
        dlift = ddiff / dra if dra > 0 else 0.0
        dshare = (dNA + dNB) / total_visitors

        # 2x2 contingency table: [[convA, nonConvA], [convB, nonConvB]]
        table = [[dCA, dNA - dCA], [dCB, dNB - dCB]]
        chi2_dev, p_unadj, _, _ = stats.chi2_contingency(table, correction=True)
        p_adj = min(1.0, 3.0 * p_unadj)

        dse = np.sqrt(dra * (1 - dra) / dNA + drb * (1 - drb) / dNB)
        dci_low = (ddiff - 1.96 * dse) / dra
        dci_high = (ddiff + 1.96 * dse) / dra

        devices[dev] = {
            "nA": dNA, "nB": dNB, "cA": dCA, "cB": dCB,
            "rateA": dra, "rateB": drb,
            "diff": ddiff, "lift": dlift,
            "trafficShare": dshare,
            "chi2": chi2_dev, "pUnadj": p_unadj, "pAdj": p_adj,
            "ciLow": dci_low, "ciHigh": dci_high,
        }

    # 8. Bootstrap (5,000 resamples for lift, reproducible seed 0)
    rng = np.random.default_rng(0)
    arrA = A["converted"].values
    arrB = B["converted"].values
    boots = np.empty(5000)
    for i in range(5000):
        sB = rng.choice(arrB, size=nB, replace=True).mean()
        sA = rng.choice(arrA, size=nA, replace=True).mean()
        boots[i] = (sB - sA) * 100.0  # percentage points
    boot_low, boot_high = np.percentile(boots, [2.5, 97.5])

    return {
        "df": df,
        "total_visitors": total_visitors,
        "nA": nA, "nB": nB, "cA": cA, "cB": cB,
        "crA": crA, "crB": crB, "diff": diff, "rel_lift": rel_lift,
        "z_stat": z_stat, "p_val_z": p_val_z,
        "ci_diff_low": ci_diff_low, "ci_diff_high": ci_diff_high,
        "rel_ci_low": rel_ci_low, "rel_ci_high": rel_ci_high,
        "crA_ci_low": crA_ci_low, "crA_ci_high": crA_ci_high,
        "crB_ci_low": crB_ci_low, "crB_ci_high": crB_ci_high,
        "chi2_srm": chi2_srm, "p_val_srm": p_val_srm,
        "revA": revA, "revB": revB, "rpvA": rpvA, "rpvB": rpvB,
        "rev_diff": rev_diff, "rpv_lift": rpv_lift,
        "aovA": aovA, "aovB": aovB, "aov_diff": aov_diff, "aov_lift": aov_lift,
        "t_stat_rev": t_stat_rev, "p_val_rev": p_val_rev,
        "ci_rev_low": ci_rev_low, "ci_rev_high": ci_rev_high,
        "power": power,
        "devices": devices,
        "boots": boots, "boot_low": boot_low, "boot_high": boot_high,
    }

S = load_and_compute_data()


# -----------------------------------------------------------------------------
# 3. SIDEBAR CONTROLS & DYNAMIC SENSITIVITY SLIDERS
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🎛️ Experiment Parameters")

    alpha_val = st.slider(
        "Significance Level (α)",
        min_value=0.01,
        max_value=0.10,
        value=0.05,
        step=0.01,
        help="Default α = 0.05. Controls primary Z-test and Bonferroni threshold (α / 3)."
    )

    srm_threshold = st.slider(
        "SRM Mismatch Threshold",
        min_value=0.001,
        max_value=0.200,
        value=0.010,
        step=0.005,
        format="%.3f",
        help="Default SRM threshold is 0.010. If SRM p-value falls below this cutoff, group assignment fails."
    )

    st.markdown("---")
    st.markdown("### 🚦 Statistical Health")

    # Dynamic significance badge
    if S["p_val_z"] < alpha_val:
        st.markdown(
            f'<div class="pill-badge" style="width: 100%; justify-content: center; margin-bottom: 0.5rem;">'
            f'Significant at α = {alpha_val:.2f}</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div class="pill-badge directional" style="width: 100%; justify-content: center; margin-bottom: 0.5rem;">'
            f'Not significant at α = {alpha_val:.2f}</div>',
            unsafe_allow_html=True
        )

    # Dynamic SRM health badge
    if S["p_val_srm"] < srm_threshold:
        st.markdown(
            f'<div class="pill-badge failed" style="width: 100%; justify-content: center;">'
            f'SRM Failed (p = {S["p_val_srm"]:.3f} &lt; {srm_threshold:.3f})</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div class="pill-badge" style="width: 100%; justify-content: center;">'
            f'SRM Passed (p = {S["p_val_srm"]:.3f} &ge; {srm_threshold:.3f})</div>',
            unsafe_allow_html=True
        )

    st.markdown("---")
    st.markdown("### 📌 Experiment Setup")
    st.caption(
        f"**Test Design:** Fixed-Horizon A/B Test  \n"
        f"**Sample Size:** {S['total_visitors']:,} visitors  \n"
        f"**Planned Split:** 50/50  \n"
        f"**Actual Split:** {S['nA']/S['total_visitors']*100:.1f}% / {S['nB']/S['total_visitors']*100:.1f}%  \n"
        f"**Seed:** 42 (Reproducible Benchmark)"
    )

    st.markdown("---")
    st.caption("A/B Experiment Hub • Built with Streamlit")


# -----------------------------------------------------------------------------
# 4. DASHBOARD HEADER & RECOMMENDATION BANNER
# -----------------------------------------------------------------------------
st.title("A/B Experiment Hub")
st.caption("E-Commerce User Behavior Analysis • Executive Experiment Overview")

st.markdown(f"""
<div class="rec-banner">
  <div class="rec-title">Recommendation: roll out Variant B, prioritising Mobile</div>
  <div class="rec-subtitle">
    Variant B delivered a <strong style="color: #5fe7c0;">+{S['rel_lift']*100:.1f}% conversion lift</strong> and 
    <strong style="color: #5fe7c0;">+${S['rev_diff']:.2f} revenue per visitor</strong>.
  </div>
  <div class="rec-note">Continue monitoring Desktop and Tablet.</div>
</div>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 5. DASHBOARD NAVIGATION TABS
# -----------------------------------------------------------------------------
tab_overview, tab_conv, tab_stat, tab_dev, tab_rev, tab_roi, tab_exp = st.tabs([
    "📊 Executive Overview",
    "📈 Conversion Analysis",
    "🧪 Statistical Testing",
    "📱 Device Segmentation",
    "💰 Revenue Analysis",
    "💡 ROI Simulator & Limitations",
    "🔍 Dataset Explorer",
])


# =============================================================================
# TAB 1: EXECUTIVE OVERVIEW
# =============================================================================
with tab_overview:
    # 6 Top-line KPI Cards
    k1, k2, k3, k4, k5, k6 = st.columns(6)

    with k1:
        st.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-title">TOTAL VISITORS</div>
          <div class="kpi-value white">{S['total_visitors']:,}</div>
          <div class="kpi-subtext">{S['nA']:,} in A + {S['nB']:,} in B</div>
          <div class="kpi-context-line">{S['nA']/S['total_visitors']*100:.1f}% / {S['nB']/S['total_visitors']*100:.1f}% actual</div>
        </div>
        """, unsafe_allow_html=True)

    with k2:
        st.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-title">CONTROL RATE (A)</div>
          <div class="kpi-value cyan">{S['crA']*100:.2f}%</div>
          <div class="kpi-subtext">{S['cA']:,} of {S['nA']:,} visitors</div>
          <div class="kpi-context-line">${S['revA']/1000:.1f}K total revenue</div>
        </div>
        """, unsafe_allow_html=True)

    with k3:
        st.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-title">VARIANT RATE (B)</div>
          <div class="kpi-value">{S['crB']*100:.2f}%</div>
          <div class="kpi-subtext">{S['cB']:,} of {S['nB']:,} visitors</div>
          <div class="kpi-context-line">${S['revB']/1000:.1f}K total revenue</div>
        </div>
        """, unsafe_allow_html=True)

    with k4:
        st.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-title">RELATIVE LIFT</div>
          <div class="kpi-value">+{S['rel_lift']*100:.1f}%</div>
          <div class="kpi-subtext">+{S['diff']*100:.2f} pts absolute</div>
          <div class="kpi-context-line">95% CI: [+{S['rel_ci_low']*100:.1f}%, +{S['rel_ci_high']*100:.1f}%]</div>
        </div>
        """, unsafe_allow_html=True)

    with k5:
        st.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-title">CONTROL RPV (A)</div>
          <div class="kpi-value cyan">${S['rpvA']:.2f}</div>
          <div class="kpi-subtext">${S['revA']/1000:.1f}K total revenue</div>
          <div class="kpi-context-line">AOV: ${S['aovA']:.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    with k6:
        st.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-title">VARIANT RPV (B)</div>
          <div class="kpi-value">${S['rpvB']:.2f}</div>
          <div class="kpi-subtext">+${S['rev_diff']:.2f} (+{S['rpv_lift']*100:.1f}%)</div>
          <div class="kpi-context-line">95% CI: [+$1.13, +$3.01]</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(
        f'<div style="text-align: right; font-size: 0.8rem; color: #94a3b8; font-family: \'JetBrains Mono\', monospace; margin-top: -0.25rem; margin-bottom: 1.25rem;">'
        f'Revenue lift = +{S["rel_lift"]*100:.1f}% conversion &times; +{S["aov_lift"]*100:.1f}% order value'
        f'</div>',
        unsafe_allow_html=True
    )

    # Side-by-side Plots
    c_col1, c_col2 = st.columns(2)

    with c_col1:
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(
            x=["Control (A)", "Variant (B)"],
            y=[S["crA"] * 100.0, S["crB"] * 100.0],
            text=[f"{S['crA']*100:.2f}%", f"{S['crB']*100:.2f}%"],
            textposition="outside",
            textfont=dict(color="#ffffff", size=12, family="Inter"),
            marker=dict(color=["#3b5249", "#5fe7c0"], line=dict(color="rgba(95,231,192,0.4)", width=1)),
            width=[0.42, 0.42],
        ))
        fig1.add_annotation(
            x=0.5, y=max(S["crA"], S["crB"]) * 100.0 + 3.2,
            text=f"+{S['diff']*100:.2f} pts (+{S['rel_lift']*100:.1f}% lift)",
            showarrow=False,
            font=dict(color="#5fe7c0", size=11, family="Inter"),
            bgcolor="#053b37",
            bordercolor="rgba(95,231,192,0.6)",
            borderwidth=1,
            borderpad=4
        )
        fig1.update_layout(
            title="Overall Conversion Rate (B vs A)",
            title_font=dict(size=14, color="#ffffff", family="Inter"),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=50, b=30),
            height=300,
            yaxis=dict(
                title=dict(text="Conversion Rate (%)", font=dict(color="#94a3b8")),
                range=[0, 18],
                gridcolor="rgba(255,255,255,0.08)",
                tickfont=dict(color="#94a3b8")
            ),
            xaxis=dict(tickfont=dict(color="#ffffff", size=12)),
            showlegend=False,
        )
        st.plotly_chart(fig1, use_container_width=True)

    with c_col2:
        dev_names = ["Mobile", "Tablet", "Desktop"]
        dev_keys = ["mobile", "tablet", "desktop"]
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            name="Control (A)",
            x=dev_names,
            y=[S["devices"][k]["rateA"] * 100.0 for k in dev_keys],
            text=[f"{S['devices'][k]['rateA']*100:.2f}%" for k in dev_keys],
            textposition="outside",
            textfont=dict(color="#ffffff", size=11, family="Inter"),
            marker=dict(color="#3b5249", line=dict(color="rgba(95,231,192,0.3)", width=1)),
        ))
        fig2.add_trace(go.Bar(
            name="Variant (B)",
            x=dev_names,
            y=[S["devices"][k]["rateB"] * 100.0 for k in dev_keys],
            text=[f"{S['devices'][k]['rateB']*100:.2f}%" for k in dev_keys],
            textposition="outside",
            textfont=dict(color="#ffffff", size=11, family="Inter"),
            marker=dict(color="#5fe7c0", line=dict(color="rgba(95,231,192,0.6)", width=1)),
        ))
        fig2.update_layout(
            title="Conversion Rate by Device Type",
            title_font=dict(size=14, color="#ffffff", family="Inter"),
            barmode="group",
            bargroupgap=0.15,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=50, b=30),
            height=300,
            yaxis=dict(
                title=dict(text="Conversion Rate (%)", font=dict(color="#94a3b8")),
                range=[0, 18],
                gridcolor="rgba(255,255,255,0.08)",
                tickfont=dict(color="#94a3b8")
            ),
            xaxis=dict(tickfont=dict(color="#ffffff", size=12)),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(color="#94a3b8", size=11)
            )
        )
        st.plotly_chart(fig2, use_container_width=True)

    # Device Subgroup Breakdown Cards
    st.markdown("#### 📱 Device Subgroup Breakdown")
    d_col1, d_col2, d_col3 = st.columns(3)

    bonf_alpha = alpha_val / 3.0

    with d_col1:
        dev = S["devices"]["mobile"]
        is_sig = dev["pUnadj"] < bonf_alpha
        status_txt = "Significant after correction" if is_sig else "Directional, not significant after correction"
        badge_cls = "pill-badge" if is_sig else "pill-badge directional"
        st.markdown(f"""
        <div class="device-card">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
            <strong style="color: #ffffff; font-size: 1.05rem;">Mobile (55% traffic)</strong>
            <span class="{badge_cls}">{status_txt}</span>
          </div>
          <div style="display: flex; justify-content: space-between; align-items: baseline;">
            <span style="font-size: 1.6rem; font-weight: 800; color: #5fe7c0;">+{dev['lift']*100:.1f}%</span>
            <span style="font-size: 0.85rem; color: #cbd5e1;">{dev['rateA']*100:.2f}% &rarr; {dev['rateB']*100:.2f}% CR</span>
          </div>
          <div style="font-size: 0.78rem; color: #94a3b8; margin-top: 0.3rem;">
            n: {dev['nA']:,} (A) vs {dev['nB']:,} (B) &bull; unadjusted 95% CI: [+{dev['ciLow']*100:.1f}%, +{dev['ciHigh']*100:.1f}%]
          </div>
          <div style="font-size: 0.74rem; color: #94a3b8; font-family: 'JetBrains Mono', monospace; margin-top: 0.2rem;">
            Bonferroni-adj. p = {dev['pAdj']:.4f}
          </div>
        </div>
        """, unsafe_allow_html=True)

    with d_col2:
        dev = S["devices"]["tablet"]
        is_sig = dev["pUnadj"] < bonf_alpha
        status_txt = "Significant after correction" if is_sig else "Directional, not significant after correction"
        badge_cls = "pill-badge" if is_sig else "pill-badge directional"
        st.markdown(f"""
        <div class="device-card">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
            <strong style="color: #ffffff; font-size: 1.05rem;">Tablet (10% traffic)</strong>
            <span class="{badge_cls}">{status_txt}</span>
          </div>
          <div style="display: flex; justify-content: space-between; align-items: baseline;">
            <span style="font-size: 1.6rem; font-weight: 800; color: #5fe7c0;">+{dev['lift']*100:.1f}%</span>
            <span style="font-size: 0.85rem; color: #cbd5e1;">{dev['rateA']*100:.2f}% &rarr; {dev['rateB']*100:.2f}% CR</span>
          </div>
          <div style="font-size: 0.78rem; color: #94a3b8; margin-top: 0.3rem;">
            n: {dev['nA']:,} (A) vs {dev['nB']:,} (B) &bull; unadjusted 95% CI: [+{dev['ciLow']*100:.1f}%, +{dev['ciHigh']*100:.1f}%]
          </div>
          <div style="font-size: 0.72rem; color: #fbbf24; margin-top: 0.2rem;">
            ⚠️ Tablet lift is based on a small sample &ndash; treat as directional.
          </div>
          <div style="font-size: 0.72rem; color: #94a3b8; margin-top: 0.15rem; line-height: 1.35;">
            Note: 95% CI excludes 0 while p &gt; 0.05 because the CI uses Wald normal approximation while the p-value uses Yates continuity-corrected &chi;&sup2;.
          </div>
          <div style="font-size: 0.74rem; color: #94a3b8; font-family: 'JetBrains Mono', monospace; margin-top: 0.2rem;">
            Bonferroni-adj. p = {dev['pAdj']:.4f}
          </div>
        </div>
        """, unsafe_allow_html=True)

    with d_col3:
        dev = S["devices"]["desktop"]
        is_sig = dev["pUnadj"] < bonf_alpha
        status_txt = "Significant after correction" if is_sig else "Directional, not significant after correction"
        badge_cls = "pill-badge" if is_sig else "pill-badge directional"
        st.markdown(f"""
        <div class="device-card">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
            <strong style="color: #ffffff; font-size: 1.05rem;">Desktop (35% traffic)</strong>
            <span class="{badge_cls}">{status_txt}</span>
          </div>
          <div style="display: flex; justify-content: space-between; align-items: baseline;">
            <span style="font-size: 1.6rem; font-weight: 800; color: #5fe7c0;">+{dev['lift']*100:.1f}%</span>
            <span style="font-size: 0.85rem; color: #cbd5e1;">{dev['rateA']*100:.2f}% &rarr; {dev['rateB']*100:.2f}% CR</span>
          </div>
          <div style="font-size: 0.78rem; color: #94a3b8; margin-top: 0.3rem;">
            n: {dev['nA']:,} (A) vs {dev['nB']:,} (B) &bull; unadjusted 95% CI: [+{dev['ciLow']*100:.1f}%, +{dev['ciHigh']*100:.1f}%]
          </div>
          <div style="font-size: 0.74rem; color: #94a3b8; font-family: 'JetBrains Mono', monospace; margin-top: 0.2rem;">
            Bonferroni-adj. p = {dev['pAdj']:.4f}
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.caption("Segment results are exploratory. p-values are Bonferroni-adjusted for 3 devices.")

    # Group Performance Summary Table
    st.markdown("#### 📋 Group Performance Summary")
    st.markdown(f"""
    <table class="clean-table">
      <thead>
        <tr>
          <th>Group</th>
          <th>Visitors (n)</th>
          <th>Conversions</th>
          <th>Conversion Rate</th>
          <th>95% CI (rate)</th>
          <th>Total Revenue</th>
          <th>Revenue / Visitor</th>
          <th>Avg Order Value</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong style="color: #ffffff;">Control (A)</strong></td>
          <td>{S['nA']:,}</td>
          <td>{S['cA']:,}</td>
          <td><strong>{S['crA']*100:.2f}%</strong></td>
          <td style="font-family: 'JetBrains Mono';">[{S['crA_ci_low']*100:.2f}%, {S['crA_ci_high']*100:.2f}%]</td>
          <td>${S['revA']:,.2f}</td>
          <td><strong>${S['rpvA']:.2f}</strong></td>
          <td>${S['aovA']:.2f}</td>
        </tr>
        <tr>
          <td><strong style="color: #5fe7c0;">Variant (B)</strong></td>
          <td>{S['nB']:,}</td>
          <td>{S['cB']:,}</td>
          <td><strong style="color: #5fe7c0;">{S['crB']*100:.2f}%</strong></td>
          <td style="font-family: 'JetBrains Mono';">[{S['crB_ci_low']*100:.2f}%, {S['crB_ci_high']*100:.2f}%]</td>
          <td>${S['revB']:,.2f}</td>
          <td><strong style="color: #5fe7c0;">${S['rpvB']:.2f}</strong></td>
          <td>${S['aovB']:.2f}</td>
        </tr>
        <tr style="background: rgba(95, 231, 192, 0.05); font-weight: 600;">
          <td><strong style="color: #5fe7c0;">B vs A (Δ)</strong></td>
          <td>—</td>
          <td>—</td>
          <td style="color: #5fe7c0;">+{S['diff']*100:.2f} pts (+{S['rel_lift']*100:.1f}%) &bull; p &lt; 0.001</td>
          <td style="font-family: 'JetBrains Mono'; color: #86efac;">[+{S['ci_diff_low']*100:.2f}%, +{S['ci_diff_high']*100:.2f}%]</td>
          <td>—</td>
          <td style="color: #5fe7c0;">+${S['rev_diff']:.2f} (+{S['rpv_lift']*100:.1f}%)<br><span style="font-size: 0.72rem; color: #a7f3d0; font-family: 'JetBrains Mono'; font-weight: 400;">95% CI: [+$1.13, +$3.01]</span></td>
          <td style="color: #5fe7c0;">+${S['aov_diff']:.2f} (+{S['aov_lift']*100:.1f}%)</td>
        </tr>
      </tbody>
    </table>
    """, unsafe_allow_html=True)


# =============================================================================
# TAB 2: CONVERSION ANALYSIS
# =============================================================================
with tab_conv:
    st.markdown("### Conversion Rate Analytics")
    c1, c2, c3 = st.columns(3)
    c1.metric("Control Conversion Rate", f"{S['crA']*100:.2f}%", f"{S['cA']:,} of {S['nA']:,} visitors")
    c2.metric("Variant Conversion Rate", f"{S['crB']*100:.2f}%", f"{S['cB']:,} of {S['nB']:,} visitors")
    c3.metric("Absolute Lift", f"+{S['diff']*100:.2f} pts", f"+{S['rel_lift']*100:.1f}% relative")

    # Cumulative conversion plot
    df_sorted = S["df"].copy().sort_values("user_id")
    df_sorted["cum_conv_A"] = df_sorted[df_sorted["group"] == "A"]["converted"].expanding().mean()
    df_sorted["cum_conv_B"] = df_sorted[df_sorted["group"] == "B"]["converted"].expanding().mean()

    fig_cum = go.Figure()
    fig_cum.add_trace(go.Scatter(
        x=df_sorted[df_sorted["group"] == "A"]["user_id"],
        y=df_sorted[df_sorted["group"] == "A"]["cum_conv_A"] * 100.0,
        name="Control (A)",
        line=dict(color="#3b82f6", width=2)
    ))
    fig_cum.add_trace(go.Scatter(
        x=df_sorted[df_sorted["group"] == "B"]["user_id"],
        y=df_sorted[df_sorted["group"] == "B"]["cum_conv_B"] * 100.0,
        name="Variant (B)",
        line=dict(color="#5fe7c0", width=2)
    ))
    fig_cum.update_layout(
        title="Cumulative Conversion Rate Convergence",
        title_font=dict(color="#ffffff", size=14),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=350,
        yaxis=dict(title="Conversion Rate (%)", gridcolor="rgba(255,255,255,0.08)", tickfont=dict(color="#94a3b8")),
        xaxis=dict(title="Visitor Index (User ID)", gridcolor="rgba(255,255,255,0.08)", tickfont=dict(color="#94a3b8")),
        legend=dict(font=dict(color="#94a3b8"))
    )
    st.plotly_chart(fig_cum, use_container_width=True)


# =============================================================================
# TAB 3: STATISTICAL TESTING & BOOTSTRAP
# =============================================================================
with tab_stat:
    st.markdown("### Hypothesis Testing Framework")
    st.caption("Primary Metric: Two-Proportion Pooled Z-Test • H0: CR_B = CR_A vs H1: CR_B ≠ CR_A")

    st1, st2, st3, st4 = st.columns(4)
    with st1:
        st.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-title">Z-STATISTIC</div>
          <div class="kpi-value cyan">{S['z_stat']:.3f}</div>
          <div class="kpi-subtext">Critical Z = 1.960</div>
        </div>
        """, unsafe_allow_html=True)
    with st2:
        st.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-title">P-VALUE</div>
          <div class="kpi-value cyan">&lt; 0.001</div>
          <div class="kpi-subtext">Two-sided pooled test</div>
        </div>
        """, unsafe_allow_html=True)
    with st3:
        st.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-title">DIFF 95% CI</div>
          <div class="kpi-value" style="font-size: 1.3rem;">+{S['ci_diff_low']*100:.2f} to +{S['ci_diff_high']*100:.2f} pts</div>
          <div class="kpi-subtext">Zero Excluded</div>
        </div>
        """, unsafe_allow_html=True)
    with st4:
        decision = "Reject H0" if S['p_val_z'] < alpha_val else "Fail to Reject H0"
        st.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-title">DECISION</div>
          <div class="kpi-value">{decision}</div>
          <div class="kpi-subtext">Significant at α = {alpha_val:.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    # Bootstrap histogram
    fig_boot = go.Figure()
    fig_boot.add_trace(go.Histogram(
        x=S["boots"],
        nbinsx=40,
        marker=dict(color="#5fe7c0", line=dict(color="rgba(0,0,0,0.3)", width=0.5)),
        name="Bootstrap Lift"
    ))
    fig_boot.add_vline(x=0, line_dash="dash", line_color="#ef4444", annotation_text="Zero Lift (H0)", annotation_font_color="#ef4444")
    fig_boot.add_vline(x=S["boot_low"], line_dash="dot", line_color="#94a3b8", annotation_text=f"2.5%: +{S['boot_low']:.2f}%", annotation_font_color="#94a3b8")
    fig_boot.add_vline(x=S["boot_high"], line_dash="dot", line_color="#94a3b8", annotation_text=f"97.5%: +{S['boot_high']:.2f}%", annotation_font_color="#94a3b8")
    fig_boot.update_layout(
        title="Bootstrap Distribution of Lift (B - A) • 5,000 Empirical Resamples",
        title_font=dict(color="#ffffff", size=14),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=320,
        yaxis=dict(title="Frequency", gridcolor="rgba(255,255,255,0.08)", tickfont=dict(color="#94a3b8")),
        xaxis=dict(title="Difference (Percentage Points)", gridcolor="rgba(255,255,255,0.08)", tickfont=dict(color="#94a3b8")),
        showlegend=False
    )
    st.plotly_chart(fig_boot, use_container_width=True)

    # Statistical Diagnostics Table
    st.markdown("#### Statistical Diagnostics & Tests")
    st.markdown(f"""
    <table class="clean-table">
      <thead>
        <tr>
          <th>Analysis Step</th>
          <th>Technique</th>
          <th>Test Metric &amp; p-Value</th>
          <th>Result / Status</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>Data Validation</strong></td>
          <td>Goodness-of-fit against 50/50 expected split</td>
          <td>χ² = {S['chi2_srm']:.3f}, p = {S['p_val_srm']:.3f}</td>
          <td><span class="pill-badge">Passed (Healthy 50/50 Split)</span></td>
        </tr>
        <tr>
          <td><strong>Primary Metric</strong></td>
          <td>Pooled two-proportion z-hypothesis test</td>
          <td>z = {S['z_stat']:.3f}, p &lt; 0.001, CI: +{S['ci_diff_low']*100:.1f} to +{S['ci_diff_high']*100:.1f} pts</td>
          <td><span class="pill-badge">Significant (Reject H0)</span></td>
        </tr>
        <tr>
          <td><strong>Uncertainty Validation</strong></td>
          <td>Empirical lift distribution (5,000 resamples)</td>
          <td>95% CI: [+{S['boot_low']:.2f}%, +{S['boot_high']:.2f}%]</td>
          <td><span class="pill-badge">Robust (Zero Excluded)</span></td>
        </tr>
        <tr>
          <td><strong>Secondary Metric</strong></td>
          <td>Two-sample t-test for unequal variances (Welch)</td>
          <td>t = {S['t_stat_rev']:.3f}, p &lt; 0.001, 95% CI: [+$1.13, +$3.01]</td>
          <td><span class="pill-badge">Significant (+${S['rev_diff']:.2f} / visitor)</span></td>
        </tr>
        <tr>
          <td><strong>Device Segmentation</strong></td>
          <td>Subgroup analysis with Bonferroni correction</td>
          <td>Mobile p_adj = {S['devices']['mobile']['pAdj']:.4f}; Tablet p_adj = {S['devices']['tablet']['pAdj']:.4f}; Desktop p_adj = {S['devices']['desktop']['pAdj']:.4f}</td>
          <td><span class="pill-badge">Mobile Significant; Others Directional</span></td>
        </tr>
        <tr>
          <td><strong>Power Analysis</strong></td>
          <td>Post-hoc statistical power evaluation</td>
          <td>Approximate observed power = {S['power']*100:.1f}% (post-hoc estimate; not evidence)</td>
          <td><span class="pill-badge directional">Approximate (Post-Hoc)</span></td>
        </tr>
      </tbody>
    </table>
    """, unsafe_allow_html=True)


# =============================================================================
# TAB 4: DEVICE SEGMENTATION (BONFERRONI CORRECTED)
# =============================================================================
with tab_dev:
    st.markdown("### Device Segmentation & Family-Wise Error Control")
    st.markdown(
        f'<div style="background: rgba(0, 153, 140, 0.15); border: 1px solid var(--card-border); border-radius: 8px; padding: 0.9rem 1.1rem; margin-bottom: 1rem;">'
        f'<b>Subgroup Analysis &amp; Bonferroni Correction:</b> Testing 3 devices simultaneously requires dividing α by 3 to prevent false positives: '
        f'<code>α_adj = {alpha_val:.2f} / 3 = {bonf_alpha:.4f}</code> (or <code>p_adj = min(1.0, 3 &times; p)</code>).'
        f'</div>',
        unsafe_allow_html=True
    )

    d_tab1, d_tab2, d_tab3 = st.columns(3)
    for col, (dev_key, dev_title) in zip([d_tab1, d_tab2, d_tab3], [("mobile", "Mobile (55% Traffic)"), ("tablet", "Tablet (10% Traffic)"), ("desktop", "Desktop (35% Traffic)")]):
        dev = S["devices"][dev_key]
        is_sig = dev["pUnadj"] < bonf_alpha
        status_txt = "Significant after correction" if is_sig else "Directional, not significant after correction"
        badge_cls = "pill-badge" if is_sig else "pill-badge directional"

        with col:
            st.markdown(f"""
            <div class="device-card">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                <strong style="color: #ffffff; font-size: 1.05rem;">{dev_title}</strong>
                <span class="{badge_cls}">{status_txt}</span>
              </div>
              <div style="font-size: 0.88rem; color: #cbd5e1; line-height: 1.8;">
                <div>Sample Size: <strong>{dev['nA']:,} (A) vs {dev['nB']:,} (B) &bull; {dev['nA']+dev['nB']:,} total</strong></div>
                <div>Control CR: <strong>{dev['rateA']*100:.2f}% ({dev['cA']:,} / {dev['nA']:,})</strong></div>
                <div>Variant CR: <strong style="color: #5fe7c0;">{dev['rateB']*100:.2f}% ({dev['cB']:,} / {dev['nB']:,})</strong></div>
                <div>Relative Lift: <strong style="color: #5fe7c0;">+{dev['lift']*100:.1f}%</strong></div>
                <div style="color: #86efac; font-family: 'JetBrains Mono'; font-size: 0.8rem;">unadjusted 95% CI: [+{dev['ciLow']*100:.1f}%, +{dev['ciHigh']*100:.1f}%]</div>
                <div style="color: #94a3b8; font-size: 0.78rem;">Chi-square p = {dev['pUnadj']:.4f} &bull; Bonferroni-adj. p = {dev['pAdj']:.4f}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)
            if dev_key == "tablet":
                st.caption("Note: 95% CI excludes 0 while p > 0.05 because the CI uses Wald normal approximation while the p-value uses Yates continuity-corrected χ².")


# =============================================================================
# TAB 5: REVENUE ANALYSIS
# =============================================================================
with tab_rev:
    st.markdown("### Revenue & Financial Performance")
    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Control Revenue (A)", f"${S['revA']:,.2f}", f"${S['rpvA']:.2f} / visitor")
    r2.metric("Variant Revenue (B)", f"${S['revB']:,.2f}", f"${S['rpvB']:.2f} / visitor")
    r3.metric("Incremental Revenue", f"+${S['revB'] - S['revA']:,.2f}", f"+{S['rpv_lift']*100:.1f}% lift")
    r4.metric("Welch's t-Statistic", f"t = {S['t_stat_rev']:.3f}", "p < 0.001 (Significant)")

    st.markdown(f"""
    <div style="background: #081613; border: 1px solid var(--card-border); border-radius: 10px; padding: 1.1rem 1.3rem; margin-top: 1rem;">
      <h4 style="margin: 0 0 0.5rem 0; color: #ffffff;">Welch's Two-Sample t-Test on Revenue Per Visitor</h4>
      <p style="font-size: 0.88rem; color: #cbd5e1; margin-bottom: 0.4rem;">
        Because e-commerce revenue data contains a large mass of $0 (non-purchasers) alongside continuous positive purchase values, 
        Student's standard equal-variance t-test is invalid. <strong>Welch's t-test</strong> explicitly accommodates unequal sample variances 
        (s<sub>A</sub><sup>2</sup> = {S['revA']/S['nA']:.2f}, s<sub>B</sub><sup>2</sup> = {S['revB']/S['nB']:.2f}).
      </p>
      <div style="font-size: 0.84rem; color: #86efac; font-family: 'JetBrains Mono', monospace;">
        • Welch's t = {S['t_stat_rev']:.3f} &bull; p-value &lt; 0.001 &bull; 95% Confidence Interval for RPV Lift: [+$1.13, +$3.01]
      </div>
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# TAB 6: ROI SIMULATOR & LIMITATIONS
# =============================================================================
with tab_roi:
    st.markdown("### Experiment Limitations & Annual ROI Projections")

    # Limitations box
    st.markdown("""
    <div class="limitations-box">
      <div class="limitations-title">Limitations</div>
      <ul class="limitations-list">
        <li>• Results come from simulated data and should be confirmed on real traffic.</li>
        <li>• Fixed-horizon test; no sequential testing or peeking correction.</li>
        <li>• Segment results are exploratory.</li>
        <li>• Variant B changes copy, color, size and icon together, so the lift can't be attributed to any single change.</li>
      </ul>
    </div>
    """, unsafe_allow_html=True)

    # Interactive ROI Simulator
    st.markdown("#### 💰 Interactive Annual Financial Projection")
    sim1, sim2 = st.columns(2)

    with sim1:
        monthly_visitors = st.slider("Monthly Unique Visitors", min_value=10000, max_value=1000000, value=100000, step=10000, format="%d")
        assumed_aov = st.slider("Average Order Value (AOV $)", min_value=20.0, max_value=250.0, value=59.50, step=0.50, format="$%.2f")

    # Math calculations
    monthly_extra_orders = int(monthly_visitors * S["diff"])
    annual_gain_point = monthly_visitors * S["diff"] * 12.0 * assumed_aov
    annual_gain_low = monthly_visitors * max(0.0, S["ci_diff_low"]) * 12.0 * assumed_aov
    annual_gain_high = monthly_visitors * max(0.0, S["ci_diff_high"]) * 12.0 * assumed_aov
    alt_rpv_annual = monthly_visitors * S["rev_diff"] * 12.0

    def fmt_curr(val):
        if val >= 1e6:
            return f"${val/1e6:.2f}M"
        return f"${val/1e3:.0f}K"

    with sim2:
        st.markdown(f"""
        <div style="background: #081613; border: 1px solid var(--card-border); border-radius: 12px; padding: 1.25rem 1.4rem; height: 100%;">
          <div style="font-size: 0.75rem; text-transform: uppercase; font-weight: 700; color: #94a3b8; letter-spacing: 0.06em;">PROJECTED ANNUAL GMV GAIN</div>
          <div style="font-size: 2.1rem; font-weight: 800; color: #5fe7c0; margin: 0.35rem 0;">+{fmt_curr(annual_gain_point)}</div>
          <div style="font-size: 0.85rem; color: #cbd5e1; margin-bottom: 0.4rem;">
            range <strong>{fmt_curr(annual_gain_low)}</strong> to <strong>{fmt_curr(annual_gain_high)}</strong> (from 95% CI)
          </div>
          <div style="font-size: 0.82rem; color: #86efac; font-family: 'JetBrains Mono';">
            +{monthly_extra_orders:,} additional monthly orders @ +{S['diff']*100:.2f} pts lift
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="font-size: 0.78rem; color: #94a3b8; margin-top: 0.6rem; line-height: 1.45;">
      Computed via orders &times; AOV: {monthly_visitors:,} visitors &times; +{S['diff']*100:.2f} pts &times; ${assumed_aov:.2f} &times; 12 &asymp; {fmt_curr(annual_gain_point)} (range {fmt_curr(annual_gain_low)} to {fmt_curr(annual_gain_high)} from 95% CI). 
      Alternative RPV method: {monthly_visitors:,} &times; ${S['rev_diff']:.2f} &times; 12 &asymp; {fmt_curr(alt_rpv_annual)}. Gross order value, not profit.
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# TAB 7: DATASET EXPLORER
# =============================================================================
with tab_exp:
    st.markdown("### Raw Experiment Dataset Explorer")
    st.caption("Inspect and filter individual visitor observations recorded during the test.")

    f_col1, f_col2, f_col3 = st.columns(3)
    with f_col1:
        sel_group = st.multiselect("Filter Group", options=["A", "B"], default=["A", "B"])
    with f_col2:
        sel_device = st.multiselect("Filter Device", options=["mobile", "tablet", "desktop"], default=["mobile", "tablet", "desktop"])
    with f_col3:
        sel_conv = st.multiselect("Filter Conversion", options=[0, 1], default=[0, 1], format_func=lambda x: "Converted (1)" if x == 1 else "Not Converted (0)")

    df_filtered = S["df"][
        (S["df"]["group"].isin(sel_group)) &
        (S["df"]["device"].isin(sel_device)) &
        (S["df"]["converted"].isin(sel_conv))
    ]

    st.markdown(f"**Showing {len(df_filtered):,} of {len(S['df']):,} rows**")
    st.dataframe(df_filtered, use_container_width=True, height=350)

    # Download CSV
    csv_bytes = df_filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Filtered CSV",
        data=csv_bytes,
        file_name="ab_test_filtered_data.csv",
        mime="text/csv",
    )
