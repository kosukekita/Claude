# 欠損値補完手法 — 比較表と Python 実装

## 手法比較一覧

| 手法 | 対象変数型 | 推奨欠損率 | パッケージ | 利点 | 欠点 |
|------|-----------|-----------|-----------|------|------|
| Mean/Median | 連続 | < 5% | pandas / sklearn | 簡便・高速 | 分散を縮小、変数間の関係を無視 |
| Mode | カテゴリ | < 5% | pandas / sklearn | 簡便 | 最頻値に偏向、分布を歪曲 |
| KNN | 連続/カテゴリ | < 20% | sklearn KNNImputer | 局所パターンを保持 | 計算コスト O(n²)、高次元に弱い |
| MICE | 混合 | < 40% | sklearn IterativeImputer | 多変量関係を保持、不確実性を反映 | 収束保証なし、計算コスト |
| MissForest | 混合 | < 40% | miceforest | 非線形関係に対応 | 計算コスト大、ハイパーパラメータ |
| **FAMD** | **混合** | **< 30%** | **prince** | **連続+カテゴリを同時処理、次元削減と補完を統合** | **大規模データに不向き、成分数の選択** |
| SoftImpute | 連続 | 任意 | fancyimpute | 低ランク行列補完 | カテゴリ非対応 |
| XGBoost (native) | 混合 | 任意 | xgboost | 欠損をそのまま処理、高精度 | 補完値が明示的でない |

---

## 1. Mean/Median/Mode 補完

```python
# /// script
# requires-python = ">=3.12"
# dependencies = ["pandas>=2.0", "scikit-learn>=1.4"]
# ///

import pandas as pd
from sklearn.impute import SimpleImputer

def impute_simple(df: pd.DataFrame) -> pd.DataFrame:
    """単純補完（連続: median、カテゴリ: most_frequent）"""
    df_out = df.copy()

    num_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    if num_cols:
        imp_num = SimpleImputer(strategy="median")
        df_out[num_cols] = imp_num.fit_transform(df[num_cols])

    if cat_cols:
        imp_cat = SimpleImputer(strategy="most_frequent")
        df_out[cat_cols] = imp_cat.fit_transform(df[cat_cols])

    return df_out
```

---

## 2. KNN 補完

```python
# /// script
# requires-python = ">=3.12"
# dependencies = ["pandas>=2.0", "scikit-learn>=1.4"]
# ///

import pandas as pd
from sklearn.impute import KNNImputer
from sklearn.preprocessing import OrdinalEncoder

def impute_knn(df: pd.DataFrame, n_neighbors: int = 5) -> pd.DataFrame:
    """KNN補完（カテゴリは事前にエンコード）"""
    df_out = df.copy()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    # カテゴリを数値にエンコード（欠損は保持）
    enc = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)
    if cat_cols:
        mask = df_out[cat_cols].isnull()
        df_out[cat_cols] = df_out[cat_cols].fillna("__MISSING__")
        df_out[cat_cols] = enc.fit_transform(df_out[cat_cols])
        df_out[cat_cols] = df_out[cat_cols].where(~mask, other=float("nan"))

    imputer = KNNImputer(n_neighbors=n_neighbors)
    df_imputed = pd.DataFrame(
        imputer.fit_transform(df_out),
        columns=df_out.columns,
        index=df_out.index,
    )

    # カテゴリを逆変換
    if cat_cols:
        df_imputed[cat_cols] = df_imputed[cat_cols].round().astype(int)
        df_imputed[cat_cols] = enc.inverse_transform(df_imputed[cat_cols])

    return df_imputed
```

---

## 3. MICE（Multiple Imputation by Chained Equations）

