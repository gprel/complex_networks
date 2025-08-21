import pandas as pd
import math

# Load dataset
url = "https://gist.githubusercontent.com/tadast/8827699/raw/countries_codes_and_coordinates.csv"
df = pd.read_csv(url)

df["Longitude (average)"] = (
    df["Longitude (average)"]
    .astype(str)
    .str.replace('"', '', regex=False)
    .astype(float)
)

df["Latitude (average)"] = (
    df["Latitude (average)"]
    .astype(str)
    .str.replace('"', '', regex=False)
    .astype(float)
)

df["Alpha-3 code"] = (
    df["Alpha-3 code"]
    .astype(str)
    .str.replace('"', '', regex=False)
    .str.strip()
)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) *
         math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.asin(math.sqrt(a))
    return R * c

def compute_distance(iso1, iso2):
    iso1, iso2 = iso1.upper(), iso2.upper()
    
    if iso1 == iso2:
        return 'They are equal'
    
    if iso1 not in df["Alpha-3 code"].values or iso2 not in df["Alpha-3 code"].values:
        return f"{iso1} or {iso2} doesn't exist"

    lat1, lon1 = df.loc[df["Alpha-3 code"] == iso1, ["Latitude (average)", "Longitude (average)"]].values[0]
    lat2, lon2 = df.loc[df["Alpha-3 code"] == iso2, ["Latitude (average)", "Longitude (average)"]].values[0]
    
    return haversine(lat1, lon1, lat2, lon2)

# Example usage:
print(compute_distance("USA", "CAN"))
