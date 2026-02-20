---
name: python-rules
description: >
  Python コードの記述・実行に関するルールとベストプラクティス。
  uv による環境管理、PEP 723 インラインスクリプト、PEP 8、
  PyTorch CUDA選択、エラーハンドリングをガイド。
  Use when user writes Python code, creates scripts, debugs Python,
  or runs data analysis with pandas/numpy/scikit-learn/PyTorch.
  Trigger phrases: "Pythonで", "スクリプト作成", "コード書いて",
  "uv run", "uv add", "uv", "pandas", "データ処理", "機械学習モデル",
  "pyproject.toml", ".py", "Python エラー", "デバッグ".
---

# Python Development Rules

## Workflow

Python タスクを受けたら、以下のステップで進める:

### Step 1: 環境確認

```bash
uv --version
```

未インストールの場合:
```bash
# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
# Linux/Mac
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Step 2: タスク種別の判定

| タスク | 推奨アプローチ |
|--------|--------------|
| ワンオフスクリプト | PEP 723 インラインメタデータ + `uv run` |
| プロジェクト開発 | `uv init` + `pyproject.toml` + `uv run` |
| 既存プロジェクト | `pyproject.toml` / `requirements.txt` 確認 → `uv run` |

### Step 3: コード実装

PEP 8 に準拠してコードを記述。

### Step 4: 実行・テスト

```bash
# スクリプト実行
uv run script.py

# pytest
uv run pytest tests/ -v
```

---

## Environment Rules

### グローバルインストール禁止（CRITICAL）

**絶対にグローバルにパッケージをインストールしない。**

```bash
# 良い例（uv が自動で隔離環境を使用）
uv run script.py
uv add pandas

# 悪い例（絶対に実行しない）
pip install pandas          # グローバルインストール
sudo pip install pandas     # システムPythonを汚染
```

### PyTorch インストール

PyTorch をインストールする際は、必ず CUDA 対応版を選択:

```bash
# CUDA バージョン確認
nvidia-smi

# プロジェクトに追加（CUDA 12.1 の例）
uv add torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# ワンオフスクリプトの場合
uv run --with torch --with torchvision script.py

# CPU のみの場合
uv add torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

**確認:**
```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA version: {torch.version.cuda}")
```

### 依存関係管理

```bash
# プロジェクト: uv add / uv remove
uv add pandas numpy
uv remove pandas

# ワンオフスクリプト: インラインメタデータを自動追加
uv add --script script.py pandas openpyxl

# ロックファイル生成（再現性確保）
uv lock
```

### Python バージョン管理

```bash
uv python install 3.12          # インストール
uv python pin 3.12              # プロジェクトで固定
uv python list --only-installed  # 一覧
```

---

## ワンオフスクリプト（PEP 723）

依存関係をスクリプト内にインラインで宣言し、venv 作成なしで実行:

```python
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "pandas>=2.0",
#   "openpyxl",
# ]
# ///

import pandas as pd

df = pd.read_excel("data.xlsx")
print(df.describe())
```

```bash
# これだけで実行完了（venv 作成・activate 不要）
uv run script.py
```

### アドホック実行（メタデータなし）

```bash
uv run --with pandas --with matplotlib analysis.py
```

---

## プロジェクト開発

```bash
uv init myproject && cd myproject
uv add pandas numpy
uv add --dev pytest ruff
uv run python -m myproject.main
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
# uv run 使用時は依存宣言に追加すれば自動解決
uv add pandas                          # プロジェクト
uv add --script script.py pandas       # ワンオフスクリプト
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

---

## Project Structure（推奨）

```
project/
├── .venv/                 # uv が自動管理（gitignore対象）
├── src/
│   └── myproject/
│       ├── __init__.py
│       └── main.py
├── tests/
│   └── test_main.py
├── pyproject.toml         # uv init で生成
├── uv.lock                # uv lock で生成
├── .python-version        # uv python pin で生成
└── .gitignore
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
