import pandas as pd


file_path = "faq.csv"


df = pd.read_csv(file_path)
if "source_column" not in df.columns:
    df["source_column"] = ['https://info.tradera.com/' for _ in range(len(df.index))]
print(df)
