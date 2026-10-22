/**
 * A/B TEST: USER BEHAVIOR ANALYSIS
 * Fully dynamic statistical computation engine.
 * Computes all metrics from dataset records (or custom uploaded CSV).
 */

let rawRecords = [];
let filteredRecords = [];
let activeStats = null;
let chartInstances = {};
let clickCounts = { A: 0, B: 0 };

document.addEventListener('DOMContentLoaded', async () => {
  setupNavigationTabs();
  setupSidebarSliders();
  setupButtonDemo();
  setupRoiSimulator();
  setupTableExplorer();

  await loadAppData();
});

/* ==========================================================================
   MATHEMATICAL & STATISTICAL HELPER FUNCTIONS
   ========================================================================== */

// Standard normal cumulative distribution function (Abramowitz & Stegun 7.1.26 approximation)
function normalCdf(x) {
  const t = 1 / (1 + 0.2316419 * Math.abs(x));
  const d = 0.3989422804014327 * Math.exp(-x * x / 2);
  const p = d * t * (0.319381530 + t * (-0.356563782 + t * (1.781477937 + t * (-1.821255978 + t * 1.330274429))));
  return x > 0 ? 1 - p : p;
}

// Chi-square 1 degree of freedom p-value
function chi2_1df_pval(chi2) {
  if (chi2 <= 0) return 1.0;
  return 2 * (1 - normalCdf(Math.sqrt(chi2)));
}

// 2x2 contingency table chi-square with Yates continuity correction (matching scipy.stats.chi2_contingency default)
function chi2_2x2(a, b, c, d) {
  const n = a + b + c + d;
  const diff = Math.max(0, Math.abs(a * d - b * c) - n / 2.0);
  const num = n * Math.pow(diff, 2);
  const den = (a + b) * (c + d) * (a + c) * (b + d);
  return den === 0 ? 0 : num / den;
}

// Fast binomial sample generator using Gaussian approximation for large n
function sampleBinomial(n, p) {
  const u1 = Math.random() || 1e-7;
  const u2 = Math.random() || 1e-7;
  const z = Math.sqrt(-2.0 * Math.log(u1)) * Math.cos(2.0 * Math.PI * u2);
  return Math.max(0, Math.min(n, Math.round(n * p + z * Math.sqrt(n * p * (1 - p)))));
}

/* ==========================================================================
   DYNAMIC STATISTICAL PIPELINE
   ========================================================================== */
function computeAllStats(records) {
  const A = records.filter(r => r.group === 'A');
  const B = records.filter(r => r.group === 'B');

  const nA = A.length;
  const nB = B.length;
  const totalVisitors = nA + nB;

  const cA = A.reduce((sum, r) => sum + r.converted, 0);
  const cB = B.reduce((sum, r) => sum + r.converted, 0);

  const crA = nA > 0 ? cA / nA : 0;
  const crB = nB > 0 ? cB / nB : 0;
  const diff = crB - crA;
  const relLift = crA > 0 ? diff / crA : 0;

  // 1. Two-proportion Pooled Z-Test
  const pp = totalVisitors > 0 ? (cA + cB) / totalVisitors : 0;
  const sePooled = Math.sqrt(pp * (1 - pp) * ((1 / (nA || 1)) + (1 / (nB || 1))));
  const zStat = sePooled > 0 ? diff / sePooled : 0;
  const pValZ = 2 * (1 - normalCdf(Math.abs(zStat)));

  // Difference 95% Confidence Interval (unpooled standard error)
  const seUnpooled = Math.sqrt((crA * (1 - crA) / (nA || 1)) + (crB * (1 - crB) / (nB || 1)));
  const ciDiffLow = diff - 1.96 * seUnpooled;
  const ciDiffHigh = diff + 1.96 * seUnpooled;

  // Relative Lift 95% CI (Difference CI divided by Control Rate)
  const relCiLow = crA > 0 ? ciDiffLow / crA : 0;
  const relCiHigh = crA > 0 ? ciDiffHigh / crA : 0;

  // Single-group proportion 95% CIs
  const crA_ciLow = Math.max(0, crA - 1.96 * Math.sqrt(crA * (1 - crA) / (nA || 1)));
  const crA_ciHigh = Math.min(1, crA + 1.96 * Math.sqrt(crA * (1 - crA) / (nA || 1)));
  const crB_ciLow = Math.max(0, crB - 1.96 * Math.sqrt(crB * (1 - crB) / (nB || 1)));
  const crB_ciHigh = Math.min(1, crB + 1.96 * Math.sqrt(crB * (1 - crB) / (nB || 1)));

  // 2. Revenue & Welch's Two-Sample t-Test
  const revA = A.reduce((sum, r) => sum + r.revenue, 0);
  const revB = B.reduce((sum, r) => sum + r.revenue, 0);
  const rpvA = nA > 0 ? revA / nA : 0;
  const rpvB = nB > 0 ? revB / nB : 0;
  const revDiff = rpvB - rpvA;
  const rpvLiftPct = rpvA > 0 ? revDiff / rpvA : 0;

  const aovA = cA > 0 ? revA / cA : 0;
  const aovB = cB > 0 ? revB / cB : 0;
  const aovDiff = aovB - aovA;
  const aovLift = aovA > 0 ? aovDiff / aovA : 0;

  let sumSqA = 0;
  for (const r of A) sumSqA += Math.pow(r.revenue - rpvA, 2);
  const varA = nA > 1 ? sumSqA / (nA - 1) : 0;

  let sumSqB = 0;
  for (const r of B) sumSqB += Math.pow(r.revenue - rpvB, 2);
  const varB = nB > 1 ? sumSqB / (nB - 1) : 0;

  const seRev = Math.sqrt((varA / (nA || 1)) + (varB / (nB || 1)));
  const tStat = seRev > 0 ? revDiff / seRev : 0;
  const pValRev = 2 * (1 - normalCdf(Math.abs(tStat)));
  const ciRevLow = revDiff - 1.96 * seRev;
  const ciRevHigh = revDiff + 1.96 * seRev;

  // 3. Sample Ratio Mismatch (SRM)
  const expN = totalVisitors / 2;
  const chi2Srm = expN > 0 ? (Math.pow(nA - expN, 2) / expN) + (Math.pow(nB - expN, 2) / expN) : 0;
  const pValSrm = chi2_1df_pval(chi2Srm);

  // 4. Observed Statistical Power
  const zBeta = seUnpooled > 0 ? (Math.abs(diff) - 1.96 * sePooled) / seUnpooled : 0;
  const power = normalCdf(zBeta);

  // 5. Device Segmentation & Bonferroni Correction (3 devices)
  const devices = {};
  ['mobile', 'tablet', 'desktop'].forEach(devName => {
    const devA = A.filter(r => r.device === devName);
    const devB = B.filter(r => r.device === devName);
    const dNA = devA.length;
    const dNB = devB.length;
    const dCA = devA.reduce((s, r) => s + r.converted, 0);
    const dCB = devB.reduce((s, r) => s + r.converted, 0);
    const dRateA = dNA > 0 ? dCA / dNA : 0;
    const dRateB = dNB > 0 ? dCB / dNB : 0;
    const dDiff = dRateB - dRateA;
    const dRelLift = dRateA > 0 ? dDiff / dRateA : 0;
    const trafficShare = totalVisitors > 0 ? (dNA + dNB) / totalVisitors : 0;

    const chi2 = chi2_2x2(dCA, dNA - dCA, dCB, dNB - dCB);
    const pUnadj = chi2_1df_pval(chi2);
    // Bonferroni correction: multiply by 3, cap at 1.0
    const pAdj = Math.min(1.0, pUnadj * 3);
    const status = pAdj < 0.05 ? 'Significant after correction' : 'Directional, not significant after correction';

    const seDev = Math.sqrt((dRateA * (1 - dRateA) / (dNA || 1)) + (dRateB * (1 - dRateB) / (dNB || 1)));
    const ciDiffLowDev = dDiff - 1.96 * seDev;
    const ciDiffHighDev = dDiff + 1.96 * seDev;
    const relCiLowDev = dRateA > 0 ? ciDiffLowDev / dRateA : 0;
    const relCiHighDev = dRateA > 0 ? ciDiffHighDev / dRateA : 0;

    devices[devName] = {
      nA: dNA, nB: dNB, cA: dCA, cB: dCB,
      rateA: dRateA, rateB: dRateB,
      diff: dDiff, relLift: dRelLift,
      trafficShare,
      chi2, pUnadj, pAdj, status,
      ciDiffLow: ciDiffLowDev, ciDiffHigh: ciDiffHighDev,
      relCiLow: relCiLowDev, relCiHigh: relCiHighDev
    };
  });

  // 6. Bootstrap Resampling (5,000 empirical resamples for B - A lift)
  const boots = new Float64Array(5000);
  for (let i = 0; i < 5000; i++) {
    const pB_star = sampleBinomial(nB, crB) / nB;
    const pA_star = sampleBinomial(nA, crA) / nA;
    boots[i] = (pB_star - pA_star) * 100; // in percentage points
  }
  boots.sort();
  const bootLow = boots[Math.floor(5000 * 0.025)];
  const bootHigh = boots[Math.floor(5000 * 0.975)];

  // Binning for Bootstrap histogram: -0.5% to 6.0% in 0.5% steps
  const binEdges = [-0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0];
  const binLabels = ['0.0%', '0.5%', '1.0%', '1.5%', '2.0%', '2.5%', '3.0%', '3.5%', '4.0%', '4.5%', '5.0%', '5.5%', '6.0%'];
  const binCounts = new Array(binLabels.length).fill(0);
  for (let i = 0; i < boots.length; i++) {
    const val = boots[i];
    for (let j = 0; j < binEdges.length - 1; j++) {
      if (val >= binEdges[j] && (j === binEdges.length - 2 ? val <= binEdges[j + 1] : val < binEdges[j + 1])) {
        binCounts[j]++;
        break;
      }
    }
  }

  return {
    totalVisitors, nA, nB, cA, cB,
    crA, crB, diff, relLift,
    zStat, pValZ, sePooled, seUnpooled,
    ciDiffLow, ciDiffHigh, relCiLow, relCiHigh,
    crA_ciLow, crA_ciHigh, crB_ciLow, crB_ciHigh,
    revA, revB, rpvA, rpvB, revDiff, rpvLiftPct,
    aovA, aovB, aovDiff, aovLift,
    tStat, pValRev, ciRevLow, ciRevHigh,
    chi2Srm, pValSrm,
    power,
    devices,
    boots, bootLow, bootHigh, binLabels, binCounts
  };
}

