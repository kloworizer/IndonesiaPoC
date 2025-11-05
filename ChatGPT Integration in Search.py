# -*- coding: utf-8 -*-
"""
Created on Wed Nov  5 23:46:28 2025

@author: wb641752
"""

from tokopaedi import search, SearchFilters, get_product, get_reviews
import json
import pandas as pd
from pandas import json_normalize
import os

# === NEW CODE: Load all search terms from CSV ===
search_terms_df = pd.read_csv("Search_Texts.csv")
search_terms = search_terms_df["search_text"].dropna().tolist()

# === Your original search filters remain unchanged ===
filters = SearchFilters(
    bebas_ongkir_extra=True,
    pmin=15000000,
    pmax=25000000,
    rt=4.5
)

# Path to your master shop database CSV
csv_path = "shops_database_AI.csv"

# If database exists, load it once at the start
if os.path.exists(csv_path):
    combined_df = pd.read_csv(csv_path, dtype={'shop_id': str})
else:
    combined_df = pd.DataFrame(columns=['shop_id', 'shop_name', 'shop_city', 'shop_url', 'shop_type', 'turnover'])

# === Loop through each search term ===
for term in search_terms:
    print(f"\n🔍 Searching for: {term}")

    # --- Your original search code ---
    results = search(term, max_result=10, debug=False)
    results.enrich_details(debug=False)

    df = json_normalize(results.json())

    # Optional: still get one sample product if you want
    """
    results2 = get_product(
        url='https://www.tokopedia.com/rowey/rowey-sepatu-balet-wanita-flat-shoes-ballerina-sepatu-flat-wanita-layla-1732453439147246903?extParam=src%3Dshop%26whid%3D16229270&aff_unique_id=&channel=others&chain_key=',
        debug=False
    )
    df2 = pd.json_normalize(results2.json())
    """
    # --- your original code above stays untouched ---

    # === New code starts here ===

    # Select only relevant shop columns
    shop_df = df[['shop.shop_id', 'shop.name', 'shop.city', 'shop.url', 'shop.shop_type']].copy()

    # Rename columns for cleaner CSV
    shop_df.columns = ['shop_id', 'shop_name', 'shop_city', 'shop_url', 'shop_type']

    # Add a blank turnover column if it doesn’t exist
    if 'turnover' not in shop_df.columns:
        shop_df['turnover'] = ""

    # Ensure shop_id is string for consistency
    shop_df['shop_id'] = shop_df['shop_id'].astype(str)

    # Merge with existing master CSV and deduplicate
    combined_df = pd.concat([combined_df, shop_df], ignore_index=True)
    combined_df = combined_df.drop_duplicates(subset='shop_id', keep='first')

# === Save deduplicated database after all searches ===
combined_df.to_csv(csv_path, index=False, encoding='utf-8-sig')
print(f"\n✅ Shop database updated and saved to '{csv_path}' with {len(combined_df)} unique shops from {len(search_terms)} searches.")
