# =============================================================================
# Annual NLCD Land Cover — County-Level Fractions via Google Earth Engine
# =============================================================================
# SETUP (run once in terminal):
#   conda install -c conda-forge earthengine-api geemap pandas
#   earthengine authenticate
# =============================================================================

import ee
import pandas as pd
import os

# --- Authenticate and initialize GEE ----------------------------------------
ee.Initialize(project='strong-imagery-464122-u0')

# --- Configuration -----------------------------------------------------------
YEARS        = list(range(1992, 2016))
DRIVE_FOLDER = "nlcd_county_exports"
SCALE        = 300    # meters — increase to 500 if tasks are slow

# --- NLCD land cover class values --------------------------------------------
NLCD_CLASSES = {
    11: "water",
    12: "ice_snow",
    21: "dev_open",
    22: "dev_low",
    23: "dev_med",
    24: "dev_high",
    31: "barren",
    41: "forest_dec",
    42: "forest_eve",
    43: "forest_mix",
    52: "shrub",
    71: "herbaceous",
    81: "hay_pasture",
    82: "crops",
    90: "wetland_woody",
    95: "wetland_emergent"
}

# --- Load county boundaries --------------------------------------------------
print("Loading county boundaries...")
counties = ee.FeatureCollection("TIGER/2018/Counties") \
    .map(lambda f: f.set(
        "county_fips",
        ee.String(f.get("STATEFP")).cat(ee.String(f.get("COUNTYFP")))
    ))

# --- Load Annual NLCD --------------------------------------------------------
print("Loading Annual NLCD collection...")
nlcd = ee.ImageCollection("projects/sat-io/open-datasets/USGS/ANNUAL_NLCD/LANDCOVER")

# --- Function: export one year -----------------------------------------------
def export_year(year):
    print(f"Submitting task for {year}...")

    # Get NLCD image for this year
    img = nlcd \
        .filter(ee.Filter.calendarRange(year, year, "year")) \
        .first() \
        .select([0], ["landcover"])

    # For each land cover class, create a binary band and sum per county
    # This is simpler and more reliable than histogram approach
    class_images = []
    for class_val, class_name in NLCD_CLASSES.items():
        binary = img.eq(class_val).rename(class_name)
        class_images.append(binary)

    # Stack all class bands into one image
    stacked = ee.Image.cat(class_images)

    # Also compute total valid pixels
    valid = img.neq(250).rename("total_valid")  # 250 = NoData in Annual NLCD
    stacked = stacked.addBands(valid)

    # Sum pixels per county for each band
    sums = stacked.reduceRegions(
        collection = counties,
        reducer    = ee.Reducer.sum(),
        scale      = SCALE,
        crs        = "EPSG:5070"
    )

    # Compute fractions from counts
    class_names = list(NLCD_CLASSES.values())
    def compute_fractions(f):
        total = ee.Number(f.get("total_valid"))
        props = {"county_fips": f.get("county_fips"), "year": year}
        for name in class_names:
            frac = ee.Number(f.get(name)).divide(total)
            props[f"frac_{name}"] = frac
        return f.set(props)

    result = sums.map(compute_fractions)

    # Export to Google Drive
    export_cols = ["county_fips", "year"] + [f"frac_{n}" for n in class_names]

    task = ee.batch.Export.table.toDrive(
        collection     = result,
        description    = f"nlcd_county_{year}",
        folder         = DRIVE_FOLDER,
        fileNamePrefix = f"nlcd_county_{year}",
        fileFormat     = "CSV",
        selectors      = export_cols
    )
    task.start()
    print(f"  Submitted: nlcd_county_{year}")
    return task

# =============================================================================
# MAIN
# =============================================================================
print(f"\nSubmitting {len(YEARS)} export tasks...")
print(f"Results will go to Google Drive folder: '{DRIVE_FOLDER}'\n")

tasks = []
for year in YEARS:
    task = export_year(year)
    tasks.append(task)

print(f"\nAll {len(tasks)} tasks submitted!")
print("Monitor at: https://code.earthengine.google.com/tasks")
print("Tasks typically complete in 5-30 minutes each.\n")

# =============================================================================
# MERGE: Run after downloading all CSVs from Google Drive
# =============================================================================

def merge_exports(downloads_folder="/Users/jyothiswaroopmakala/Downloads/nlcd_county_exports"):
    print("Merging CSVs...")
    dfs = []
    for year in YEARS:
        path = os.path.join(downloads_folder, f"nlcd_county_{year}.csv")
        if os.path.exists(path):
            df = pd.read_csv(path)
            df["year"] = year
            dfs.append(df)
            print(f"  Loaded {year}: {len(df)} counties")
        else:
            print(f"  Missing: {path}")
    if dfs:
        combined = pd.concat(dfs, ignore_index=True)
        out = os.path.join(downloads_folder, "nlcd_county_landcover_1992_2015.csv")
        combined.to_csv(out, index=False)
        print(f"\nSaved: {out}")
        print(f"Rows: {len(combined)}, Columns: {list(combined.columns)}")
    else:
        print("No files found.")