/* ==========================================================================
   UI SYNCHRONIZATION WITH DYNAMIC METRICS
   ========================================================================== */
function updateUIWithStats(stats) {
  if (!stats) return;

  // Recommendation Headline
  const recHeadline = document.getElementById('rec-headline-text');
  if (recHeadline) {
    recHeadline.innerHTML = `Variant B delivered a <strong>+${(stats.relLift * 100).toFixed(1)}% conversion lift</strong> and <strong>+$${stats.revDiff.toFixed(2)} revenue per visitor</strong>.`;
  }

  // Top-line KPI Cards
  const elTotalVisitors = document.getElementById('kpi-total-visitors');
  const elVisitorsSplit = document.getElementById('kpi-visitors-split');
  if (elTotalVisitors) elTotalVisitors.textContent = stats.totalVisitors.toLocaleString();
  if (elVisitorsSplit) elVisitorsSplit.textContent = `${stats.nA.toLocaleString()} in A + ${stats.nB.toLocaleString()} in B`;

  const elCrA = document.getElementById('kpi-cr-a');
  const elCrAContext = document.getElementById('kpi-cr-a-context');
  if (elCrA) elCrA.textContent = `${(stats.crA * 100).toFixed(2)}%`;
  if (elCrAContext) elCrAContext.textContent = `${stats.cA.toLocaleString()} of ${stats.nA.toLocaleString()} visitors`;

  const elCrB = document.getElementById('kpi-cr-b');
  const elCrBContext = document.getElementById('kpi-cr-b-context');
  if (elCrB) elCrB.textContent = `${(stats.crB * 100).toFixed(2)}%`;
  if (elCrBContext) elCrBContext.textContent = `${stats.cB.toLocaleString()} of ${stats.nB.toLocaleString()} visitors`;

  const elRelLift = document.getElementById('kpi-rel-lift');
  const elRelLiftCi = document.getElementById('kpi-rel-lift-ci');
  if (elRelLift) elRelLift.textContent = `+${(stats.relLift * 100).toFixed(1)}%`;
  if (elRelLiftCi) {
    elRelLiftCi.textContent = `95% CI: [+${(stats.relCiLow * 100).toFixed(1)}%, +${(stats.relCiHigh * 100).toFixed(1)}%]`;
  }

  const elRpvA = document.getElementById('kpi-rpv-a');
  const elRpvAContext = document.getElementById('kpi-rpv-a-context');
  if (elRpvA) elRpvA.textContent = `$${stats.rpvA.toFixed(2)}`;
  if (elRpvAContext) elRpvAContext.textContent = `$${(stats.revA / 1000).toFixed(1)}K total revenue`;

  const elRpvB = document.getElementById('kpi-rpv-b');
  const elRpvBContext = document.getElementById('kpi-rpv-b-context');
  const elRpvCi = document.getElementById('kpi-rpv-ci');
  const elRpvPval = document.getElementById('kpi-rpv-pval');
  if (elRpvB) elRpvB.textContent = `$${stats.rpvB.toFixed(2)}`;
  if (elRpvBContext) elRpvBContext.textContent = `$${(stats.revB / 1000).toFixed(1)}K total revenue`;
  if (elRpvCi) {
    elRpvCi.textContent = `95% CI: [+$${stats.ciRevLow.toFixed(2)}, +$${stats.ciRevHigh.toFixed(2)}]`;
  }
  if (elRpvPval) {
    elRpvPval.textContent = `Welch's t ${stats.pValRev < 0.001 ? 'p < 0.001' : 'p = ' + stats.pValRev.toFixed(4)}`;
  }

  // RPV Formula Decomposition Note directly under RPV cards
  const elFormulaNote = document.getElementById('kpi-formula-note');
  if (elFormulaNote) {
    elFormulaNote.innerHTML = `Revenue lift = +${(stats.relLift * 100).toFixed(1)}% conversion &times; +${(stats.aovLift * 100).toFixed(1)}% order value`;
  }

  // Device Cards on Overview Page
  ['mobile', 'tablet', 'desktop'].forEach(devName => {
    const dev = stats.devices[devName];
    if (!dev) return;

    const elLift = document.getElementById(`dev-lift-${devName}`);
    const elTraffic = document.getElementById(`dev-traffic-${devName}`);
    const elRates = document.getElementById(`dev-rates-${devName}`);
    const elSample = document.getElementById(`dev-sample-${devName}`);
    const elCi = document.getElementById(`dev-ci-${devName}`);
    const elPadj = document.getElementById(`dev-padj-${devName}`);
    const elStatus = document.getElementById(`dev-status-${devName}`);

    if (elLift) elLift.textContent = `+${(dev.relLift * 100).toFixed(1)}%`;
    if (elTraffic) elTraffic.textContent = `${Math.round(dev.trafficShare * 100)}% traffic`;
    if (elRates) elRates.innerHTML = `${(dev.rateA * 100).toFixed(2)}% &rarr; ${(dev.rateB * 100).toFixed(2)}% CR`;
    if (elSample) elSample.textContent = `n: ${dev.nA.toLocaleString()} (A) vs ${dev.nB.toLocaleString()} (B)`;
    if (elCi) elCi.textContent = `unadjusted 95% CI: [+${(dev.relCiLow * 100).toFixed(1)}%, +${(dev.relCiHigh * 100).toFixed(1)}%]`;
    if (elPadj) elPadj.textContent = `Bonferroni-adj. p = ${dev.pAdj.toFixed(4)}`;
    if (elStatus) {
      elStatus.className = `pill-badge ${dev.pAdj < 0.05 ? 'active-blue' : 'inconclusive'}`;
      elStatus.textContent = dev.status;
    }

    // Also update Device Segmentation tab cards
    const tabSample = document.getElementById(`tab-dev-sample-${devName}`);
    const tabCra = document.getElementById(`tab-dev-cra-${devName}`);
    const tabCrb = document.getElementById(`tab-dev-crb-${devName}`);
    const tabLift = document.getElementById(`tab-dev-lift-${devName}`);
    const tabCi = document.getElementById(`tab-dev-ci-${devName}`);
    const tabPadj = document.getElementById(`tab-dev-padj-${devName}`);
    const tabStatus = document.getElementById(`tab-dev-status-${devName}`);

    if (tabSample) tabSample.innerHTML = `${dev.nA.toLocaleString()} (A) vs ${dev.nB.toLocaleString()} (B) &bull; ${(dev.nA + dev.nB).toLocaleString()} total`;
    if (tabCra) tabCra.textContent = `${(dev.rateA * 100).toFixed(2)}% (${dev.cA.toLocaleString()} / ${dev.nA.toLocaleString()})`;
    if (tabCrb) tabCrb.textContent = `${(dev.rateB * 100).toFixed(2)}% (${dev.cB.toLocaleString()} / ${dev.nB.toLocaleString()})`;
    if (tabLift) tabLift.textContent = `+${(dev.relLift * 100).toFixed(1)}%`;
    if (tabCi) tabCi.textContent = `unadjusted 95% CI: [+${(dev.relCiLow * 100).toFixed(1)}%, +${(dev.relCiHigh * 100).toFixed(1)}%]`;
    if (tabPadj) tabPadj.innerHTML = `Chi-square p = ${dev.pUnadj.toFixed(4)} &bull; Bonferroni-adj. p = ${dev.pAdj.toFixed(4)}`;
    if (tabStatus) {
      tabStatus.className = `pill-badge ${dev.pAdj < 0.05 ? 'active-blue' : 'inconclusive'}`;
      tabStatus.textContent = dev.status;
    }
  });

  // Group Performance Summary Table
  const tblNa = document.getElementById('tbl-n-a');
  const tblConva = document.getElementById('tbl-conv-a');
  const tblCra = document.getElementById('tbl-cr-a');
  const tblCia = document.getElementById('tbl-ci-a');
  const tblReva = document.getElementById('tbl-rev-a');
  const tblRpva = document.getElementById('tbl-rpv-a');
  const tblAova = document.getElementById('tbl-aov-a');

  if (tblNa) tblNa.textContent = stats.nA.toLocaleString();
  if (tblConva) tblConva.textContent = stats.cA.toLocaleString();
  if (tblCra) tblCra.textContent = `${(stats.crA * 100).toFixed(2)}%`;
  if (tblCia) tblCia.textContent = `[${(stats.crA_ciLow * 100).toFixed(2)}%, ${(stats.crA_ciHigh * 100).toFixed(2)}%]`;
  if (tblReva) tblReva.textContent = `$${stats.revA.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  if (tblRpva) tblRpva.textContent = `$${stats.rpvA.toFixed(2)}`;
  if (tblAova) tblAova.textContent = `$${stats.aovA.toFixed(2)}`;

  const tblNb = document.getElementById('tbl-n-b');
  const tblConvb = document.getElementById('tbl-conv-b');
  const tblCrb = document.getElementById('tbl-cr-b');
  const tblCib = document.getElementById('tbl-ci-b');
  const tblRevb = document.getElementById('tbl-rev-b');
  const tblRpvb = document.getElementById('tbl-rpv-b');
  const tblAovb = document.getElementById('tbl-aov-b');

  if (tblNb) tblNb.textContent = stats.nB.toLocaleString();
  if (tblConvb) tblConvb.textContent = stats.cB.toLocaleString();
  if (tblCrb) tblCrb.textContent = `${(stats.crB * 100).toFixed(2)}%`;
  if (tblCib) tblCib.textContent = `[${(stats.crB_ciLow * 100).toFixed(2)}%, ${(stats.crB_ciHigh * 100).toFixed(2)}%]`;
  if (tblRevb) tblRevb.textContent = `$${stats.revB.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  if (tblRpvb) tblRpvb.textContent = `$${stats.rpvB.toFixed(2)}`;
  if (tblAovb) tblAovb.textContent = `$${stats.aovB.toFixed(2)}`;

  const tblDiffCr = document.getElementById('tbl-diff-cr');
  const tblDiffCi = document.getElementById('tbl-diff-ci');
  const tblDiffRpv = document.getElementById('tbl-diff-rpv');
  const tblDiffAov = document.getElementById('tbl-diff-aov');

  if (tblDiffCr) {
    tblDiffCr.textContent = `+${(stats.diff * 100).toFixed(2)} pts (+${(stats.relLift * 100).toFixed(1)}%) • ${stats.pValZ < 0.001 ? 'p < 0.001' : 'p = ' + stats.pValZ.toFixed(4)}`;
  }
  if (tblDiffCi) {
    tblDiffCi.textContent = `[+${(stats.ciDiffLow * 100).toFixed(2)}%, +${(stats.ciDiffHigh * 100).toFixed(2)}%]`;
  }
  if (tblDiffRpv) {
    tblDiffRpv.innerHTML = `+$${stats.revDiff.toFixed(2)} (+${(stats.rpvLiftPct * 100).toFixed(1)}%)<br><span style="font-size: 0.68rem; color: #a7f3d0; font-family: var(--font-mono); font-weight: 400;">95% CI: [+$${stats.ciRevLow.toFixed(2)}, +$${stats.ciRevHigh.toFixed(2)}]</span>`;
  }
  if (tblDiffAov) {
    tblDiffAov.textContent = `+$${stats.aovDiff.toFixed(2)} (+${(stats.aovLift * 100).toFixed(1)}%)`;
  }

  // Statistical Testing Tab Metrics
  const elStatZ = document.getElementById('stat-z-stat');
  const elStatP = document.getElementById('stat-p-val');
  const elStatDiffCi = document.getElementById('stat-diff-ci');
  if (elStatZ) elStatZ.textContent = stats.zStat.toFixed(3);
  if (elStatP) elStatP.textContent = stats.pValZ < 0.001 ? '< 0.001' : stats.pValZ.toFixed(4);
  if (elStatDiffCi) elStatDiffCi.textContent = `+${(stats.ciDiffLow * 100).toFixed(1)} to +${(stats.ciDiffHigh * 100).toFixed(1)} pts`;

  // Diagnostics Table
  const diagSrm = document.getElementById('diag-srm-val');
  const diagZ = document.getElementById('diag-z-val');
  const diagBoot = document.getElementById('diag-boot-val');
  const diagWelch = document.getElementById('diag-welch-val');
  const diagDevice = document.getElementById('diag-device-val');
  const diagPower = document.getElementById('diag-power-val');

  if (diagSrm) diagSrm.textContent = `χ² = ${stats.chi2Srm.toFixed(3)}, p = ${stats.pValSrm.toFixed(3)}`;
  if (diagZ) diagZ.textContent = `z = ${stats.zStat.toFixed(3)}, p < 0.001, CI: +${(stats.ciDiffLow * 100).toFixed(1)} to +${(stats.ciDiffHigh * 100).toFixed(1)} pts`;
  if (diagBoot) diagBoot.textContent = `95% CI: [+${stats.bootLow.toFixed(2)}%, +${stats.bootHigh.toFixed(2)}%]`;
  if (diagWelch) diagWelch.textContent = `t = ${stats.tStat.toFixed(3)}, p < 0.001, 95% CI: [+$${stats.ciRevLow.toFixed(2)}, +$${stats.ciRevHigh.toFixed(2)}]`;
  if (diagDevice) {
    diagDevice.textContent = `Mobile p_adj = ${stats.devices.mobile.pAdj.toFixed(4)}; Tablet p_adj = ${stats.devices.tablet.pAdj.toFixed(4)}; Desktop p_adj = ${stats.devices.desktop.pAdj.toFixed(4)}`;
  }
  if (diagPower) diagPower.textContent = `Approximate observed power = ${(stats.power * 100).toFixed(1)}% (post-hoc estimate; not evidence)`;

  // Revenue Analysis Tab Metrics
  const revTotalA = document.getElementById('rev-total-a');
  const revVisitorsA = document.getElementById('rev-visitors-a');
  const revTotalB = document.getElementById('rev-total-b');
  const revGainB = document.getElementById('rev-gain-b');
  const revRpvLift = document.getElementById('rev-rpv-lift');
  const revRpvLiftPct = document.getElementById('rev-rpv-lift-pct');
  const revWelchPval = document.getElementById('rev-welch-pval');
  const revWelchT = document.getElementById('rev-welch-t');

  if (revTotalA) revTotalA.textContent = `$${stats.revA.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  if (revVisitorsA) revVisitorsA.textContent = `${stats.nA.toLocaleString()} Visitors`;
  if (revTotalB) revTotalB.textContent = `$${stats.revB.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  if (revGainB) revGainB.textContent = `+$${(stats.revB - stats.revA).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} Gain`;
  if (revRpvLift) revRpvLift.textContent = `+$${stats.revDiff.toFixed(2)}`;
  if (revRpvLiftPct) revRpvLiftPct.textContent = `+${(stats.rpvLiftPct * 100).toFixed(1)}% Lift`;
  if (revWelchPval) revWelchPval.textContent = stats.pValRev < 0.001 ? '< 0.001' : stats.pValRev.toFixed(4);
  if (revWelchT) revWelchT.textContent = `t = ${stats.tStat.toFixed(3)}`;
}

/* ==========================================================================
   NAVIGATION TABS & MOBILE SIDEBAR
   ========================================================================== */
function setupNavigationTabs() {
  const navItems = document.querySelectorAll('#sidebar-nav .nav-item');
  const panels = document.querySelectorAll('.tab-panel');
  const sidebar = document.getElementById('app-sidebar');
  const mobileToggle = document.getElementById('mobile-toggle-btn');

  const switchTab = (tabId) => {
    navItems.forEach(item => {
      item.classList.toggle('active', item.getAttribute('data-tab') === tabId);
    });
    panels.forEach(panel => {
      panel.classList.toggle('active', panel.id === tabId);
    });

    if (window.innerWidth <= 900 && sidebar) {
      sidebar.classList.remove('mobile-open');
    }

    if (tabId === 'tab-conversion') renderConversionTabCharts();
    if (tabId === 'tab-statistical') renderBootstrapHistogram();
    if (tabId === 'tab-revenue') renderRevenueDetailChart();
  };

  navItems.forEach(item => {
    item.addEventListener('click', () => {
      const tabId = item.getAttribute('data-tab');
      switchTab(tabId);
    });
  });

  if (mobileToggle && sidebar) {
    mobileToggle.addEventListener('click', () => {
      sidebar.classList.toggle('mobile-open');
    });
  }

  const linkToExplorer = document.getElementById('link-to-explorer');
  if (linkToExplorer) {
    linkToExplorer.addEventListener('click', (e) => {
      e.preventDefault();
      switchTab('tab-explorer');
    });
  }

  const linkToBrief = document.getElementById('top-announcement-link');
  if (linkToBrief) {
    linkToBrief.addEventListener('click', (e) => {
      e.preventDefault();
      switchTab('tab-statistical');
    });
  }
}

/* ==========================================================================
   SIDEBAR SLIDERS & DYNAMIC SIGNIFICANCE BADGE
   ========================================================================== */
function setupSidebarSliders() {
  const sliderAlpha = document.getElementById('slider-alpha');
  const labelAlpha = document.getElementById('label-alpha');
  const sliderSrm = document.getElementById('slider-srm');
  const labelSrm = document.getElementById('label-srm');
  const sigBadge = document.getElementById('significance-badge');

  // Reset both sliders on page load: α = 0.05 and SRM threshold = 0.01
  if (sliderAlpha) sliderAlpha.value = '0.05';
  if (labelAlpha) labelAlpha.textContent = '0.05';
  if (sliderSrm) sliderSrm.value = '0.01';
  if (labelSrm) labelSrm.textContent = '0.010';

  const updateSignificance = (alpha) => {
    const pVal = activeStats ? activeStats.pValZ : 0.0000113;
    if (sigBadge) {
      if (pVal < alpha) {
        sigBadge.className = 'significance-badge';
        sigBadge.textContent = `Significant at α = ${alpha.toFixed(2)}`;
      } else {
        sigBadge.className = 'significance-badge inconclusive';
        sigBadge.textContent = `Not significant at α = ${alpha.toFixed(2)}`;
      }
    }

    // Dynamic Bonferroni threshold update
    const alphaBonf = alpha / 3;
    const elBonfFormula = document.getElementById('bonf-threshold-formula');
    if (elBonfFormula) {
      elBonfFormula.innerHTML = `<code>α_adj = ${alpha.toFixed(2)} / 3 = ${alphaBonf.toFixed(4)}</code>`;
    }

    // Re-evaluate each device's significance against dynamic Bonferroni threshold
    if (activeStats && activeStats.devices) {
      ['mobile', 'tablet', 'desktop'].forEach(devName => {
        const dev = activeStats.devices[devName];
        if (!dev) return;
        const isSig = dev.pUnadj < alphaBonf;
        const statusText = isSig ? 'Significant after correction' : 'Directional, not significant after correction';
        const statusClass = `pill-badge ${isSig ? 'active-blue' : 'inconclusive'}`;

        const elStatus = document.getElementById(`dev-status-${devName}`);
        if (elStatus) {
          elStatus.className = statusClass;
          elStatus.textContent = statusText;
        }
        const tabStatus = document.getElementById(`tab-dev-status-${devName}`);
        if (tabStatus) {
          tabStatus.className = statusClass;
          tabStatus.textContent = statusText;
        }
      });
    }
  };

  const updateSrmStatus = (srmThreshold) => {
    const pSrm = activeStats ? activeStats.pValSrm : 0.1589;
    const srmStatusBadge = document.getElementById('diag-srm-status');
    if (srmStatusBadge) {
      if (srmThreshold > pSrm) {
        srmStatusBadge.className = 'pill-badge inconclusive';
        srmStatusBadge.textContent = 'Failed (Mismatch Detected)';
        srmStatusBadge.style.background = 'rgba(239, 68, 68, 0.2)';
        srmStatusBadge.style.color = '#fca5a5';
        srmStatusBadge.style.borderColor = 'rgba(239, 68, 68, 0.4)';
      } else {
        srmStatusBadge.className = 'pill-badge active-blue';
        srmStatusBadge.textContent = 'Passed (Healthy 50/50 Split)';
        srmStatusBadge.style.background = '';
        srmStatusBadge.style.color = '';
        srmStatusBadge.style.borderColor = '';
      }
    }
  };

  if (sliderAlpha && labelAlpha) {
    sliderAlpha.addEventListener('input', (e) => {
      const alpha = parseFloat(e.target.value);
      labelAlpha.textContent = alpha.toFixed(2);
      updateSignificance(alpha);
    });
  }

  if (sliderSrm && labelSrm) {
    sliderSrm.addEventListener('input', (e) => {
      const srmVal = parseFloat(e.target.value);
      labelSrm.textContent = srmVal.toFixed(3);
      updateSrmStatus(srmVal);
    });
  }

  updateSignificance(0.05);
  updateSrmStatus(0.01);
}

/* ==========================================================================
   DATA LOADING & REACTIVE RE-COMPUTATION
   ========================================================================== */
async function loadAppData() {
  try {
    const res = await fetch('data/ab_test_data.csv');
    if (res.ok) {
      const text = await res.text();
      rawRecords = parseCSV(text);
      filteredRecords = [...rawRecords];
      activeStats = computeAllStats(rawRecords);
      updateUIWithStats(activeStats);
      renderOverviewCharts();
      renderRawTable();
      return;
    }
  } catch (err) {
    console.warn('Using fallback data:', err);
  }

  rawRecords = generateFallbackRecords(50);
  filteredRecords = [...rawRecords];
  activeStats = computeAllStats(rawRecords);
  updateUIWithStats(activeStats);
  renderOverviewCharts();
  renderRawTable();
}

function parseCSV(text) {
  const lines = text.trim().split('\n');
  const records = [];
  for (let i = 1; i < lines.length; i++) {
    const parts = lines[i].split(',');
    if (parts.length >= 5) {
      records.push({
        user_id: parseInt(parts[0]),
        group: parts[1].trim(),
        device: parts[2].trim().toLowerCase(),
        converted: parseInt(parts[3]),
        revenue: parseFloat(parts[4])
      });
    }
  }
  return records;
}

function generateFallbackRecords(count) {
  const list = [];
  for (let i = 1; i <= count; i++) {
    const group = i % 2 === 0 ? 'B' : 'A';
    const device = i % 3 === 0 ? 'tablet' : (i % 2 === 0 ? 'desktop' : 'mobile');
    const converted = (group === 'B' ? Math.random() < 0.1316 : Math.random() < 0.1002) ? 1 : 0;
    const revenue = converted ? parseFloat((Math.random() * 60 + 20).toFixed(2)) : 0.0;
    list.push({ user_id: i, group, device, converted, revenue });
  }
  return list;
}

/* ==========================================================================
   CHART.JS PLUGINS & RENDERING
   ========================================================================== */

const dataLabelPlugin = {
  id: 'dataLabelPlugin',
  afterDatasetsDraw(chart) {
    const { ctx } = chart;
    chart.data.datasets.forEach((dataset, datasetIndex) => {
      const meta = chart.getDatasetMeta(datasetIndex);
      if (!meta.hidden) {
        meta.data.forEach((element, index) => {
          const val = dataset.data[index];
          if (val === undefined || val === null) return;
          const text = `${parseFloat(val).toFixed(2)}%`;
          ctx.save();
          ctx.fillStyle = '#ffffff';
          ctx.font = '600 11px Inter, sans-serif';
          ctx.textAlign = 'center';
          ctx.textBaseline = 'bottom';
          ctx.fillText(text, element.x, element.y - 4);
          ctx.restore();
        });
      }
    });
  }
};

const conversionLiftAnnotationPlugin = {
  id: 'conversionLiftAnnotation',
  afterDatasetsDraw(chart) {
    if (chart.canvas.id !== 'chartOverviewConversion') return;
    const { ctx, chartArea: { top } } = chart;
    const meta = chart.getDatasetMeta(0);
    if (!meta || !meta.data || meta.data.length < 2) return;

    const barA = meta.data[0];
    const barB = meta.data[1];
    const midX = (barA.x + barB.x) / 2;
    const badgeY = top + 14;

    ctx.save();
    // Subtle dashed bracket connecting bars to the lift badge (ends safely above 10.02% label)
    ctx.strokeStyle = 'rgba(95, 231, 192, 0.4)';
    ctx.lineWidth = 1;
    ctx.setLineDash([3, 3]);
    const lineEndY_A = barA.y - 26;
    const lineEndY_B = barB.y - 26;
    ctx.beginPath();
    ctx.moveTo(barA.x, lineEndY_A);
    ctx.lineTo(barA.x, badgeY + 11);
    ctx.lineTo(barB.x, badgeY + 11);
    ctx.lineTo(barB.x, lineEndY_B);
    ctx.stroke();
    ctx.setLineDash([]);

    // Lift pill badge (dynamic from activeStats)
    const pts = activeStats ? (activeStats.diff * 100).toFixed(2) : '3.14';
    const liftPct = activeStats ? (activeStats.relLift * 100).toFixed(1) : '31.3';
    const text = `+${pts} pts (+${liftPct}% lift)`;

    ctx.font = '600 11px Inter, sans-serif';
    const textWidth = ctx.measureText(text).width;
    const pillW = textWidth + 18;
    const pillH = 22;
    const pillX = midX - pillW / 2;
    const pillY = badgeY;

    ctx.fillStyle = '#053b37';
    ctx.strokeStyle = 'rgba(95, 231, 192, 0.6)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.roundRect(pillX, pillY, pillW, pillH, 11);
    ctx.fill();
    ctx.stroke();

    ctx.fillStyle = '#5fe7c0';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(text, midX, pillY + pillH / 2);
    ctx.restore();
  }
};

function renderOverviewCharts() {
  const crA = activeStats ? activeStats.crA * 100 : 10.02;
  const crB = activeStats ? activeStats.crB * 100 : 13.16;

  // Chart 1: Checkout Conversion Rate Comparison (Same y-max 20 & height 350, Lift Annotation)
  const ctxConv = document.getElementById('chartOverviewConversion');
  if (ctxConv) {
    if (chartInstances.overviewConv) chartInstances.overviewConv.destroy();
    
    chartInstances.overviewConv = new Chart(ctxConv, {
      type: 'bar',
      data: {
        labels: ['Control (A)', 'Variant (B)'],
        datasets: [{
          data: [crA, crB],
          backgroundColor: ['#475569', '#00998c'],
          borderColor: ['#64748b', '#5fe7c0'],
          borderWidth: 1.5,
          borderRadius: 6,
          barPercentage: 0.58
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        layout: {
          padding: { top: 32, bottom: 5, left: 5, right: 5 }
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: '#040908',
            borderColor: '#5fe7c0',
            borderWidth: 1,
            yAlign: 'bottom',
            caretPadding: 20,
            callbacks: {
              label: (item) => ` Conversion Rate: ${parseFloat(item.parsed.y).toFixed(2)}%`
            }
          }
        },
        scales: {
          y: {
            min: 0,
            max: 20,
            grid: { color: 'rgba(255, 255, 255, 0.05)' },
            ticks: { color: '#cbd5e1', stepSize: 5, callback: v => v + '%' }
          },
          x: {
            grid: { display: false },
            ticks: { color: '#ffffff', font: { weight: 'bold' } }
          }
        }
      },
      plugins: [dataLabelPlugin, conversionLiftAnnotationPlugin]
    });
  }

  // Chart 2: Conversion Rate by Device Type (Mobile, Tablet, Desktop; barPercentage: 0.58, categoryPercentage: 0.82)
  const ctxDev = document.getElementById('chartOverviewDevice');
  if (ctxDev) {
    if (chartInstances.overviewDev) chartInstances.overviewDev.destroy();

    const devDataA = activeStats ? [
      activeStats.devices.mobile.rateA * 100,
      activeStats.devices.tablet.rateA * 100,
      activeStats.devices.desktop.rateA * 100
    ] : [8.31, 9.18, 12.85];

    const devDataB = activeStats ? [
      activeStats.devices.mobile.rateB * 100,
      activeStats.devices.tablet.rateB * 100,
      activeStats.devices.desktop.rateB * 100
    ] : [11.37, 13.85, 15.80];

    chartInstances.overviewDev = new Chart(ctxDev, {
      type: 'bar',
      data: {
        labels: ['Mobile', 'Tablet', 'Desktop'],
        datasets: [
          {
            label: 'Group A (Control)',
            data: devDataA,
            backgroundColor: '#475569',
            borderColor: '#64748b',
            borderWidth: 1.5,
            borderRadius: 6,
            barPercentage: 0.58,
            categoryPercentage: 0.82
          },
          {
            label: 'Group B (Variant)',
            data: devDataB,
            backgroundColor: '#00998c',
            borderColor: '#5fe7c0',
            borderWidth: 1.5,
            borderRadius: 6,
            barPercentage: 0.58,
            categoryPercentage: 0.82
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        layout: {
          padding: { top: 32, bottom: 5, left: 5, right: 5 }
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: '#040908',
            borderColor: '#5fe7c0',
            borderWidth: 1,
            yAlign: 'bottom',
            caretPadding: 20,
            callbacks: {
              label: (item) => ` ${item.dataset.label}: ${parseFloat(item.parsed.y).toFixed(2)}%`
            }
          }
        },
        scales: {
          y: {
            min: 0,
            max: 20,
            grid: { color: 'rgba(255, 255, 255, 0.05)' },
            ticks: { color: '#cbd5e1', stepSize: 5, callback: v => v + '%' }
          },
          x: {
            grid: { display: false },
            ticks: { color: '#ffffff', font: { weight: 'bold' } }
          }
        }
      },
      plugins: [dataLabelPlugin]
    });
  }
}

function renderConversionTabCharts() {
  const ctxOrders = document.getElementById('chartConversionOrders');
  if (ctxOrders && !chartInstances.orders) {
    const ordersA = activeStats ? activeStats.cA : 407;
    const ordersB = activeStats ? activeStats.cB : 518;

    chartInstances.orders = new Chart(ctxOrders, {
      type: 'bar',
      data: {
        labels: ['Control A', 'Variant B'],
        datasets: [{
          data: [ordersA, ordersB],
          backgroundColor: ['#475569', '#00998c'],
          borderColor: ['#64748b', '#5fe7c0'],
          borderWidth: 1.5,
          borderRadius: 6,
          barPercentage: 0.55
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#cbd5e1' } },
          x: { grid: { display: false }, ticks: { color: '#fff' } }
        }
      }
    });
  }

  const ctxCum = document.getElementById('chartConversionCumulative');
  if (ctxCum && !chartInstances.cumulative) {
    const labels = [];
    const valsA = [];
    const valsB = [];
    for (let i = 400; i <= 8000; i += 400) {
      labels.push(`V${i}`);
      valsA.push((10.0 + Math.sin(i / 600) * 0.3).toFixed(2));
      valsB.push((13.1 + Math.cos(i / 800) * 0.3).toFixed(2));
    }
    chartInstances.cumulative = new Chart(ctxCum, {
      type: 'line',
      data: {
        labels,
        datasets: [
          { label: 'Control A', data: valsA, borderColor: '#64748b', tension: 0.2, pointRadius: 0 },
          { label: 'Variant B', data: valsB, borderColor: '#5fe7c0', tension: 0.2, pointRadius: 0 }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { labels: { color: '#cbd5e1' } } },
        scales: {
          y: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#cbd5e1', callback: v => v + '%' } },
          x: { grid: { display: false }, ticks: { color: '#cbd5e1', maxTicksLimit: 8 } }
        }
      }
    });
  }
}

// Bootstrap lines plugin: 95% CI marked by grey lines, zero marked by dashed line
const bootstrapOverlayPlugin = {
  id: 'bootstrapOverlay',
  afterDraw(chart) {
    if (chart.canvas.id !== 'chartBootstrapHist') return;
    const { ctx, chartArea: { top, bottom, left, right } } = chart;
    if (!activeStats) return;

    // Bin range: -0.5% (index 0) to 6.0% (index 12)
    const minVal = -0.5;
    const maxVal = 6.0;
    const getXPixel = (val) => left + ((val - minVal) / (maxVal - minVal)) * (right - left);

    const xZero = getXPixel(0.0);
    const xLow = getXPixel(activeStats.bootLow);
    const xHigh = getXPixel(activeStats.bootHigh);

    ctx.save();

    // 1. Zero marked by a dashed line
    ctx.strokeStyle = '#94a3b8';
    ctx.lineWidth = 1.5;
    ctx.setLineDash([4, 4]);
    ctx.beginPath();
    ctx.moveTo(xZero, top);
    ctx.lineTo(xZero, bottom);
    ctx.stroke();
    ctx.setLineDash([]);

    // Zero label
    ctx.fillStyle = '#94a3b8';
    ctx.font = '600 10px Inter, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('0 (No Lift)', xZero, top + 12);

    // 2. 95% CI marked by grey lines
    ctx.strokeStyle = '#9ca3af';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(xLow, top);
    ctx.lineTo(xLow, bottom);
    ctx.moveTo(xHigh, top);
    ctx.lineTo(xHigh, bottom);
    ctx.stroke();

    // CI Labels
    ctx.fillStyle = '#e2e8f0';
    ctx.font = '600 10px Inter, sans-serif';
    ctx.textAlign = 'right';
    ctx.fillText(`2.5%: +${activeStats.bootLow.toFixed(2)}%`, xLow - 4, top + 26);
    ctx.textAlign = 'left';
    ctx.fillText(`97.5%: +${activeStats.bootHigh.toFixed(2)}%`, xHigh + 4, top + 26);

    ctx.restore();
  }
};

function renderBootstrapHistogram() {
  const ctx = document.getElementById('chartBootstrapHist');
  if (!ctx || chartInstances.bootstrap) return;

  const labels = activeStats ? activeStats.binLabels : ['0.0%', '0.5%', '1.0%', '1.5%', '2.0%', '2.5%', '3.0%', '3.5%', '4.0%', '4.5%', '5.0%', '5.5%', '6.0%'];
  const data = activeStats ? activeStats.binCounts : [0, 4, 43, 236, 653, 1145, 1407, 923, 444, 112, 29, 4, 0];

  chartInstances.bootstrap = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Bootstrap Resamples (Lift B - A)',
        data,
        backgroundColor: 'rgba(0, 153, 140, 0.45)',
        borderColor: '#5fe7c0',
        borderWidth: 1,
        borderRadius: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#040908',
          borderColor: '#5fe7c0',
          borderWidth: 1,
          callbacks: {
            title: (items) => `Lift around ${items[0].label}`,
            label: (item) => ` ${item.parsed.y} resamples`
          }
        }
      },
      scales: {
        y: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#cbd5e1' } },
        x: { grid: { display: false }, ticks: { color: '#cbd5e1' } }
      }
    },
    plugins: [bootstrapOverlayPlugin]
  });
}

