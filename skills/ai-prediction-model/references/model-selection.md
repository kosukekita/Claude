# モデル選択ガイドとハイパーパラメータチューニング

## アルゴリズム選択フロー

### 二値分類

| 条件 | 推奨アルゴリズム | 理由 |
|------|----------------|------|
| 解釈性が最優先 | ロジスティック回帰 (ElasticNet) | 係数 = オッズ比、臨床的解釈が容易 |
| 高カーディナリティ特徴量あり | LightGBM | カテゴリ変数のネイティブサポート |
| 表形式・中〜大規模 | XGBoost / LightGBM | 一般的に最高精度 |
| 小規模（n < 200） | ロジスティック回帰 + L1/L2 | 過学習リスクが低い |
| 不均衡データ | XGBoost (`scale_pos_weight`) | 不均衡対応パラメータあり |
| 欠損値が多い | XGBoost | 欠損値をネイティブ処理 |

### 多クラス分類

| 条件 | 推奨 | 代替 |
|------|------|------|
| 表形式 | LightGBM / XGBoost | RandomForest |
| クラス数 > 10 | LightGBM | ニューラルネット |

### 回帰

| 条件 | 推奨 | 代替 |
|------|------|------|
| 線形関係が主 | ElasticNet | Ridge / Lasso |
| 非線形 | XGBoost / LightGBM | SVR |
| 外れ値あり | LightGBM (Huber loss) | QuantileRegressor |

### 生存時間解析

| 条件 | 推奨 | 代替 |
|------|------|------|
| 比例ハザード仮定が成立 | Cox比例ハザードモデル | Penalized Cox |
| 非線形・交互作用 | Random Survival Forest | DeepSurv |
| 競合リスク | Fine-Gray モデル | CIF ベースの ML |

---

## ハイパーパラメータチューニング（Optuna）

### XGBoost

```python
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "pandas>=2.0",
#   "scikit-learn>=1.4",
#   "xgboost>=2.0",
#   "optuna>=3.5",
# ]
# ///

import optuna
import xgboost as xgb
from sklearn.model_selection import StratifiedKFold, cross_val_score

def objective(trial, X, y):
    params = {
        "n_estimators": trial.suggest_int("n_estimators", 100, 1000, step=100),
        "max_depth": trial.suggest_int("max_depth", 3, 10),
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
        "subsample": trial.suggest_float("subsample", 0.6, 1.0),
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
        "min_child_weight": trial.suggest_int("min_child_weight", 1, 10),
        "reg_alpha": trial.suggest_float("reg_alpha", 1e-8, 10.0, log=True),
        "reg_lambda": trial.suggest_float("reg_lambda", 1e-8, 10.0, log=True),
        "random_state": 42,
        "enable_categorical": True,
    }

    model = xgb.XGBClassifier(**params)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scores = cross_val_score(model, X, y, cv=cv, scoring="roc_auc")

    return scores.mean()


# 使用例
study = optuna.create_study(direction="maximize")
study.optimize(lambda trial: objective(trial, X, y), n_trials=100)

print(f"Best AUROC: {study.best_value:.4f}")
print(f"Best params: {study.best_params}")
```

### LightGBM

```python
import lightgbm as lgb

def objective_lgbm(trial, X, y):
    params = {
        "n_estimators": trial.suggest_int("n_estimators", 100, 1000, step=100),
        "max_depth": trial.suggest_int("max_depth", 3, 12),
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
        "num_leaves": trial.suggest_int("num_leaves", 20, 150),
        "subsample": trial.suggest_float("subsample", 0.6, 1.0),
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
        "min_child_samples": trial.suggest_int("min_child_samples", 5, 100),
        "reg_alpha": trial.suggest_float("reg_alpha", 1e-8, 10.0, log=True),
        "reg_lambda": trial.suggest_float("reg_lambda", 1e-8, 10.0, log=True),
        "random_state": 42,
        "verbose": -1,
    }

    model = lgb.LGBMClassifier(**params)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scores = cross_val_score(model, X, y, cv=cv, scoring="roc_auc")

    return scores.mean()
```

### ロジスティック回帰（ElasticNet）

```python
from sklearn.linear_model import LogisticRegression

def objective_lr(trial, X, y):
    params = {
        "C": trial.suggest_float("C", 1e-4, 100.0, log=True),
        "l1_ratio": trial.suggest_float("l1_ratio", 0.0, 1.0),
        "penalty": "elasticnet",
        "solver": "saga",
        "max_iter": 5000,
        "random_state": 42,
    }

    model = LogisticRegression(**params)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scores = cross_val_score(model, X, y, cv=cv, scoring="roc_auc")

    return scores.mean()
```

---

## 不均衡データの対処

| 手法 | 実装 | 適用場面 |
|------|------|---------|
| `scale_pos_weight` | XGBoost パラメータ | 軽度の不均衡 |
| `class_weight='balanced'` | sklearn モデル | 軽度〜中度 |
| SMOTE | `imblearn.over_sampling.SMOTE` | 中度（CV fold 内で適用） |
| 閾値調整 | Youden's index / F1 最適化 | 任意 |

**注意**: SMOTE は必ず交差検証の fold 内で適用する（Data Leakage 防止）。

```python
from imblearn.pipeline import Pipeline as ImbPipeline
from imblearn.over_sampling import SMOTE

pipe = ImbPipeline([
    ("imputer", KNNImputer()),
    ("scaler", StandardScaler()),
    ("smote", SMOTE(random_state=42)),
    ("model", XGBClassifier(random_state=42)),
])
```

---

## Pipeline の構築例

```python
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import KNNImputer, SimpleImputer

# 列タイプごとの前処理
num_pipeline = Pipeline([
    ("imputer", KNNImputer(n_neighbors=5)),
    ("scaler", StandardScaler()),
])

cat_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
])

preprocessor = ColumnTransformer([
    ("num", num_pipeline, num_cols),
    ("cat", cat_pipeline, cat_cols),
])

full_pipeline = Pipeline([
    ("preprocessor", preprocessor),
    ("model", xgb.XGBClassifier(random_state=42)),
])

# CV で全パイプラインを評価（Data Leakage なし）
scores = cross_val_score(full_pipeline, X, y, cv=5, scoring="roc_auc")
```
