---
name: ai-prediction-model
description: "AI予測モデル開発の全工程をガイド。欠損値補完（FAMD・MICE・MissForest等の比較検証）、特徴量選択、モデル構築、評価（AUROC・Calibration・DCA）、解釈性（SHAP）を体系的に支援。TRIPOD+AI 準拠の報告と連携。Use when user builds prediction models, handles missing data, performs feature engineering, model evaluation, or interpretability analysis. Trigger phrases: 予測モデル, 欠損値, 補完, imputation, FAMD, MICE, MissForest, 特徴量選択, feature selection, モデル構築, AUROC, calibration, SHAP, 機械学習, XGBoost, ランダムフォレスト, ロジスティック回帰, 交差検証, cross-validation, ハイパーパラメータ, AI解析, prediction model, missing data, DCA."
---

# AI Prediction Model Development

> 医学AI研究における予測モデル開発の全工程（前処理→構築→評価→解釈）をガイドするスキル。

## Workflow

予測モデル開発タスクを受けたら、以下の5ステップで進める:

### Step 1: データ品質評価

1. **データ概要の把握**
   ```python
   df.info()
   df.describe(include='all')
   df.dtypes.value_counts()
   ```

2. **欠損値の評価**
   - 欠損率を変数ごとに算出（`df.isnull().mean()`）
   - 欠損パターンを可視化（`missingno.matrix(df)`）
   - 欠損メカニズムを判定 → 下記「欠損メカニズム判定」参照

3. **変数型の分類**

   | 型 | 判定基準 | 例 |
   |----|---------|-----|
   | 連続量 | `float` / ユニーク値が多い `int` | 年齢、BMI、検査値 |
   | カテゴリ（名義） | `object` / `category` / ユニーク値 ≤10 | 性別、診断名 |
   | カテゴリ（順序） | 自然な順序あり | Stage I/II/III、重症度 |
   | 二値 | ユニーク値 = 2 | アウトカム、治療有無 |

### Step 2: 前処理（欠損値補完・特徴量エンジニアリング）

#### 欠損メカニズム判定

| メカニズム | 定義 | 判定方法 | 対応 |
|-----------|------|---------|------|
| **MCAR** | 欠損が完全にランダム | Little's MCAR test (p > 0.05) | 単純削除も許容 |
| **MAR** | 欠損が他の観測変数に依存 | 欠損有無と他変数の関連を検定 | 多重補完推奨 |
| **MNAR** | 欠損が欠損値自体に依存 | ドメイン知識で判断 | 感度分析必須 |

```python
# Little's MCAR test（近似）
from scipy import stats
# 欠損有無の指示変数と他変数のt検定/χ²検定で判断
for col in cols_with_missing:
    indicator = df[col].isnull().astype(int)
    for other_col in numeric_cols:
        if other_col != col:
            stat, p = stats.pointbiserialr(indicator, df[other_col].dropna())
            if p < 0.05:
                print(f"{col} の欠損は {other_col} と関連 → MAR の可能性")
```

#### 欠損値補完手法の選択

**手法選択マトリクス**（変数型 × 欠損率）:

| 欠損率 | 連続変数のみ | カテゴリ変数のみ | 混合型 |
|--------|------------|----------------|-------|
| < 5% | Mean/Median | Mode | Mean/Median + Mode |
| 5-20% | KNN | KNN | **FAMD** / KNN |
| 20-40% | MICE | MICE | **FAMD** / MICE / MissForest |
| > 40% | 変数除外を検討 | 変数除外を検討 | 変数除外を検討 |

**比較検証プロトコル**（推奨）:
1. 少なくとも3手法を適用（例: MICE, FAMD, MissForest）
2. 各手法で補完後の分布を比較（KS検定、ヒストグラム重畳）
3. 下流モデルの性能を比較（交差検証 AUROC 等）
4. 最終的にモデル性能＋分布保持の両面で手法を選択

各手法の実装コードは `references/imputation-methods.md` を参照。

#### 特徴量エンジニアリング

| 処理 | 対象 | 手法 |
|------|------|------|
| スケーリング | 連続量 | StandardScaler（線形モデル）/ RobustScaler（外れ値あり） |
| エンコーディング | 名義カテゴリ | OneHotEncoder（低カーディナリティ）/ TargetEncoder（高） |
| エンコーディング | 順序カテゴリ | OrdinalEncoder |
| 変換 | 歪んだ分布 | log変換 / Box-Cox / Yeo-Johnson |
| 特徴量選択 | 全変数 | Boruta / LASSO / Recursive Feature Elimination |

### Step 3: モデル構築

#### アルゴリズム選択ガイド

