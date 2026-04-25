#!/usr/bin/env python3
"""
plot_results.py — Generate charts from sweep_summary.csv and sweep_results.csv.

Usage:
    python3 plot_results.py

Outputs (saved in graphs/):
    win_rate_vs_aggression.png     — Bar chart of win rate per aggression level
    score_vs_aggression.png        — Grouped bar chart of avg agent vs opponent score
    turns_vs_aggression.png        — Bar chart of avg turns survived
    resource_use_vs_aggression.png — SP vs MP spent per aggression level
    sweep_heatmap.png              — Heatmap of win rate across aggression levels
    behavior_overview.png          — Combined 4-panel summary chart

Reads:
    sweep_summary.csv   (averages per aggression level)
    sweep_results.csv   (raw per-match results)
"""

import os
import sys

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import seaborn as sns

ROOT      = os.path.dirname(os.path.abspath(__file__))
OUT_DIR   = os.path.join(ROOT, "graphs")
SUMMARY   = os.path.join(ROOT, "sweep_summary.csv")
RESULTS   = os.path.join(ROOT, "sweep_results.csv")

# ── Shared style ─────────────────────────────────────────────────────────────
PALETTE     = "coolwarm"
BAR_COLOR   = "#4C9BE8"
WIN_COLOR   = "#2ECC71"
LOSE_COLOR  = "#E74C3C"
SP_COLOR    = "#5DADE2"
MP_COLOR    = "#F39C12"
FONT_TITLE  = 14
FONT_LABEL  = 11


def load_data():
    """Load both CSVs; exit with a helpful message if missing."""
    missing = [p for p in (SUMMARY, RESULTS) if not os.path.isfile(p)]
    if missing:
        print("ERROR: Missing data files:")
        for p in missing:
            print(f"  {p}")
        print("\nRun these first:")
        print("  python3 run_sweep.py --repeats 10")
        print("  python3 analyze_results.py")
        sys.exit(1)

    summary = pd.read_csv(SUMMARY)
    results = pd.read_csv(RESULTS)
    return summary, results


def save(fig, name: str):
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, name)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


# ── Chart 1: Win Rate vs Aggression ──────────────────────────────────────────
def plot_win_rate(summary: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(10, 5))
    colors = [WIN_COLOR if w >= 0.5 else LOSE_COLOR for w in summary["win_rate"]]
    bars = ax.bar(summary["aggression_value"], summary["win_rate"] * 100,
                  color=colors, edgecolor="white", linewidth=0.8, width=0.07)

    # Annotate each bar
    for bar, val in zip(bars, summary["win_rate"]):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 1.5,
                f"{val*100:.0f}%",
                ha="center", va="bottom", fontsize=9)

    ax.set_xlabel("Aggression (c)  —  objective weight toward offense", fontsize=FONT_LABEL)
    ax.set_ylabel("Win Rate (%)", fontsize=FONT_LABEL)
    ax.set_title("Win Rate vs. Aggression Parameter\n"
                 r"$R(s,c) = c \cdot \mathrm{offense}(s) + (1-c) \cdot \mathrm{defense}(s)$",
                 fontsize=FONT_TITLE)
    ax.set_xticks(summary["aggression_value"])
    ax.set_ylim(0, 120)
    ax.axhline(50, color="gray", linestyle="--", linewidth=0.8, alpha=0.6, label="50% baseline")
    ax.legend(fontsize=9)
    ax.spines[["top", "right"]].set_visible(False)

    win_patch  = mpatches.Patch(color=WIN_COLOR,  label="Win rate ≥ 50%")
    lose_patch = mpatches.Patch(color=LOSE_COLOR, label="Win rate < 50%")
    ax.legend(handles=[win_patch, lose_patch], fontsize=9)

    save(fig, "win_rate_vs_aggression.png")


# ── Chart 2: Score vs Aggression (agent vs opponent) ─────────────────────────
def plot_scores(summary: pd.DataFrame):
    x      = np.array(summary["aggression_value"])
    width  = 0.03
    fig, ax = plt.subplots(figsize=(10, 5))

    ax.bar(x - width, summary["avg_agent_score"],    width=width*1.8, label="Agent score",    color="#2980B9", edgecolor="white")
    ax.bar(x + width, summary["avg_opponent_score"], width=width*1.8, label="Opponent score", color="#E74C3C", edgecolor="white")

    ax.set_xlabel("Aggression (c)", fontsize=FONT_LABEL)
    ax.set_ylabel("Average Points Scored", fontsize=FONT_LABEL)
    ax.set_title("Agent vs. Opponent Score by Aggression Level", fontsize=FONT_TITLE)
    ax.set_xticks(x)
    ax.legend(fontsize=10)
    ax.spines[["top", "right"]].set_visible(False)

    save(fig, "score_vs_aggression.png")


