import pandas as pd

class CsvService:

    @staticmethod
    def load(path):
        return pd.read_csv(path)

    @staticmethod
    def save(df, path):
        df.to_csv(path, index=False)