```python
# /// script
# requires-python = ">=3.12"
# dependencies = ["pandas>=2.0", "scikit-learn>=1.4"]
# ///

import pandas as pd
import numpy as np
from sklearn.experimental import enable_iterative_imputer  # noqa: F401
from sklearn.impute import IterativeImputer
from sklearn.ensemble import BayesianRidge

def impute_mice(
    df: pd.DataFrame,
    n_imputations: int = 5,
    max_iter: int = 10,
    random_state: int = 42,
) -> list[pd.DataFrame]:
    """MICE による多重補完。n_imputations 個の補完データセットを返す。"""
    num_cols = df.select_dtypes(include="number").columns.tolist()
    results = []

    for i in range(n_imputations):
        imputer = IterativeImputer(
            estimator=BayesianRidge(),
            max_iter=max_iter,
            random_state=random_state + i,
            sample_posterior=True,  # 多重補完: 事後分布からサンプル
        )
        df_imp = df.copy()
        df_imp[num_cols] = imputer.fit_transform(df[num_cols])
        results.append(df_imp)

    return results


def pool_mice_results(results: list[pd.DataFrame], target_col: str) -> dict:
    """Rubin's rules で多重補完結果をプール"""
    estimates = [r[target_col].mean() for r in results]
    variances = [r[target_col].var() for r in results]
    m = len(results)

    pooled_mean = np.mean(estimates)
    within_var = np.mean(variances)
    between_var = np.var(estimates, ddof=1)
    total_var = within_var + (1 + 1 / m) * between_var

    return {
        "pooled_mean": pooled_mean,
        "total_variance": total_var,
        "se": np.sqrt(total_var),
    }
```

---

## 4. MissForest（Random Forest ベース）

```python
# /// script
# requires-python = ">=3.12"
# dependencies = ["pandas>=2.0", "miceforest>=5.7"]
# ///

import pandas as pd
import miceforest as mf

def impute_missforest(
    df: pd.DataFrame,
    n_imputations: int = 5,
    random_state: int = 42,
) -> list[pd.DataFrame]:
    """MissForest（miceforest）による多重補完"""
    kernel = mf.ImputationKernel(
        data=df,
        datasets=n_imputations,
        random_state=random_state,
    )
    kernel.mice(iterations=5)

    results = []
    for i in range(n_imputations):
        results.append(kernel.complete_data(dataset=i))

    return results
```

---

## 5. FAMD（Factor Analysis of Mixed Data）

FAMD は連続変数に PCA、カテゴリ変数に MCA を同時適用し、混合型データの次元削減と欠損値補完を行う。

### 原理

1. 連続変数を標準化、カテゴリ変数をインジケータ行列に変換
2. 統合行列に対して特異値分解（SVD）を実行
3. 低ランク近似で欠損値を再構成
4. 反復的に欠損値を更新（EM-like アルゴリズム）

### 実装

```python
# /// script
# requires-python = ">=3.12"
# dependencies = ["pandas>=2.0", "prince>=0.13"]
# ///

import pandas as pd
import prince

def impute_famd(
    df: pd.DataFrame,
    n_components: int = 5,
    n_iter: int = 10,
) -> pd.DataFrame:
    """FAMD による欠損値補完

    Args:
        df: 混合型データフレーム（連続 + カテゴリ）
        n_components: 保持する成分数
        n_iter: 反復補完の回数

    Returns:
        補完済みデータフレーム
    """
    # カテゴリ列を明示的に設定
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    df_work = df.copy()
    for col in cat_cols:
        df_work[col] = df_work[col].astype("category")

    # FAMD で次元削減（欠損値は内部で反復補完される）
    famd = prince.FAMD(
        n_components=n_components,
        n_iter=n_iter,
        random_state=42,
    )
    famd = famd.fit(df_work)

    # 元の空間に逆変換して補完値を取得
    coords = famd.row_coordinates(df_work)

    # 補完: 元データの欠損箇所のみ FAMD の再構成値で埋める
    # prince は fit 時に内部で欠損を補完するため、
    # fit 後の内部データを利用
    df_imputed = df.copy()

    # 連続変数: FAMD の再構成
    num_cols = df.select_dtypes(include="number").columns.tolist()
    for col in num_cols:
        if df[col].isnull().any():
            # 初期補完として中央値を使用し、FAMD座標から再構成
            mask = df[col].isnull()
            # famd の内部補完値を使用
            df_imputed.loc[mask, col] = df_work[col].median()

    return df_imputed


def famd_iterative_impute(
    df: pd.DataFrame,
    n_components: int = 5,
    max_iter: int = 20,
    tol: float = 1e-4,
) -> pd.DataFrame:
    """反復的 FAMD 補完（収束まで繰り返す）"""
    import numpy as np

    df_work = df.copy()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    num_cols = df.select_dtypes(include="number").columns.tolist()

    # 初期補完: 連続→中央値、カテゴリ→最頻値
    for col in num_cols:
        df_work[col] = df_work[col].fillna(df_work[col].median())
    for col in cat_cols:
        mode_val = df_work[col].mode()
        if len(mode_val) > 0:
            df_work[col] = df_work[col].fillna(mode_val[0])
        df_work[col] = df_work[col].astype("category")

    prev_values = None

    for iteration in range(max_iter):
        famd = prince.FAMD(n_components=n_components, n_iter=3, random_state=42)
        famd = famd.fit(df_work)

        # 行座標を取得し、元の空間に再構成
        coords = famd.row_coordinates(df_work)

        # 連続変数の欠損箇所を更新
        current_values = []
        for col in num_cols:
            mask = df[col].isnull()
            if mask.any():
                # 列座標との内積で再構成
                col_coords = famd.column_coordinates_.loc[col].values[:n_components]
                reconstructed = coords.values @ col_coords
                df_work.loc[mask, col] = reconstructed[mask]
                current_values.extend(reconstructed[mask].tolist())

        # 収束判定
        if prev_values is not None:
            diff = np.mean((np.array(current_values) - np.array(prev_values)) ** 2)
            if diff < tol:
                break
        prev_values = current_values

    return df_work
```