# ── Chart 3: Turns Survived vs Aggression ────────────────────────────────────
def plot_turns(summary: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(summary["aggression_value"], summary["avg_turns"],
           color=BAR_COLOR, edgecolor="white", linewidth=0.8, width=0.07)

    ax.set_xlabel("Aggression (c)", fontsize=FONT_LABEL)
    ax.set_ylabel("Average Turns", fontsize=FONT_LABEL)
    ax.set_title("Average Game Length (Turns) vs. Aggression Level\n"
                 "Fewer turns = faster wins or faster losses",
                 fontsize=FONT_TITLE)
    ax.set_xticks(summary["aggression_value"])
    ax.spines[["top", "right"]].set_visible(False)

    save(fig, "turns_vs_aggression.png")


# ── Chart 4: Resource Use (SP vs MP) ─────────────────────────────────────────
def plot_resources(summary: pd.DataFrame):
    x     = np.array(summary["aggression_value"])
    width = 0.03
    fig, ax = plt.subplots(figsize=(10, 5))

    ax.bar(x - width, summary["avg_agent_sp_spent"], width=width*1.8,
           label="SP spent (defense)", color=SP_COLOR, edgecolor="white")
    ax.bar(x + width, summary["avg_agent_mp_spent"], width=width*1.8,
           label="MP spent (offense)", color=MP_COLOR, edgecolor="white")

    ax.set_xlabel("Aggression (c)", fontsize=FONT_LABEL)
    ax.set_ylabel("Average Resources Spent", fontsize=FONT_LABEL)
    ax.set_title("Resource Allocation: SP (Defense) vs. MP (Offense) by Aggression Level",
                 fontsize=FONT_TITLE)
    ax.set_xticks(x)
    ax.legend(fontsize=10)
    ax.spines[["top", "right"]].set_visible(False)

    save(fig, "resource_use_vs_aggression.png")


# ── Chart 5: Heatmap ──────────────────────────────────────────────────────────
def plot_heatmap(summary: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(12, 3))
    data = summary.set_index("aggression_value")[["win_rate", "avg_agent_score",
                                                   "avg_opponent_score", "avg_turns"]].T
    data.index = ["Win Rate", "Avg Agent Score", "Avg Opp Score", "Avg Turns"]

    sns.heatmap(
        data,
        annot=True, fmt=".1f",
        cmap="YlGnBu",
        linewidths=0.5,
        linecolor="white",
        ax=ax,
        cbar_kws={"shrink": 0.8},
    )
    ax.set_xlabel("Aggression (c)", fontsize=FONT_LABEL)
    ax.set_title("Outcome Metrics Heatmap Across Aggression Levels", fontsize=FONT_TITLE)
    ax.tick_params(axis="x", labelsize=8)

    save(fig, "sweep_heatmap.png")


# ── Chart 6: 4-panel behavior overview ───────────────────────────────────────
def plot_overview(summary: pd.DataFrame):
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    fig.suptitle(
        "Behavior Overview: How Aggression Parameter Shapes Agent Outcomes\n"
        r"$R(s,c) = c \cdot \mathrm{offense}(s) + (1-c) \cdot \mathrm{defense}(s)$",
        fontsize=FONT_TITLE + 1,
        y=1.01,
    )

    x = summary["aggression_value"]

    # Panel 1 — Win rate
    colors = [WIN_COLOR if w >= 0.5 else LOSE_COLOR for w in summary["win_rate"]]
    axes[0, 0].bar(x, summary["win_rate"] * 100, color=colors, width=0.07, edgecolor="white")
    axes[0, 0].set_title("Win Rate (%)")
    axes[0, 0].set_xlabel("Aggression (c)")
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_ylim(0, 115)

    # Panel 2 — Scores
    width = 0.03
    axes[0, 1].bar(np.array(x) - width, summary["avg_agent_score"],    width=width*1.8, color="#2980B9", label="Agent")
    axes[0, 1].bar(np.array(x) + width, summary["avg_opponent_score"], width=width*1.8, color="#E74C3C", label="Opponent")
    axes[0, 1].set_title("Avg Score (Agent vs. Opponent)")
    axes[0, 1].set_xlabel("Aggression (c)")
    axes[0, 1].set_xticks(x)
    axes[0, 1].legend(fontsize=8)

    # Panel 3 — Turns
    axes[1, 0].bar(x, summary["avg_turns"], color=BAR_COLOR, width=0.07, edgecolor="white")
    axes[1, 0].set_title("Avg Game Length (Turns)")
    axes[1, 0].set_xlabel("Aggression (c)")
    axes[1, 0].set_xticks(x)

    # Panel 4 — Resources
    axes[1, 1].bar(np.array(x) - width, summary["avg_agent_sp_spent"], width=width*1.8, color=SP_COLOR, label="SP (defense)")
    axes[1, 1].bar(np.array(x) + width, summary["avg_agent_mp_spent"], width=width*1.8, color=MP_COLOR, label="MP (offense)")
    axes[1, 1].set_title("Avg Resource Allocation")
    axes[1, 1].set_xlabel("Aggression (c)")
    axes[1, 1].set_xticks(x)
    axes[1, 1].legend(fontsize=8)

    for ax in axes.flat:
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(axis="x", labelsize=7)

    plt.tight_layout()
    save(fig, "behavior_overview.png")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("Loading CSVs...")
    summary, results = load_data()

    print(f"  {len(summary)} aggression levels, {len(results)} total matches\n")
    print("Generating charts...")

    plot_win_rate(summary)
    plot_scores(summary)
    plot_turns(summary)
    plot_resources(summary)
    plot_heatmap(summary)
    plot_overview(summary)

    print(f"\nAll charts saved to: {OUT_DIR}/")


if __name__ == "__main__":
    main()
