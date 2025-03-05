import pandas as pd

# Bemeneti és kimeneti fájlok elérési útja
input_file = "data/NYC_Building_Energy_and_Water_Data_Disclosure_for_Local_Law_84__2022-Present__20250106.csv"
output_file = "data_reduced.csv"

# A megtartandó oszlopok listája (hozzáadtuk a "Latitude" és "Longitude" oszlopokat a térképhez)
columns_to_keep = ["Property ID", "Property Name", "Address 1", "ENERGY STAR Score", "Postal Code", "Year Built", "Calendar Year", "Latitude", "Longitude", "Site Energy Use (kBtu)"
]

# Chunkméret beállítása
chunk_size = 100_000  

# Új CSV létrehozása
with open(output_file, "w", encoding="utf-8", newline="") as f:
    for chunk in pd.read_csv(input_file, usecols=columns_to_keep, chunksize=chunk_size, low_memory=False):
        chunk.to_csv(f, index=False, header=f.tell() == 0, mode="a")

print("✅ Adatok sikeresen mentve a 'data_reduced.csv' fájlba!")
