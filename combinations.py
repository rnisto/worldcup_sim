
import pandas as pd

combinations = pd.read_csv("./r32_combinations.csv")
combinations.columns = ['Index', '1', '2', '3', '4',
       '5', '6', '7', '8', '9','10', '11', '12', 'Blank', '1A',
       '1B', '1D', '1E', '1G', '1I', '1K', '1L']

combinations['third_place'] = combinations[combinations.columns[1:13]].apply(
    lambda x: ''.join(x.dropna().astype(str)),
    axis=1
)

cols = ['1A','1B', '1D', '1E', '1G', '1I', '1K', '1L'] 
combinations[cols] = combinations[cols].replace('[1-9]', '', regex=True)
combinations = combinations[["third_place", "1A", "1B", "1D", "1E", "1G", "1I", "1K", "1L"]]