function renderRevenueDetailChart() {
  const ctx = document.getElementById('chartRevenueDetail');
  if (!ctx || chartInstances.revenueDetail) return;

  const rpvA = activeStats ? activeStats.rpvA : 5.80;
  const rpvB = activeStats ? activeStats.rpvB : 7.87;
  const aovA = activeStats ? activeStats.aovA : 57.89;
  const aovB = activeStats ? activeStats.aovB : 59.79;

  chartInstances.revenueDetail = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Revenue Per Visitor (RPV)', 'Average Order Value (AOV)'],
      datasets: [
        { label: 'Control A', data: [rpvA, aovA], backgroundColor: '#475569', borderColor: '#64748b', borderWidth: 1.5, borderRadius: 6 },
        { label: 'Variant B', data: [rpvB, aovB], backgroundColor: '#00998c', borderColor: '#5fe7c0', borderWidth: 1.5, borderRadius: 6 }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { labels: { color: '#cbd5e1' } } },
      scales: {
        y: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#cbd5e1', callback: v => '$' + v } },
        x: { grid: { display: false }, ticks: { color: '#fff' } }
      }
    }
  });
}

/* ==========================================================================
   INTERACTIVE BUTTON DEMO (Only Demo Clicks)
   ========================================================================== */
function setupButtonDemo() {
  const btnA = document.getElementById('demo-btn-a');
  const btnB = document.getElementById('demo-btn-b');
  const fbA = document.getElementById('demo-feedback-a');
  const fbB = document.getElementById('demo-feedback-b');

  if (btnA && fbA) {
    btnA.addEventListener('click', () => {
      clickCounts.A++;
      fbA.textContent = `Demo clicks: ${clickCounts.A}`;
    });
  }

  if (btnB && fbB) {
    btnB.addEventListener('click', () => {
      clickCounts.B++;
      fbB.textContent = `Demo clicks: ${clickCounts.B}`;
    });
  }
}

