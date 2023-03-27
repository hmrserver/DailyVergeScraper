import pandas as pd

class CSV:
    def __init__(self, csv_filename):
        self.csv_filename = csv_filename
        self.existing_data_df = self.read_csv()

    
    def read_csv(self):
        try:
            existing_data_df = pd.read_csv(self.csv_filename)
        except FileNotFoundError:
            existing_data_df = pd.DataFrame(columns=["id", "url", "headline", "author", "date"])
        return existing_data_df
    
    def add_row_to_csv(self, row):
        self.existing_data_df = self.read_csv()
        self.existing_data_df = pd.concat([self.existing_data_df, pd.DataFrame(row, index=[0])], ignore_index=True)
        self.write_csv(self.existing_data_df)

    def write_csv(self, data_df):
        data_df.to_csv(self.csv_filename, index=False)

