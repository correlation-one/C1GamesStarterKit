import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# Data for visualization
data = {
    "Aggression Level": [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    "Resource Allocation (SP vs. MP)": ["High SP, Low MP", "High SP, Low MP", "Moderate SP, Low MP", "Moderate SP, Moderate MP", "Balanced SP and MP", "Balanced SP and MP", "Low SP, High MP", "Low SP, High MP", "Low SP, High MP", "Low SP, High MP", "Low SP, High MP"],
    "Avg Turns Survived": [100, 99, 93, 59, 44, 34, 25, 16, 17, 16, 11],
    "Observed Behavior": [
        "Turtling",
        "Defensive",
        "Inefficient",
        "Overextended",
        "Strategic",
        "Optimal",
        "Aggressive",
        "Overcommitted",
        "Chaotic",
        "Fragile",
        "Glass Cannon",
    ],
}

# Convert to DataFrame
df = pd.DataFrame(data)

# Bar chart for Avg Turns Survived
plt.figure(figsize=(10, 6))
plt.bar(df["Aggression Level"], df["Avg Turns Survived"], color="skyblue")
plt.title("Average Turns Survived by Aggression Level", fontsize=14)
plt.xlabel("Aggression Level", fontsize=12)
plt.ylabel("Average Turns Survived", fontsize=12)
plt.xticks(df["Aggression Level"], rotation=45)
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.tight_layout()
plt.savefig("avg_turns_survived.png")
plt.show()

# Heatmap for Resource Allocation and Behavior
heatmap_data = pd.DataFrame({
    "Aggression Level": df["Aggression Level"],
    "SP Bias": [1 if "High SP" in alloc else 0.5 if "Moderate SP" in alloc else 0 for alloc in df["Resource Allocation (SP vs. MP)"]],
    "MP Bias": [1 if "High MP" in alloc else 0.5 if "Moderate MP" in alloc else 0 for alloc in df["Resource Allocation (SP vs. MP)"]],
})

plt.figure(figsize=(8, 6))
sns.heatmap(
    heatmap_data.set_index("Aggression Level"),
    annot=True,
    cmap="coolwarm",
    cbar_kws={"label": "Bias (SP vs. MP)"},
    linewidths=0.5,
)
plt.title("Resource Allocation Bias by Aggression Level", fontsize=14)
plt.tight_layout()
plt.savefig("resource_allocation_heatmap.png")
plt.show()