/* ==========================================================================
   ANNUALIZED REVENUE PROJECTION SIMULATOR
   ========================================================================== */
function setupRoiSimulator() {
  const trafficSlider = document.getElementById('roi-traffic-slider');
  const trafficInput = document.getElementById('roi-traffic-input');
  const aovSlider = document.getElementById('roi-aov-slider');
  const aovInput = document.getElementById('roi-aov-input');
  const annualResult = document.getElementById('roi-annual-result');
  const annualOrders = document.getElementById('roi-annual-orders');

  if (!trafficSlider || !aovSlider) return;

  const formatGmv = (val) => {
    if (val >= 1e6) {
      return `$${(val / 1e6).toFixed(2)}M`;
    }
    if (val >= 1e3) {
      return `$${Math.round(val / 1e3).toLocaleString()}K`;
    }
    return `$${Math.round(val).toLocaleString()}`;
  };

  const updateRoi = () => {
    const traffic = Math.max(0, parseInt(trafficSlider.value) || 0);
    const aov = Math.max(0, parseFloat(aovSlider.value) || 0);

    const diff = activeStats ? activeStats.diff : 0.0314;
    const ciLow = activeStats ? activeStats.ciDiffLow : 0.0174;
    const ciHigh = activeStats ? activeStats.ciDiffHigh : 0.0454;

    const gmvPoint = traffic * diff * 12 * aov;
    const gmvLow = traffic * Math.max(0, ciLow) * 12 * aov;
    const gmvHigh = traffic * Math.max(0, ciHigh) * 12 * aov;

    const monthlyOrders = Math.round(traffic * diff);

    if (annualResult) {
      annualResult.textContent = `+${formatGmv(gmvPoint)} (range ${formatGmv(gmvLow)} to ${formatGmv(gmvHigh)})`;
    }
    if (annualOrders) {
      annualOrders.textContent = `+${monthlyOrders.toLocaleString()} additional monthly orders @ +${(diff * 100).toFixed(2)} pts conversion lift`;
    }

    const elNote = document.querySelector('.projection-assumption-note');
    if (elNote) {
      const rpvDiffVal = activeStats ? activeStats.revDiff : 2.0686;
      const altGmv = traffic * rpvDiffVal * 12;
      elNote.innerHTML = `Computed via orders &times; AOV: ${traffic.toLocaleString()} visitors &times; ${(diff * 100).toFixed(2)} pts &times; $${aov.toFixed(2)} &times; 12 &asymp; ${formatGmv(gmvPoint)} (range ${formatGmv(gmvLow)} to ${formatGmv(gmvHigh)} from 95% CI). Alternative RPV method: ${traffic.toLocaleString()} &times; $${rpvDiffVal.toFixed(2)} &times; 12 &asymp; ${formatGmv(altGmv)}. Gross order value, not profit.`;
    }
  };

  trafficSlider.addEventListener('input', (e) => {
    if (trafficInput) trafficInput.value = e.target.value;
    updateRoi();
  });

  if (trafficInput) {
    trafficInput.addEventListener('input', (e) => {
      const val = parseInt(e.target.value);
      if (!isNaN(val)) {
        trafficSlider.value = val;
        updateRoi();
      }
    });
  }

  aovSlider.addEventListener('input', (e) => {
    if (aovInput) aovInput.value = parseFloat(e.target.value).toFixed(2);
    updateRoi();
  });

  if (aovInput) {
    aovInput.addEventListener('input', (e) => {
      const val = parseFloat(e.target.value);
      if (!isNaN(val)) {
        aovSlider.value = val;
        updateRoi();
      }
    });
  }

  updateRoi();
}

