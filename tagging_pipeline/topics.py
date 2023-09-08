import pandas as pd


if __name__ == "__main__":
    df = pd.read_csv('topics/2023-09-08 11:36:46.csv')
    print(df['topic_three'].value_counts())
