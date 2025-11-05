# -*- coding: utf-8 -*-
"""
Created on Wed Nov  5 23:06:11 2025

@author: wb641752
"""

import requests
import time
import json
import pandas as pd
from tokopaedi import get_product
from pandas import json_normalize
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# === Load CSV ===
df = pd.read_csv("shops_database.csv", dtype={'shop_id': str})

# --- Validation ---
if 'shop_id' not in df.columns:
    raise KeyError("❌ Column 'shop_id' not found in shops_database.csv")
if 'shop_name' not in df.columns:
    raise KeyError("❌ Column 'shop_name' not found in shops_database.csv")
if 'turnover' not in df.columns:
    raise KeyError("❌ Column 'turnover' not found in shops_database.csv")

# --- Prepare shop list ---
shop_data = df[['shop_id', 'shop_name']].dropna()
shop_data['shop_id'] = shop_data['shop_id'].astype(int)
shop_data = shop_data.head(2)  # limit to 2 shops for demo

urlTarget = 'https://gql.tokopedia.com/graphql/ShopProducts'

header = {
    'authority': 'gql.tokopedia.com',
    'method': 'POST',
    'path': '/graphql/ShopProducts',
    'scheme': 'https',
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9',
    'content-length': '1677',
    'content-type': 'application/json',
    'cookie': 'DID=35aae3e71151f85d472bf30407fa58404c747df50ceaf15875e856d1fc69430a8e3eb890ed832627027f4de2007370b1; ...',
    'origin': 'https://www.tokopedia.com',
    'referer': 'https://www.tokopedia.com/wd-official',
    'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'x-device': 'default_v3',
    'x-source': 'tokopedia-lite',
    'x-tkpd-lite-service': 'zeus',
    'x-version': 'ab79483'
}

# === Processing shops ===
for _, row_shop in shop_data.iterrows():
    shop_id = row_shop['shop_id']
    shop_name = row_shop['shop_name']
    print(f"\nProcessing shop ID: {shop_id} | Name: {shop_name}")

    page_number = 1
    hasil = []
    flag = True

    while flag:
        print('Fetching Page', page_number)

        query = f'''[{{"operationName":"ShopProducts","variables":{{"sid":"{shop_id}","page":{page_number},"perPage":80,"etalaseId":"etalase","sort":1,"user_districtId":"2274","user_cityId":"176","user_lat":"","user_long":""}},"query":"query ShopProducts($sid: String!, $page: Int, $perPage: Int, $keyword: String, $etalaseId: String, $sort: Int, $user_districtId: String, $user_cityId: String, $user_lat: String, $user_long: String) {{\\n  GetShopProduct(shopID: $sid, filter: {{page: $page, perPage: $perPage, fkeyword: $keyword, fmenu: $etalaseId, sort: $sort, user_districtId: $user_districtId, user_cityId: $user_cityId, user_lat: $user_lat, user_long: $user_long}}) {{\\n    status\\n    errors\\n    links {{ prev next __typename }}\\n    data {{\\n      name\\n      product_url\\n      product_id\\n      price {{ text_idr __typename }}\\n      primary_image {{ original thumbnail resize300 __typename }}\\n      flags {{ isSold isPreorder isWholesale isWishlist __typename }}\\n      campaign {{ discounted_percentage original_price_fmt start_date end_date __typename }}\\n      label {{ color_hex content __typename }}\\n      label_groups {{ position title type url __typename }}\\n      badge {{ title image_url __typename }}\\n      stats {{ reviewCount rating __typename }}\\n      category {{ id __typename }}\\n      __typename\\n    }}\\n    __typename\\n  }}\\n}}\\n"}}]'''

        res = requests.post(urlTarget, headers=header, data=query, verify=False)
        res_json = res.json()

        try:
            product = res_json[0]['data']['GetShopProduct']['data']
        except Exception as e:
            print(f"⚠️ Error fetching data for shop {shop_id}: {e}")
            break

        if not product:
            flag = False
            break

        for i in product:
            hasil.append({
                'nama': i['name'],
                'gambar': i['primary_image']['original'],
                'diskon': i['campaign']['discounted_percentage'],
                'rating': i['stats']['rating'],
                'URL': i['product_url']
            })

        page_number += 1
        time.sleep(0.5)

    # --- Convert to DataFrame ---
    df_products = pd.DataFrame.from_dict(hasil)
    if df_products.empty:
        print(f"⚠️ No products found for shop {shop_id}")
        continue

    # --- Enrich with product price and sold quantity ---
    product_revenues = []
    for idx, row in df_products.iterrows():
        product_url = row['URL']
        try:
            results2 = get_product(url=product_url, debug=False)
            df2 = pd.json_normalize(results2.json())

            try:
                price = df2['price'].iloc[0]
            except KeyError:
                price = 0

            try:
                sold_qty = df2['sold_count'].iloc[0]
            except KeyError:
                sold_qty = 0

            product_revenue = price * sold_qty

        except Exception as e:
            print(f"⚠️ Error fetching product details for {product_url}: {e}")
            price = 0
            sold_qty = 0
            product_revenue = 0

        df_products.loc[idx, 'price'] = price
        df_products.loc[idx, 'sold_qty'] = sold_qty
        df_products.loc[idx, 'product_revenue'] = product_revenue

        product_revenues.append(product_revenue)
        time.sleep(0.3)

    # --- Compute total shop revenue ---
    total_revenue = sum(product_revenues)
    print(f"💰 Total revenue for shop ID {shop_id} ({shop_name}): {total_revenue:,.0f} IDR")

    # --- Update turnover in main dataframe ---
    df.loc[df['shop_id'].astype(int) == shop_id, 'turnover'] = total_revenue

    # --- Save product data ---
    output_file = f"products_{shop_id}.csv"
    df_products.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"✅ Saved product data to {output_file}")

    time.sleep(2)

# --- Save updated shop database ---
df.to_csv("shops_database.csv", index=False, encoding='utf-8-sig')
print("✅ Updated 'turnover' column in shops_database.csv")
print('done')