| タスク | データ特性 | 第一選択 | 代替 |
|--------|-----------|---------|------|
| 二値分類 | 表形式・中規模 | XGBoost / LightGBM | ロジスティック回帰 |
| 二値分類 | 解釈性重視 | ロジスティック回帰 | ElasticNet |
| 多クラス分類 | 表形式 | XGBoost / LightGBM | RandomForest |
| 回帰 | 表形式 | XGBoost / LightGBM | ElasticNet |
| 生存時間解析 | 打ち切りあり | Cox比例ハザード | RSF / DeepSurv |

#### 交差検証戦略

| データ特性 | 推奨CV | 注意点 |
|-----------|--------|--------|
| 標準 | Stratified K-Fold (k=5 or 10) | クラスバランス保持 |
| 時系列 | TimeSeriesSplit | 未来→過去のリーク防止 |
| グループあり | GroupKFold | 同一患者が訓練・検証に混在しない |
| 小規模 | Repeated Stratified K-Fold | 安定性向上 |
| 多施設 | LeaveOneGroupOut (施設単位) | 外的妥当性の検証 |

#### ハイパーパラメータチューニング

Optuna を推奨。詳細は `references/model-selection.md` を参照。

### Step 4: 評価

#### 判別モデル（分類）

| 指標 | 用途 | 必須/推奨 |
|------|------|----------|
| AUROC | 全体的な判別能 | **必須**（95% CI付） |
| AUPRC | 不均衡データ | 推奨 |
| Sensitivity / Specificity | カットオフ依存 | 推奨 |
| Calibration plot | 予測確率の較正 | **必須** |
| Brier score | 較正の定量評価 | 推奨 |
| Decision Curve Analysis | 臨床的有用性 | **推奨** |
| Net Reclassification Index | 既存モデルとの比較 | 状況依存 |

#### 回帰モデル

| 指標 | 用途 |
|------|------|
| RMSE | 予測誤差の大きさ |
| MAE | 中央値ベースの誤差 |
| R² | 説明率 |
| Calibration plot | 予測値 vs 実測値 |

#### 信頼区間の算出

Bootstrap 法（n=1000）で95%信頼区間を必ず報告。

```python
from sklearn.utils import resample
import numpy as np

scores = []
for _ in range(1000):
    idx = resample(range(len(y_test)), random_state=None)
    score = roc_auc_score(y_test[idx], y_pred[idx])
    scores.append(score)
ci_lower, ci_upper = np.percentile(scores, [2.5, 97.5])
print(f"AUROC: {np.mean(scores):.3f} (95% CI: {ci_lower:.3f}-{ci_upper:.3f})")
```

詳細は `references/evaluation-metrics.md` を参照。

### Step 5: 解釈性・報告

#### SHAP による解釈

```python
import shap
explainer = shap.TreeExplainer(model)
shap_values = explainer(X_test)

# Global: 変数重要度
shap.plots.beeswarm(shap_values)

# Local: 個別症例の説明
shap.plots.waterfall(shap_values[0])
```

#### 報告（TRIPOD+AI 連携）

論文化する場合は `academic-writing` スキルの TRIPOD+AI チェックリストに準拠:
- Methods: 欠損値処理の手法・根拠、モデル選択過程、検証戦略
- Results: 性能指標を 95% CI 付で報告、Calibration plot
- Discussion: 限界（欠損メカニズムの仮定、外的妥当性）

---

## 重要な注意事項

### Data Leakage 防止

**補完・スケーリング・特徴量選択はすべて交差検証の fold 内で実施する。**

```python
from sklearn.pipeline import Pipeline
from sklearn.impute import KNNImputer
from sklearn.preprocessing import StandardScaler

pipe = Pipeline([
    ('imputer', KNNImputer(n_neighbors=5)),
    ('scaler', StandardScaler()),
    ('model', LogisticRegression())
])

# CV 内で全前処理が fold ごとに fit される
from sklearn.model_selection import cross_val_score
scores = cross_val_score(pipe, X, y, cv=5, scoring='roc_auc')
```

### 再現性の確保

- `random_state` を全箇所で固定
- `uv.lock` で依存パッケージのバージョンを固定
- データの前処理パイプライン全体を `Pipeline` で構成

---

## References

- `references/imputation-methods.md` — 全補完手法の比較表と Python 実装コード
- `references/model-selection.md` — アルゴリズム選択ガイドとハイパーパラメータチューニング
- `references/evaluation-metrics.md` — 評価指標の詳細と実装（Calibration, DCA 含む）
- `references/validation-checklist.md` — 欠損値補完・モデル評価の検証チェックリスト
