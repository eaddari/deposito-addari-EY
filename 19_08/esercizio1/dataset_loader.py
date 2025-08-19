import pandas as pd
from glob import glob
from functools import reduce

csv_files = glob("C:\\desktopnoonedrive\\Ai Academy\\deposito-addari-EY\\19_08\\esercizio1\\dataset\\*.csv")

df = pd.read_csv(csv_files[0])

dfs = []
for file in csv_files:
    dfs.append(pd.read_csv(file))

merged_df = reduce(lambda left, right: pd.merge(left, right, on='Datetime', how='outer'), dfs)
merged_df.to_csv("C:\\desktopnoonedrive\\Ai Academy\\deposito-addari-EY\\19_08\\esercizio1\\merged_dataset.csv", index=False)
