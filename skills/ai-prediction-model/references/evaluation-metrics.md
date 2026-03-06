# 評価指標の詳細と実装

## 判別モデル（分類）の評価指標

### AUROC（必須）

```python
# /// script
# requires-python = ">=3.12"
# dependencies = ["pandas>=2.0", "scikit-learn>=1.4", "matplotlib>=3.8", "numpy>=1.26"]
# ///

import numpy as np
from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.utils import resample
import matplotlib.pyplot as plt

def auroc_with_ci(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    n_bootstrap: int = 1000,
    ci: float = 0.95,
    random_state: int = 42,
) -> dict:
    """AUROC を Bootstrap 95% CI 付で算出"""
    rng = np.random.RandomState(random_state)
    point_estimate = roc_auc_score(y_true, y_prob)

    scores = []
    for _ in range(n_bootstrap):
        idx = rng.randint(0, len(y_true), len(y_true))
        if len(np.unique(y_true[idx])) < 2:
            continue
        scores.append(roc_auc_score(y_true[idx], y_prob[idx]))

    alpha = (1 - ci) / 2
    ci_lower = np.percentile(scores, alpha * 100)
    ci_upper = np.percentile(scores, (1 - alpha) * 100)

    return {
        "auroc": point_estimate,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "report": f"AUROC {point_estimate:.3f} (95% CI {ci_lower:.3f}-{ci_upper:.3f})",
    }


def plot_roc_curve(y_true, y_prob, label="Model", ax=None):
    """ROC 曲線を描画"""
    fpr, tpr, _ = roc_curve(y_true, y_prob)
    auc = roc_auc_score(y_true, y_prob)

    if ax is None:
        fig, ax = plt.subplots(figsize=(6, 6))
    ax.plot(fpr, tpr, label=f"{label} (AUC={auc:.3f})")
    ax.plot([0, 1], [0, 1], "k--", alpha=0.3)
    ax.set_xlabel("1 - Specificity (FPR)")
    ax.set_ylabel("Sensitivity (TPR)")
    ax.set_title("ROC Curve")
    ax.legend()
    return ax
```

### AUPRC（不均衡データで推奨）

```python
from sklearn.metrics import average_precision_score, precision_recall_curve

def plot_pr_curve(y_true, y_prob, label="Model", ax=None):
    """PR 曲線を描画"""
    precision, recall, _ = precision_recall_curve(y_true, y_prob)
    ap = average_precision_score(y_true, y_prob)

    if ax is None:
        fig, ax = plt.subplots(figsize=(6, 6))
    ax.plot(recall, precision, label=f"{label} (AP={ap:.3f})")
    prevalence = y_true.mean()
    ax.axhline(y=prevalence, color="k", linestyle="--", alpha=0.3, label=f"Prevalence={prevalence:.3f}")
    ax.set_xlabel("Recall")
    ax.set_ylabel("Precision")
    ax.set_title("Precision-Recall Curve")
    ax.legend()
    return ax
```

---

## Calibration（必須）

較正（Calibration）は予測確率が実際の発生率と一致しているかを評価する。

### Calibration Plot

```python
from sklearn.calibration import calibration_curve

def plot_calibration(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    n_bins: int = 10,
    strategy: str = "quantile",
    label: str = "Model",
) -> dict:
    """Calibration plot を描画し、統計量を返す"""
    prob_true, prob_pred = calibration_curve(
        y_true, y_prob, n_bins=n_bins, strategy=strategy
    )

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Calibration plot
    ax = axes[0]
    ax.plot(prob_pred, prob_true, "o-", label=label)
    ax.plot([0, 1], [0, 1], "k--", alpha=0.3, label="Perfectly calibrated")
    ax.set_xlabel("Mean predicted probability")
    ax.set_ylabel("Fraction of positives")
    ax.set_title("Calibration Plot")
    ax.legend()

    # Histogram of predicted probabilities
    ax = axes[1]
    ax.hist(y_prob, bins=50, edgecolor="black", alpha=0.7)
    ax.set_xlabel("Predicted probability")
    ax.set_ylabel("Count")
    ax.set_title("Distribution of Predictions")

    plt.tight_layout()
    plt.savefig("calibration_plot.png", dpi=150)
    plt.close()

    # Brier score
    from sklearn.metrics import brier_score_loss
    brier = brier_score_loss(y_true, y_prob)

    return {
        "brier_score": brier,
        "report": f"Brier score: {brier:.4f}",
    }
```

