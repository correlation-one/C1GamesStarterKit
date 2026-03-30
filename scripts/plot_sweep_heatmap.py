
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def main():
    try:
        print("Loading sweep_results.csv...")
        csv_path = os.path.join(os.path.dirname(__file__), "..", "sweep_results.csv")
        df = pd.read_csv(csv_path)
        print("Loaded CSV with shape:", df.shape)

        win_df = df.copy()
        win_df["agent_win"] = (win_df["winner"] == "agent").astype(int)
        agg_win = win_df.groupby("aggression")["agent_win"].mean().reset_index()
        print("Aggression values:", agg_win["aggression"].tolist())
        print("Win rates:", agg_win["agent_win"].tolist())

        plt.figure(figsize=(8, 4))
        sns.heatmap([agg_win["agent_win"]], annot=True, fmt=".2f", cmap="YlGnBu",
                    xticklabels=agg_win["aggression"].round(2), yticklabels=["Win Rate"])
        plt.xlabel("Aggression")
        plt.title("Agent Win Rate vs. Aggression")
        plt.tight_layout()
        out_path = os.path.join(os.path.dirname(__file__), "..", "sweep_heatmap.png")
        plt.savefig(out_path)
        print(f"Saved heatmap to {out_path}")
        plt.close()
    except Exception as e:
        print("Error generating heatmap:", e)

if __name__ == "__main__":
    main()
