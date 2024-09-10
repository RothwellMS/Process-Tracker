import pandas as pd

def merge_table(csv1,csv2):
    df1=pd.read_csv(csv1)
    df2=pd.read_csv(csv2)
    result = pd.merge(df1, df2, on="Cage No.", how="left")
    result.to_csv('Storage.csv', index=False)