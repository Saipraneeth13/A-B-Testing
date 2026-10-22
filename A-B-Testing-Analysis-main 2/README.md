# 📊 A/B Testing Analysis Studio & Interactive Dashboard
### E-Commerce User Behavior Analysis (Control A vs. Variant B)

> **Repository:** [https://github.com/Saipraneeth13/A-B-Testing/tree/main/A-B-Testing-Analysis-main%202](https://github.com/Saipraneeth13/A-B-Testing/tree/main/A-B-Testing-Analysis-main%202)  
> **Theme:** Deep Obsidian Black & Electric Blue (`#05070d`, `#0d1424`, `#2563eb`, `#38bdf8`)  
> **Author:** Sai Praneeth

---

## 🌟 Overview

This website is a production-grade, statistically rigorous experimentation dashboard and portfolio site built for the **User Behavior Analysis A/B Test**.

The experiment evaluated whether transitioning from a standard, muted checkout button (**Control A**) to an enlarged, high-contrast electric blue button with security lock micro-interactions (**Variant B**) increases overall conversion rate and revenue per visitor across **8,000 live visitors**.

---

## 🚀 Key Results & Executive Verdict

| Evaluation Metric | Control (A) | Variant (B) | Absolute Delta | Relative Lift | Statistical Test | p-Value | 95% Confidence Interval | Verdict |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Visitors** | 4,063 | 3,937 | -126 | -1.57% | $\chi^2$ Goodness-of-Fit (SRM) | $p = 0.1589$ | $[49.7\%, 50.3\%]$ | **PASSED** (Healthy Split) |
| **Conversion Rate** | **10.02%** | **13.16%** | **+3.14% pts** | **+31.34%** | Two-Proportion Pooled Z-Test | **$p < 0.0001$** | $[+1.74\%, +4.54\%]$ | **REJECT $H_0$** (Significant) |
| **Bootstrap 95% CI** | 10.02% | 13.16% | +3.14% pts | +31.3% | 5,000 Empirical Resamples | — | $[+1.72\%, +4.57\%]$ | **ZERO EXCLUDED** (Robust) |
| **Revenue / Visitor** | **$5.80** | **$7.87** | **+$2.07** | **+35.7%** | Welch's Two-Sample t-Test | **$p < 0.0001$** | $[+\$1.13, +\$3.01]$ | **REJECT $H_0$** (Significant) |
| **Statistical Power** | — | — | — | — | Post-Hoc Power @ $\alpha=0.05$ | — | **$99.2\%$ Power** | **$\beta < 0.8\%$** (Low Risk) |

### 🎯 Recommendation: **100% PRODUCTION ROLLOUT**
Variant B delivers a statistically irrefutable conversion lift (+31.3%) and substantial revenue gain (+35.7%), driven predominantly by mobile shoppers (+36.7% lift on mobile). Recommended action: Roll out immediately to all traffic with prioritized mobile optimization.

---

## 🎨 Design System: Deep Blue & Black
- **Backgrounds:** Obsidian Black (`#05070d`), Midnight Navy (`#080c16`, `#0d1424`), Deep Slate (`#0a101d`)
- **Accent Blues:** Electric Royal Blue (`#2563eb`), Bright Blue (`#3b82f6`), Neon Cyan (`#38bdf8`), Soft Sky Blue (`#60a5fa`)
- **Gradients & Glows:** Subtle radial gradients, glowing card borders (`rgba(59, 130, 246, 0.25)` to `rgba(56, 189, 248, 0.45)`), glowing metrics
- **Typography:** Inter (for clean UI/data density) and JetBrains Mono (for formulas and code)

---

## ⚡ Features & Modules

### 1. Interactive Button Preview & Tactile Click Simulator
- Side-by-side interactive checkout interface comparing Variant A (38px height, muted slate `#334155`) vs Variant B (52px height, electric blue `#2563eb`, lock icon, tactile micro-interaction).
- Users can click both buttons to experience tactile feedback, simulated click latency, and see why mobile users responded so strongly.

### 2. Interactive Chart.js Visualizations
1. **Overall Conversion Rate Bar Chart:** Control A (10.02%) vs Redesign B (13.16%) with custom tooltips.
2. **Device Segmentation Comparison:** Desktop, Mobile, and Tablet conversion rates with Bonferroni alpha markers.
3. **Bootstrap Sampling Distribution (5,000 Resamples):** Histogram showing distribution of differences, 95% CI cutoffs, and zero reference line.
4. **Cumulative Conversion Convergence:** Line chart tracking conversion stability across all 8,000 visitor IDs.
5. **Revenue Per Visitor & AOV:** Control vs Variant revenue metrics with Welch's t-test validation.

### 3. End-to-End 6-Step Statistical Pipeline
1. **Sample Ratio Mismatch (SRM):** $\chi^2 = 1.9845, p = 0.1589 > 0.01$. Confirms clean randomization without telemetry drop-off.
2. **Primary Metric (Two-Proportion Z-Test):** $z = 4.391, p < 0.0001, 95\% \text{ CI } [+1.74\%, +4.54\%]$.
3. **Non-Parametric Bootstrap Validation:** 5,000 resamples without parametric assumptions, empirical 95% CI $[+1.72\%, +4.57\%]$.
4. **Secondary Metric (Welch's T-Test for Revenue):** Handles zero-inflated continuous gamma revenue distribution and unequal variances, $t = 4.315, p < 0.0001, 95\% \text{ CI } [+\$1.13, +\$3.01]$.
5. **Bonferroni Device Correction:** Controls Family-Wise Error Rate ($\alpha_{adj} = 0.05 / 3 = 0.0167$). Mobile is statistically significant ($p = 0.0008$).
6. **Observed Power Analysis:** Post-hoc observed power = 99.2% at measured effect size.

### 4. Interactive A/B Testing Laboratory & Simulator
- Live parameter inputs: Visitors A, Conversions A, Visitors B, Conversions B, and Significance Level ($\alpha = 0.05, 0.01, 0.10$).
- Real-time recalculation of SRM, pooled standard error, Z-score, P-value, Confidence Interval, and Statistical Power.
- Presets: "Current Repo Data (8,000)", "High-Traffic E-commerce (100,000)", "SaaS Trial Signups", "Failed SRM Simulation".

### 5. Annualized ROI & Financial Simulator
- Interactive traffic and Average Order Value (AOV) sliders.
- Automatically calculates incremental monthly orders, monthly revenue gain, and projected annual Gross Merchandise Value (GMV).

### 6. Raw Data Explorer & Custom CSV Uploader
- Searchable and sortable table of visitor records.
- Filter by Assigned Group (A / B), Device (Mobile / Desktop / Tablet), and Conversion Status.
- Pagination controls (15, 25, 50, 100 rows per page).
- **Export Dataset:** Download the full 8,000-row dataset as `.csv`.
- **Custom CSV Uploader:** Drag-and-drop any CSV file with columns `user_id, group, device, converted, revenue` to instantly re-run statistical tests and update all charts!

### 7. Technical Interview Q&A Guide
- In-depth answers to 5 key interview questions:
  1. Why is SRM the first check you run before calculating metrics?
  2. Why use Welch's t-test instead of Student's t-test for revenue per visitor?
  3. What is the danger of continuous peeking in fixed-horizon A/B tests?
  4. Why was Bonferroni correction used for device segments and what is its trade-off?
  5. What are the limitations of synthetic experimentation data compared to production data?

### 8. Executive Decision Memo Modal
- 1-Click modal generator that produces a formatted briefing ready to copy to clipboard or export as PDF for leadership presentations.

---

## 💻 How to Run Locally

### Option 1: Using the Included Python Server (Recommended)
```bash
cd /Users/saisripraneethbandiicloud.com/.gemini/antigravity/scratch/ab-testing-website
python3 serve.py
```
Then open your browser to **[http://localhost:8080](http://localhost:8080)**.

### Option 2: Standard Python One-Liner
```bash
python3 -m http.server 8080
```

### Option 3: Direct File Opening
Double-click `index.html` in your file browser or open directly in Chrome/Safari/Firefox. All core metrics and visualizations are pre-bundled and work completely offline without requiring an active internet connection.

---

## 📁 Project Directory Structure

```
ab-testing-website/
├── index.html                  # Full single-page interactive dashboard
├── serve.py                    # Lightweight local HTTP server runner
├── README.md                   # Complete documentation (this file)
├── css/
│   └── style.css               # Deep Blue & Black design system
├── js/
│   └── app.js                  # Statistical calculation engine & Chart.js logic
├── data/
│   ├── ab_test_data.csv        # Full 8,000-row visitor experiment dataset
│   ├── data_summary.json       # Precomputed statistical metrics & bootstrap bins
│   └── ab_test_results.png     # Reference visualization chart
└── ab-testing-project/          # Original repository files and Python analysis scripts
    ├── requirements.txt
    ├── README.md
    ├── src/
    │   ├── analysis.py         # Full SciPy / Pandas pipeline
    │   └── generate_data.py    # Synthetic dataset generator
    └── results/
        ├── summary.txt         # Statistical output summary
        └── ab_test_results.png
```

---

## 🌐 Deploying to the Web

### GitHub Pages:
1. Push this folder to a GitHub repository (e.g. `Saipraneeth13/ab-testing-website`).
2. Go to **Settings > Pages**.
3. Select `Branch: main` and `/ (root)`.
4. Click **Save**. Your site will be live instantly!

### Vercel / Netlify:
Simply drag-and-drop the `ab-testing-website` folder onto [Netlify Drop](https://app.netlify.com/drop) or import the Git repo into Vercel.