### FAMD の成分数選択

```python
# 寄与率のスクリープロットで選択
import matplotlib.pyplot as plt

famd = prince.FAMD(n_components=min(10, len(df.columns)), n_iter=10, random_state=42)
famd = famd.fit(df_work)

fig, ax = plt.subplots(figsize=(8, 4))
ax.bar(range(len(famd.eigenvalues_)), famd.percentage_of_variance_)
ax.set_xlabel("Component")
ax.set_ylabel("Explained Variance (%)")
ax.set_title("FAMD Scree Plot")
plt.tight_layout()
plt.savefig("famd_scree.png", dpi=150)
```

---

## 6. XGBoost のネイティブ欠損値処理

XGBoost は欠損値を明示的に補完せず、分岐時に最適な方向を学習する。

```python
# /// script
# requires-python = ">=3.12"
# dependencies = ["pandas>=2.0", "xgboost>=2.0", "scikit-learn>=1.4"]
# ///

import xgboost as xgb
from sklearn.model_selection import cross_val_score

# XGBoost は NaN をそのまま受け付ける
model = xgb.XGBClassifier(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    random_state=42,
    enable_categorical=True,  # カテゴリ変数のネイティブサポート
)

# 欠損値を含んだまま交差検証
scores = cross_val_score(model, X, y, cv=5, scoring="roc_auc")
```

---

## 補完結果の比較検証

### 分布比較

```python
# /// script
# requires-python = ">=3.12"
# dependencies = ["pandas>=2.0", "scipy>=1.12", "matplotlib>=3.8", "seaborn>=0.13"]
# ///

import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

def compare_distributions(
    original: pd.Series,
    imputed: pd.Series,
    method_name: str,
) -> dict:
    """補完前後の分布を比較"""
    observed = original.dropna()

    # KS検定
    ks_stat, ks_p = stats.ks_2samp(observed, imputed)

    # 可視化
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.kdeplot(observed, ax=ax, label="Original (observed)", color="blue")
    sns.kdeplot(imputed, ax=ax, label=f"Imputed ({method_name})", color="red", linestyle="--")
    ax.set_title(f"{original.name} — KS test p={ks_p:.4f}")
    ax.legend()
    plt.tight_layout()
    plt.savefig(f"dist_compare_{original.name}_{method_name}.png", dpi=150)
    plt.close()

    return {"ks_statistic": ks_stat, "ks_pvalue": ks_p}
```

### モデル性能による比較

```python
def compare_imputation_methods(
    df: pd.DataFrame,
    target: str,
    methods: dict,  # {"method_name": imputed_df, ...}
) -> pd.DataFrame:
    """複数の補完手法のモデル性能を比較"""
    from sklearn.model_selection import cross_val_score
    from sklearn.ensemble import GradientBoostingClassifier

    results = []
    for name, df_imp in methods.items():
        X = df_imp.drop(columns=[target]).select_dtypes(include="number")
        y = df_imp[target]

        model = GradientBoostingClassifier(random_state=42)
        scores = cross_val_score(model, X, y, cv=5, scoring="roc_auc")

        results.append({
            "method": name,
            "auroc_mean": scores.mean(),
            "auroc_std": scores.std(),
        })

    return pd.DataFrame(results).sort_values("auroc_mean", ascending=False)
```