### Calibration 改善（Platt Scaling / Isotonic Regression）

```python
from sklearn.calibration import CalibratedClassifierCV

# Platt scaling（シグモイド）
calibrated_model = CalibratedClassifierCV(
    estimator=model,
    method="sigmoid",  # or "isotonic"
    cv=5,
)
calibrated_model.fit(X_train, y_train)
y_prob_calibrated = calibrated_model.predict_proba(X_test)[:, 1]
```

---

## Decision Curve Analysis（DCA）（推奨）

臨床的有用性を閾値確率ごとに評価する。

```python
# /// script
# requires-python = ">=3.12"
# dependencies = ["pandas>=2.0", "numpy>=1.26", "matplotlib>=3.8"]
# ///

import numpy as np
import matplotlib.pyplot as plt

def decision_curve_analysis(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    thresholds: np.ndarray | None = None,
    label: str = "Model",
) -> dict:
    """Decision Curve Analysis を実行"""
    if thresholds is None:
        thresholds = np.arange(0.01, 0.99, 0.01)

    n = len(y_true)
    prevalence = y_true.mean()

    net_benefits = []
    for t in thresholds:
        y_pred = (y_prob >= t).astype(int)
        tp = np.sum((y_pred == 1) & (y_true == 1))
        fp = np.sum((y_pred == 1) & (y_true == 0))
        nb = tp / n - fp / n * (t / (1 - t))
        net_benefits.append(nb)

    # Treat all
    treat_all = [prevalence - (1 - prevalence) * (t / (1 - t)) for t in thresholds]

    # Plot
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(thresholds, net_benefits, label=label, color="blue")
    ax.plot(thresholds, treat_all, label="Treat All", color="gray", linestyle="--")
    ax.axhline(y=0, color="black", linestyle="-", alpha=0.3, label="Treat None")
    ax.set_xlabel("Threshold Probability")
    ax.set_ylabel("Net Benefit")
    ax.set_title("Decision Curve Analysis")
    ax.legend()
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.1, max(net_benefits) * 1.2)
    plt.tight_layout()
    plt.savefig("dca_plot.png", dpi=150)
    plt.close()

    return {
        "thresholds": thresholds.tolist(),
        "net_benefits": net_benefits,
    }
```

---

## 回帰モデルの評価指標

```python
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

def evaluate_regression(y_true, y_pred) -> dict:
    """回帰モデルの評価指標を算出"""
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)

    return {
        "RMSE": rmse,
        "MAE": mae,
        "R²": r2,
        "report": f"RMSE: {rmse:.3f}, MAE: {mae:.3f}, R²: {r2:.3f}",
    }


def plot_regression_calibration(y_true, y_pred, label="Model"):
    """回帰モデルの Calibration plot（予測値 vs 実測値）"""
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(y_pred, y_true, alpha=0.3, s=10)

    # 回帰直線
    z = np.polyfit(y_pred, y_true, 1)
    p = np.poly1d(z)
    x_line = np.linspace(min(y_pred), max(y_pred), 100)
    ax.plot(x_line, p(x_line), "r-", label=f"Fit: y={z[0]:.2f}x+{z[1]:.2f}")

    # 完全一致線
    lims = [min(min(y_true), min(y_pred)), max(max(y_true), max(y_pred))]
    ax.plot(lims, lims, "k--", alpha=0.3, label="Perfect calibration")

    ax.set_xlabel("Predicted")
    ax.set_ylabel("Observed")
    ax.set_title(f"Calibration Plot — {label}")
    ax.legend()
    plt.tight_layout()
    plt.savefig("regression_calibration.png", dpi=150)
    plt.close()
```

---

## 評価結果の統合レポート

```python
def generate_evaluation_report(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    task: str = "classification",
) -> str:
    """評価結果を TRIPOD+AI 準拠の形式でテキスト出力"""
    if task == "classification":
        auroc = auroc_with_ci(y_true, y_prob)
        from sklearn.metrics import brier_score_loss
        brier = brier_score_loss(y_true, y_prob)

        report = f"""## Model Performance

The model achieved an {auroc['report']}.
The Brier score was {brier:.4f}, indicating {'good' if brier < 0.1 else 'moderate' if brier < 0.25 else 'poor'} calibration.
"""
        return report
    return ""
```
