import pandas as pd
import glob
import os

def import_all_csvs(folder1, folder2):
    csv_files = glob.glob(os.path.join(folder1, "*.csv")) + glob.glob(os.path.join(folder2, "*.csv"))
    dataframes = [pd.read_csv(f) for f in csv_files]
    all_data = pd.concat(dataframes, ignore_index=True)
    return all_data

if __name__ == "__main__":
    folder1 = input("Enter path to first folder: ")
    folder2 = input("Enter path to second folder: ")
    all_data = import_all_csvs(folder1, folder2)
    print("Imported data shape:", all_data.shape)
    print(all_data.head())
    # You can now pass 'all_data' to your pipeline functions
