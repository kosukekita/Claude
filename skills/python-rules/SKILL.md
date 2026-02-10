---
name: python-rules
description: "Python開発時のガイドライン。仮想環境管理、PEP 8準拠、PyTorch CUDA選択。Use when user writes, debugs, or executes Python code. Trigger phrases: Python, pip, venv, PyTorch, pandas, numpy, scikit-learn, データ分析, スクリプト, ML, 機械学習."
---

# Python Development Rules

## Environment Constraints
- **Package Management**: NEVER install packages globally. ALWAYS use a virtual environment (e.g., `.venv`) for `pip install`.
- **PyTorch**: When installing PyTorch, always ensure the CUDA-enabled version is selected.

## Code Style
- Adhere to PEP 8 for Python code.
- Ensure all new dependencies are reflected in `requirements.txt` or `pyproject.toml`.
