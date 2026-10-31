"""Histogram of the most recent draws in the lotto CSV.

Reads the CSV from the ``data`` folder into pandas, takes the top ``--rows`` rows (the most
recent draws when the file is sorted newest first) and plots histograms of the columns
``N1`` .. ``N5`` and ``Mega``.

Run it with either::

    python -m lotto.histogram
    lotto-histogram --rows 10 --show
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

WHITE_BALLS = ["N1", "N2", "N3", "N4", "N5"]
MEGA = "Mega"
REQUIRED_COLUMNS = [*WHITE_BALLS, MEGA]

# Project root: src/lotto/histogram.py -> parents[2]
_PROJECT_ROOT = Path(__file__).resolve().parents[2]


def find_csv(path: str | Path | None = None) -> Path:
    """Return the CSV to read.

    ``path`` may be a CSV file or a folder holding exactly one CSV. With no argument the
    ``data`` folder in the current directory (or the project root) is searched.
    """
    if path is not None:
        target = Path(path)
        if not target.exists():
            raise FileNotFoundError(f"{target} does not exist")
        folders = [target] if target.is_dir() else []
        if not folders:
            return target
    else:
        folders = [Path.cwd() / "data", _PROJECT_ROOT / "data"]

    for folder in folders:
        found = sorted(folder.glob("*.csv"))
        if len(found) == 1:
            return found[0]
        if len(found) > 1:
            names = ", ".join(p.name for p in found)
            raise ValueError(f"several CSV files in {folder} ({names}); choose one with --csv")
    searched = ", ".join(str(f) for f in folders)
    raise FileNotFoundError(f"no CSV file found in: {searched}")


def load_draws(csv_path: str | Path) -> pd.DataFrame:
    """Read the CSV and return the numeric ``N1`` .. ``N5`` and ``Mega`` columns.

    Column names are matched ignoring case and surrounding spaces. Rows where any of those
    columns is missing or not a number are dropped.
    """
    df = pd.read_csv(csv_path)
    df.columns = df.columns.astype(str).str.strip()

    by_lower = {name.lower(): name for name in df.columns}
    missing = [c for c in REQUIRED_COLUMNS if c.lower() not in by_lower]
    if missing:
        raise ValueError(
            f"{Path(csv_path).name} is missing column(s) {missing}; found {list(df.columns)}"
        )

    draws = pd.DataFrame({c: df[by_lower[c.lower()]] for c in REQUIRED_COLUMNS})
    draws = draws.apply(pd.to_numeric, errors="coerce").dropna()
    return draws.astype(int).reset_index(drop=True)


def top_rows(draws: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """The first ``n`` rows (all of them when there are fewer)."""
    if n < 1:
        raise ValueError("rows must be at least 1")
    return draws.head(n)


def _bin_edges(values: np.ndarray, width: float = 1.0) -> np.ndarray:
    """Bin edges that centre integer values in their bins."""
    low, high = float(values.min()), float(values.max())
    return np.arange(low - 0.5, high + 0.5 + width, width)


def plot_histograms(rows: pd.DataFrame, *, per_column: bool = False, bin_width: float = 1.0):
    """Draw the histograms and return the matplotlib figure.

    By default two panels are drawn: all of ``N1`` .. ``N5`` pooled together, and ``Mega``
    on its own (it comes from a different number range). With ``per_column`` there is one
    panel for each of the six columns.
    """
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MaxNLocator

    n = len(rows)
    if per_column:
        fig, axes = plt.subplots(2, 3, figsize=(12, 6))
        panels = [(ax, rows[col].to_numpy(), col) for ax, col in zip(axes.flat, REQUIRED_COLUMNS)]
    else:
        fig, axes = plt.subplots(1, 2, figsize=(11, 4), gridspec_kw={"width_ratios": [3, 2]})
        panels = [
            (axes[0], rows[WHITE_BALLS].to_numpy().ravel(), "N1 .. N5 (combined)"),
            (axes[1], rows[MEGA].to_numpy(), "Mega"),
        ]

    for ax, values, title in panels:
        ax.hist(values, bins=_bin_edges(values, bin_width), edgecolor="black", color="#4c78a8")
        ax.set_title(title)
        ax.set_xlabel("number")
        ax.set_ylabel("count")
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))

    fig.suptitle(f"Top {n} rows of the draw history")
    fig.tight_layout()
    return fig


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lotto-histogram",
        description="Histogram of N1..N5 and Mega for the top rows of the lotto CSV.",
    )
    parser.add_argument("--csv", default=None, help="CSV file, or a folder with one CSV (default: data/)")
    parser.add_argument("--rows", type=int, default=10, help="how many top rows to use (default 10)")
    parser.add_argument("--output", default=None, help="image path (default: output/top<rows>_histogram.png)")
    parser.add_argument("--per-column", action="store_true", help="one panel per column")
    parser.add_argument("--bin-width", type=float, default=1.0, help="histogram bin width (default 1)")
    parser.add_argument("--show", action="store_true", help="open a window as well as saving")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if not args.show:
        import matplotlib

        matplotlib.use("Agg", force=True)

    try:
        csv_path = find_csv(args.csv)
        draws = load_draws(csv_path)
        rows = top_rows(draws, args.rows)
    except (FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if rows.empty:
        print(f"error: {csv_path} has no usable rows", file=sys.stderr)
        return 1
    if len(rows) < args.rows:
        print(f"note: only {len(rows)} rows available (asked for {args.rows})", file=sys.stderr)

    print(f"Read {len(draws)} draws from {csv_path}")
    print(f"Using the top {len(rows)} rows:")
    print(rows.to_string(index=False))

    output = Path(args.output) if args.output else Path("output") / f"top{len(rows)}_histogram.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    fig = plot_histograms(rows, per_column=args.per_column, bin_width=args.bin_width)
    fig.savefig(output, dpi=150)
    print(f"Saved plot to {output}")

    if args.show:
        import matplotlib.pyplot as plt

        plt.show()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
