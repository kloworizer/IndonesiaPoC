# -*- coding: utf-8 -*-
"""
Created on Wed Nov  5 23:24:56 2025

@author: wb641752
"""

import pandas as pd
import requests
import time
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

df = pd.read_csv("shops_database.csv", dtype={'shop_id': str})

# ✅ Ensure column exists before processing
if 'turnover_estimate' not in df.columns:
    df['turnover_estimate'] = 0

if 'shop_id' not in df.columns:
    raise KeyError("❌ Column 'shop_id' not found in shops_database.csv")
    
shop_ids = df['shop_id'].dropna().astype(int).tolist()
    
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

page_number = 1

def parse_sales(sales_str: str) -> int:
    if not isinstance(sales_str, str):
        return 0
    s = sales_str.lower().replace(' terjual', '').replace('+', '').strip()
    if not any(char.isdigit() for char in s):
        return 0
    try:
        if 'rb' in s:
            num = float(s.replace('rb', '')) * 1000
        else:
            num = float(s)
        return int(num)
    except ValueError:
        return 0

def parse_rupiah(rp_str: str) -> int:
    s = rp_str.lower().replace('rp', '').strip()
    s = s.replace('.', '').replace(',', '')
    return int(s)

for shop_id in shop_ids:
    print(f"Processing shop ID: {shop_id}")
    page_number = 1    
    hasil = []
    flag = True
    while flag:
        query = f'[{{"operationName":"ShopProducts","variables":{{"sid":"{shop_id}","page":{page_number},"perPage":80,"etalaseId":"etalase","sort":1,"user_districtId":"2274","user_cityId":"176","user_lat":"","user_long":""}},"query":"query ShopProducts($sid: String\u0021, $page: Int, $perPage: Int, $keyword: String, $etalaseId: String, $sort: Int, $user_districtId: String, $user_cityId: String, $user_lat: String, $user_long: String) {{\\n  GetShopProduct(shopID: $sid, filter: {{page: $page, perPage: $perPage, fkeyword: $keyword, fmenu: $etalaseId, sort: $sort, user_districtId: $user_districtId, user_cityId: $user_cityId, user_lat: $user_lat, user_long: $user_long}}) {{\\n    status\\n    errors\\n    links {{\\n      prev\\n      next\\n      __typename\\n    }}\\n    data {{\\n      name\\n      product_url\\n      product_id\\n      price {{\\n        text_idr\\n        __typename\\n      }}\\n      primary_image {{\\n        original\\n        thumbnail\\n        resize300\\n        __typename\\n      }}\\n      flags {{\\n        isSold\\n        isPreorder\\n        isWholesale\\n        isWishlist\\n        __typename\\n      }}\\n      campaign {{\\n        discounted_percentage\\n        original_price_fmt\\n        start_date\\n        end_date\\n        __typename\\n      }}\\n      label {{\\n        color_hex\\n        content\\n        __typename\\n      }}\\n      label_groups {{\\n        position\\n        title\\n        type\\n        url\\n        __typename\\n      }}\\n      badge {{\\n        title\\n        image_url\\n        __typename\\n      }}\\n      stats {{\\n        reviewCount\\n        rating\\n        __typename\\n      }}\\n      category {{\\n        id\\n        __typename\\n      }}\\n      __typename\\n    }}\\n    __typename\\n  }}\\n}}\\n"}}]'
    
        res = requests.post(urlTarget, headers=header, data=query, verify=False)
        resJson = res.json()
    
        product = resJson[0]['data']['GetShopProduct']['data']
        for i in product:
            name = i['name']
            price = parse_rupiah(i['price']['text_idr'])
            image = i['primary_image']['original']
            discount = i['campaign']['discounted_percentage']
            rating = i['stats']['rating']
            sold_dict = i['label_groups']
            product_url = i['product_url']
            for group in sold_dict:
                title = group['title']
                sold = title
                break
            
            hasil.append({
                'nama': name,
                'harga': price,
                'gambar': image,
                'diskon': discount,
                'rating': rating,
                'sold': parse_sales(sold),
                'URL': product_url
            })
        if not product:
            flag = False
        page_number += 1

    df_temp = pd.DataFrame.from_dict(hasil)
    df_temp["product_revenue"] = df_temp["harga"] * df_temp["sold"]
    total_revenue = df_temp["product_revenue"].sum()
    print(f"Total revenue: Rp {total_revenue:,.0f}")

    # ✅ NEW: Save total revenue to shops_database.csv
    df.loc[df['shop_id'].astype(int) == shop_id, 'turnover_estimate'] = total_revenue

# ✅ Save updated CSV
df.to_csv("shops_database.csv", index=False, encoding='utf-8-sig')

print('✅ Updated shops_database.csv with turnover_estimate')
print('done')
