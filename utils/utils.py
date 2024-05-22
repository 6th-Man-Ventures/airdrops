import os
import pandas as pd

def compile_directory_to_object(directory_path):
    data = dict()
    for filename in os.listdir(directory_path): # loop through dir
        if filename.endswith(".csv"):
            file_path = os.path.join(directory_path, filename)
            df = pd.read_csv(file_path)
            filename = filename.split(".")[0]
            data[filename] = df
    
    return data