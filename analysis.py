import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("data/cleaned.csv")

# Define entities (stock/index names you want to track)
entities = ["nifty", "banknifty", "sensex", "gold", "bitcoin", "sbin", "coromandel"]

# Create a summary dictionary
summary = {"Entity": [], "Buy": [], "Sell": [], "Neutral": []}

# Count signals per entity
for entity in entities:
    entity_mask = df["clean_content"].str.contains(entity, case=False, na=False)
    filtered = df[entity_mask]
    
    buy_count = (filtered["signal"] == 1).sum()
    sell_count = (filtered["signal"] == -1).sum()
    neutral_count = (filtered["signal"] == 0).sum()

    summary["Entity"].append(entity.upper())
    summary["Buy"].append(buy_count)
    summary["Sell"].append(sell_count)
    summary["Neutral"].append(neutral_count)

# Convert to DataFrame
summary_df = pd.DataFrame(summary)
summary_df.set_index("Entity", inplace=True)

# Plot
summary_df.plot(kind="bar", stacked=True, figsize=(10,6), colormap="coolwarm")
plt.title("Tweet Sentiment Signals per Stock/Index")
plt.ylabel("Number of Tweets")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()