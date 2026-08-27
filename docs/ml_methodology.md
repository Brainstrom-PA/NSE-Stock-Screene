# ML methodology (Phase 3 plan)

**Not implemented in Phase 1. No fabricated probabilities anywhere.**

## Problem

Supervised binary classification.

- **Input** — feature vector available at the exact moment a crossover
  event fires (see `docs/quantitative_methodology.md`).
- **Output** — probability that the resulting trade will be profitable
  (BUY/SELL rule from the quant methodology).

## Model hierarchy

1. Baseline — `LogisticRegression` (calibrated).
2. Primary — `HistGradientBoostingClassifier`.
3. Comparison — `RandomForestClassifier`.

## Validation

Time-aware. No random shuffling. Rolling-window / forward-chaining
cross-validation on the crossover events, respecting event chronology.

## Metrics

- ROC-AUC
- Log-loss
- Precision @ top-K (K = number of trades a user would realistically take)
- Calibration plot

## Explanation

- Feature importance (gradient boosting native)
- Per-prediction SHAP (best effort — may be omitted if inference latency
  becomes a concern in the packaged .exe)

## Registry

Models are versioned in the `ml_models` SQLite table with:
`name`, `version`, `artifact_path`, `metrics_json`, `created_at`.