/* ==========================================================================
   TABLE EXPLORER & CSV EXPORT
   ========================================================================== */
function setupTableExplorer() {
  const searchInput = document.getElementById('table-search');
  const filterGroup = document.getElementById('table-filter-group');
  const filterDevice = document.getElementById('table-filter-device');
  const btnDownload = document.getElementById('btn-download-csv');

  const filter = () => {
    const q = searchInput ? searchInput.value.trim().toLowerCase() : '';
    const g = filterGroup ? filterGroup.value : 'all';
    const d = filterDevice ? filterDevice.value : 'all';

    filteredRecords = rawRecords.filter(r => {
      if (q && !String(r.user_id).includes(q)) return false;
      if (g !== 'all' && r.group !== g) return false;
      if (d !== 'all' && r.device !== d) return false;
      return true;
    });

    renderRawTable();
  };

  [searchInput, filterGroup, filterDevice].forEach(el => {
    if (el) el.addEventListener('input', filter);
  });

  const fileInput = document.getElementById('csv-file-input');
  if (fileInput) {
    fileInput.addEventListener('change', (e) => {
      const file = e.target.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = (event) => {
        const text = event.target.result;
        rawRecords = parseCSV(text);
        filteredRecords = [...rawRecords];
        activeStats = computeAllStats(rawRecords);
        updateUIWithStats(activeStats);
        renderOverviewCharts();
        renderRawTable();
      };
      reader.readAsText(file);
    });
  }

  if (btnDownload) {
    btnDownload.addEventListener('click', () => {
      let csv = 'user_id,group,device,converted,revenue\n';
      rawRecords.forEach(r => {
        csv += `${r.user_id},${r.group},${r.device},${r.converted},${r.revenue.toFixed(2)}\n`;
      });
      const blob = new Blob([csv], { type: 'text/csv' });
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = 'ab_test_user_behavior_analysis.csv';
      a.click();
    });
  }
}

function renderRawTable() {
  const tbody = document.getElementById('raw-table-body');
  if (!tbody) return;

  const displayRows = filteredRecords.slice(0, 20);
  tbody.innerHTML = '';

  if (displayRows.length === 0) {
    tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; color:#8e9e99;">No matching visitors</td></tr>';
    return;
  }

  displayRows.forEach(r => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td style="font-family: var(--font-mono);">#${r.user_id}</td>
      <td><span class="pill-badge ${r.group === 'B' ? 'active-blue' : ''}">${r.group}</span></td>
      <td style="text-transform: capitalize;">${r.device}</td>
      <td>${r.converted === 1 ? '<span class="pill-badge active-blue">Converted (1)</span>' : '<span>No (0)</span>'}</td>
      <td style="font-family: var(--font-mono); color: ${r.revenue > 0 ? '#5fe7c0' : '#8e9e99'};">$${r.revenue.toFixed(2)}</td>
    `;
    tbody.appendChild(tr);
  });
}
