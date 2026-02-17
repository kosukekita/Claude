---
name: python-rules
description: >
  Python コードの記述・実行に関するルールとベストプラクティス。
  仮想環境管理、PEP 8、PyTorch CUDA選択、エラーハンドリングをガイド。
  Use when user writes Python code, creates scripts, debugs Python,
  or runs data analysis with pandas/numpy/scikit-learn/PyTorch.
  Trigger phrases: "Pythonで", "スクリプト作成", "コード書いて",
  "pip install", "pandas", "データ処理", "機械学習モデル",
  "requirements.txt", "venv", ".py", "Python エラー", "デバッグ".
---

# Python Development Rules

## Workflow

Python タスクを受けたら、以下のステップで進める:

### Step 1: 環境確認

プロジェクトに仮想環境があるか確認:

```bash
# 仮想環境の存在確認
ls -la .venv/ 2>/dev/null || ls -la venv/ 2>/dev/null
```

なければ作成を提案:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows
```

### Step 2: 依存関係確認

```bash
# requirements.txt または pyproject.toml の存在確認
cat requirements.txt 2>/dev/null || cat pyproject.toml 2>/dev/null
```

### Step 3: コード実装

PEP 8 に準拠してコードを記述。

### Step 4: テスト実行

```bash
# pytest がある場合
python -m pytest tests/ -v

# 単体スクリプトの場合
python script.py
```

---

## Environment Rules

### 仮想環境（CRITICAL）

**絶対にグローバルにパッケージをインストールしない。**

```bash
# 良い例
python -m venv .venv
source .venv/bin/activate
pip install pandas

# 悪い例（絶対に実行しない）
pip install pandas  # グローバルインストール
sudo pip install pandas  # システムPythonを汚染
```

### PyTorch インストール

PyTorch をインストールする際は、必ず CUDA 対応版を選択:

```bash
# CUDA バージョン確認
nvidia-smi

# PyTorch インストール（CUDA 12.1 の例）
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# CPU のみの場合
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

**確認:**
```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA version: {torch.version.cuda}")
```

### 依存関係管理

新しいパッケージをインストールしたら、必ず記録:

```bash
# requirements.txt に追加
pip freeze > requirements.txt

# または手動で追加（バージョン固定推奨）
echo "pandas==2.0.3" >> requirements.txt
```

---

## Code Style（PEP 8）

### 基本ルール

- インデント: スペース4つ
- 行の長さ: 最大79文字（docstringは72文字）
- インポート順: 標準ライブラリ → サードパーティ → ローカル
- 関数・変数名: snake_case
- クラス名: PascalCase
- 定数: UPPER_CASE

### インポートの書き方

```python
# 良い例
import os
import sys
from typing import List, Optional

import numpy as np
import pandas as pd

from myproject.utils import helper

# 悪い例
from pandas import *  # ワイルドカードインポート
import pandas, numpy  # 複数インポートを1行に
```

### 型ヒント（推奨）

```python
def process_data(
    data: pd.DataFrame,
    columns: List[str],
    threshold: Optional[float] = None
) -> pd.DataFrame:
    """データを処理する。

    Args:
        data: 入力データフレーム
        columns: 処理対象のカラム名リスト
        threshold: フィルタリング閾値（省略可）

    Returns:
        処理済みデータフレーム
    """
    ...
```

---

## Error Handling

### 基本パターン

```python
# 良い例 - 具体的な例外をキャッチ
try:
    result = process_data(df)
except FileNotFoundError as e:
    logger.error(f"File not found: {e}")
    raise
except ValueError as e:
    logger.warning(f"Invalid value: {e}")
    return default_value

# 悪い例 - 広すぎる例外キャッチ
try:
    result = process_data(df)
except Exception:  # 全例外をキャッチは避ける
    pass  # 無視も避ける
```

### ロギング

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logger.info("Processing started")
logger.warning("Deprecated function used")
logger.error("Failed to process", exc_info=True)
```

---

## Common Issues

### ModuleNotFoundError

```bash
# 仮想環境がアクティブか確認
which python  # .venv/bin/python であるべき

# パッケージがインストールされているか確認
pip list | grep pandas

# 再インストール
pip install pandas
```

### CUDA out of memory

```python
# メモリ解放
import torch
torch.cuda.empty_cache()

# バッチサイズを小さくする
# gradient accumulation を使用する
# mixed precision training を使用する
```

### Permission denied

```bash
# 仮想環境を使用する（sudo は使わない）
python -m venv .venv
source .venv/bin/activate
pip install package_name
```

---

## Project Structure（推奨）

```
project/
├── .venv/                 # 仮想環境（gitignore対象）
├── src/
│   └── myproject/
│       ├── __init__.py
│       └── main.py
├── tests/
│   └── test_main.py
├── requirements.txt       # または pyproject.toml
├── .gitignore
└── README.md
```

### .gitignore 必須項目

```
.venv/
__pycache__/
*.pyc
.env
*.egg-info/
dist/
build/
```