# Uncomment after all exports finish and CSVs are downloaded from Drive:
# merge_exports()# =============================================================================
# Annual NLCD Land Cover — County-Level Fractions via Google Earth Engine
# =============================================================================
# SETUP (run once in terminal):
#   conda install -c conda-forge earthengine-api geemap pandas
#   earthengine authenticate
# =============================================================================

import ee
import pandas as pd
import os

# --- Authenticate and initialize GEE ----------------------------------------
ee.Initialize(project='strong-imagery-464122-u0')

# --- Configuration -----------------------------------------------------------
YEARS        = list(range(1992, 2016))
DRIVE_FOLDER = "nlcd_county_exports"
SCALE        = 300    # meters — increase to 500 if tasks are slow

# --- NLCD land cover class values --------------------------------------------
NLCD_CLASSES = {
    11: "water",
    12: "ice_snow",
    21: "dev_open",
    22: "dev_low",
    23: "dev_med",
    24: "dev_high",
    31: "barren",
    41: "forest_dec",
    42: "forest_eve",
    43: "forest_mix",
    52: "shrub",
    71: "herbaceous",
    81: "hay_pasture",
    82: "crops",
    90: "wetland_woody",
    95: "wetland_emergent"
}

# --- Load county boundaries --------------------------------------------------
print("Loading county boundaries...")
counties = ee.FeatureCollection("TIGER/2018/Counties") \
    .map(lambda f: f.set(
        "county_fips",
        ee.String(f.get("STATEFP")).cat(ee.String(f.get("COUNTYFP")))
    ))

# --- Load Annual NLCD --------------------------------------------------------
print("Loading Annual NLCD collection...")
nlcd = ee.ImageCollection("projects/sat-io/open-datasets/USGS/ANNUAL_NLCD/LANDCOVER")

# --- Function: export one year -----------------------------------------------
def export_year(year):
    print(f"Submitting task for {year}...")

    # Get NLCD image for this year
    img = nlcd \
        .filter(ee.Filter.calendarRange(year, year, "year")) \
        .first() \
        .select([0], ["landcover"])

    # For each land cover class, create a binary band and sum per county
    # This is simpler and more reliable than histogram approach
    class_images = []
    for class_val, class_name in NLCD_CLASSES.items():
        binary = img.eq(class_val).rename(class_name)
        class_images.append(binary)

    # Stack all class bands into one image
    stacked = ee.Image.cat(class_images)

    # Also compute total valid pixels
    valid = img.neq(250).rename("total_valid")  # 250 = NoData in Annual NLCD
    stacked = stacked.addBands(valid)

    # Sum pixels per county for each band
    sums = stacked.reduceRegions(
        collection = counties,
        reducer    = ee.Reducer.sum(),
        scale      = SCALE,
        crs        = "EPSG:5070"
    )

    # Compute fractions from counts
    class_names = list(NLCD_CLASSES.values())
    def compute_fractions(f):
        total = ee.Number(f.get("total_valid"))
        props = {"county_fips": f.get("county_fips"), "year": year}
        for name in class_names:
            frac = ee.Number(f.get(name)).divide(total)
            props[f"frac_{name}"] = frac
        return f.set(props)

    result = sums.map(compute_fractions)

    # Export to Google Drive
    export_cols = ["county_fips", "year"] + [f"frac_{n}" for n in class_names]

    task = ee.batch.Export.table.toDrive(
        collection     = result,
        description    = f"nlcd_county_{year}",
        folder         = DRIVE_FOLDER,
        fileNamePrefix = f"nlcd_county_{year}",
        fileFormat     = "CSV",
        selectors      = export_cols
    )
    task.start()
    print(f"  Submitted: nlcd_county_{year}")
    return task

# =============================================================================
# MAIN
# =============================================================================
print(f"\nSubmitting {len(YEARS)} export tasks...")
print(f"Results will go to Google Drive folder: '{DRIVE_FOLDER}'\n")

tasks = []
for year in YEARS:
    task = export_year(year)
    tasks.append(task)

print(f"\nAll {len(tasks)} tasks submitted!")
print("Monitor at: https://code.earthengine.google.com/tasks")
print("Tasks typically complete in 5-30 minutes each.\n")

# =============================================================================
# MERGE: Run after downloading all CSVs from Google Drive
# =============================================================================

def merge_exports(downloads_folder="/Users/jyothiswaroopmakala/Downloads/nlcd_county"):
    print("Merging CSVs...")
    dfs = []
    for year in YEARS:
        path = os.path.join(downloads_folder, f"nlcd_county_{year}.csv")
        if os.path.exists(path):
            df = pd.read_csv(path)
            df["year"] = year
            dfs.append(df)
            print(f"  Loaded {year}: {len(df)} counties")
        else:
            print(f"  Missing: {path}")
    if dfs:
        combined = pd.concat(dfs, ignore_index=True)
        out = os.path.join(downloads_folder, "nlcd_county_1992_2015.csv")
        combined.to_csv(out, index=False)
        print(f"\nSaved: {out}")
        print(f"Rows: {len(combined)}, Columns: {list(combined.columns)}")
    else:
        print("No files found.")

# Uncomment after all exports finish and CSVs are downloaded from Drive:
merge_exports()