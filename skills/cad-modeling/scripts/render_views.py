# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = ["build123d>=0.8", "matplotlib"]
# ///
"""STEP/STL を読み、ヘッドレスで多視点PNG(iso/front/top/side)を出す検証用レンダラ。

usage: uv run render_views.py <model.step|model.stl> <out.png> [--tol 0.2]
GL/GPU 不要(matplotlib Agg)。用途はQCプレビュー(寸法感・穴位置・向きの確認)であって
美麗レンダではない。大面が三角形ファンで暗く見えるのは深度ソートの既知アーティファクト。
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


def load_tris(path: Path, tol: float) -> np.ndarray:
    if path.suffix.lower() in (".step", ".stp"):
        from build123d import import_step
        part = import_step(str(path))
        verts, faces = part.tessellate(tolerance=tol)
        V = np.array([(v.X, v.Y, v.Z) for v in verts])
        return V[np.array(faces)]
    if path.suffix.lower() == ".stl":
        from build123d import Mesher
        shapes = Mesher().read(str(path))
        verts, faces = shapes[0].tessellate(tolerance=tol)
        V = np.array([(v.X, v.Y, v.Z) for v in verts])
        return V[np.array(faces)]
    raise SystemExit(f"unsupported: {path.suffix}")


def render(tris: np.ndarray, out: Path) -> None:
    # 面法線で簡易シェーディング(ライト方向固定)して立体感を出す
    n = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    n = n / (np.linalg.norm(n, axis=1, keepdims=True) + 1e-12)
    light = np.array([0.4, -0.5, 0.77])
    shade = 0.45 + 0.55 * np.clip(n @ light, 0, 1)
    colors = np.outer(shade, np.array([0.56, 0.71, 0.85]))

    V = tris.reshape(-1, 3)
    lo, hi = V.min(0), V.max(0)
    c, r = (lo + hi) / 2, float((hi - lo).max()) / 2 or 1.0
    fig = plt.figure(figsize=(10, 8), dpi=110)
    for i, (name, elev, azim) in enumerate(
            [("iso", 30, -60), ("front(-Y)", 0, -90), ("top(+Z)", 90, -90), ("side(+X)", 0, 0)], 1):
        ax = fig.add_subplot(2, 2, i, projection="3d")
        ax.add_collection3d(Poly3DCollection(tris, facecolors=colors, linewidth=0))
        ax.set_xlim(c[0] - r, c[0] + r); ax.set_ylim(c[1] - r, c[1] + r); ax.set_zlim(c[2] - r, c[2] + r)
        ax.view_init(elev=elev, azim=azim); ax.set_title(name, fontsize=9); ax.set_axis_off()
    size = hi - lo
    fig.suptitle(f"bbox {size[0]:.1f} x {size[1]:.1f} x {size[2]:.1f} mm", fontsize=10)
    fig.tight_layout()
    fig.savefig(out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("model"); ap.add_argument("out"); ap.add_argument("--tol", type=float, default=0.2)
    a = ap.parse_args()
    render(load_tris(Path(a.model), a.tol), Path(a.out))
    print("saved:", a.out)
