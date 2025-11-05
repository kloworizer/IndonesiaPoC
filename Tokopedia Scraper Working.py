# -*- coding: utf-8 -*-
"""
Created on Thu Sep 11 15:54:29 2025

@author: wb641752
"""

from tokopaedi import search, SearchFilters, get_product, get_reviews
import json
import pandas as pd
from pandas import json_normalize

filters = SearchFilters(
            bebas_ongkir_extra = True,
            pmin = 15000000,
            pmax = 25000000,
            rt = 4.5
        )

#results = search("Asus Zenbook S14 32GB", max_result=10, debug=False, filters=filters)


results = search("Asus Zenbook S14 32GB", max_result=10, debug=False)


# Enrich each result with product details and reviews
results.enrich_details(debug=False)
#results.enrich_reviews(max_result=50, debug=False)

# Convert to DataFrame and preview important fields
df = json_normalize(results.json())


results2 = get_product(url='https://www.tokopedia.com/rowey/rowey-sepatu-balet-wanita-flat-shoes-ballerina-sepatu-flat-wanita-layla-1732453439147246903?extParam=src%3Dshop%26whid%3D16229270&aff_unique_id=&channel=others&chain_key=', debug=True)
df2 = pd.json_normalize(results2.json())


# --- your original code above stays untouched ---


# === New code starts here ===

import os

# Select only relevant shop columns
shop_df = df[['shop.shop_id', 'shop.name', 'shop.city', 'shop.url', 'shop.shop_type']].copy()

# Rename columns for cleaner CSV
shop_df.columns = ['shop_id', 'shop_name', 'shop_city', 'shop_url', 'shop_type']

# Add a blank turnover column if it doesn’t exist
if 'turnover' not in shop_df.columns:
    shop_df['turnover'] = ""

# Path to your master shop database CSV
csv_path = "shops_database.csv"

# If the file already exists, merge with old data
if os.path.exists(csv_path):
    existing_df = pd.read_csv(csv_path, dtype={'shop_id': str})
    # Ensure new data also treats shop_id as string for consistency
    shop_df['shop_id'] = shop_df['shop_id'].astype(str)

    # Concatenate old + new, then deduplicate by shop_id
    combined_df = pd.concat([existing_df, shop_df], ignore_index=True)
    combined_df = combined_df.drop_duplicates(subset='shop_id', keep='first')
else:
    # If file doesn’t exist, start fresh
    combined_df = shop_df.copy()

# Save deduplicated database back to CSV
combined_df.to_csv(csv_path, index=False, encoding='utf-8-sig')

print(f"✅ Shop database updated and saved to '{csv_path}' with {len(combined_df)} unique shops.")



