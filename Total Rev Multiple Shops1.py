
import pandas as pd
import requests
import time
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

df = pd.read_csv("shops_database.csv", dtype={'shop_id': str})


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
    'cookie': 'DID=35aae3e71151f85d472bf30407fa58404c747df50ceaf15875e856d1fc69430a8e3eb890ed832627027f4de2007370b1; DID_JS=MzVhYWUzZTcxMTUxZjg1ZDQ3MmJmMzA0MDdmYTU4NDA0Yzc0N2RmNTBjZWFmMTU4NzVlODU2ZDFmYzY5NDMwYThlM2ViODkwZWQ4MzI2MjcwMjdmNGRlMjAwNzM3MGIx47DEQpj8HBSa+/TImW+5JCeuQeRkm5NMpJWZG3hSuFU=; _UUID_NONLOGIN_=259ba7cb91ac26b22c902995a6bb8bac; _gcl_au=1.1.1885528358.1670948295; _UUID_CAS_=9c9df32d-5a9f-45dd-901d-a09a1f2119f9; __auc=0e7a190d1850c47a20d9dd4209c; _fbp=fb.1.1670948301346.960270670; webauthn-session=e3cc4915-ab1d-46a5-915e-787299970543; _CASE_=237a3c113c7a626a6a6f6c747a39113c7a6268747a343a347a627a123933392a2c3978082d2b392c7a747a3b113c7a62696f6e747a3437363f7a627a7a747a34392c7a627a7a747a281b377a627a7a747a2f113c7a62696a6a69686b6f6d747a2b113c7a6269696d6b686d6f6b747a2b0c21283d7a627a6a307a747a2f302b7a627a0323047a2f392a3d30372d2b3d07313c047a62696a6a69686b6f6d74047a2b3d2a2e313b3d072c21283d047a62047a6a30047a74047a07072c21283d3639353d047a62047a0f392a3d30372d2b3d2b047a257423047a2f392a3d30372d2b3d07313c047a626874047a2b3d2a2e313b3d072c21283d047a62047a696d35047a74047a07072c21283d3639353d047a62047a0f392a3d30372d2b3d2b047a25057a747a340d283c7a627a6a686a6a75696a75696f0c6968626b6a626d6073686f6268687a25; l=1; TOPATK=jjjOCUAUQmSSA647Rpdw9g; _hjSessionUser_714968=eyJpZCI6ImRkODVmMDAyLWZlOTItNTk5OC1hMzZhLTU3OWU0MGVlNzQ3NyIsImNyZWF0ZWQiOjE2NzE2OTUzMjY0MDEsImV4aXN0aW5nIjpmYWxzZX0=; _gcl_aw=GCL.1671695329.Cj0KCQiA-oqdBhDfARIsAO0TrGHpUrOWBH5CNg6IUDqohGCQ0TzMH7P5gvuFew4XXcjD3xICQBCqR20aAi5DEALw_wcB; _gcl_dc=GCL.1671695329.Cj0KCQiA-oqdBhDfARIsAO0TrGHpUrOWBH5CNg6IUDqohGCQ0TzMH7P5gvuFew4XXcjD3xICQBCqR20aAi5DEALw_wcB; _gac_UA-126956641-6=1.1671695329.Cj0KCQiA-oqdBhDfARIsAO0TrGHpUrOWBH5CNg6IUDqohGCQ0TzMH7P5gvuFew4XXcjD3xICQBCqR20aAi5DEALw_wcB; _gac_UA-9801603-1=1.1671695348.Cj0KCQiA-oqdBhDfARIsAO0TrGHpUrOWBH5CNg6IUDqohGCQ0TzMH7P5gvuFew4XXcjD3xICQBCqR20aAi5DEALw_wcB; bm_sz=6B57B2DAFE98DE5B9B1E9B1476DC5D72~YAAQLGswF6JDHCuFAQAAx+wRgBJ1OcSQRhzh/BvVgLapkcftDKKx39Ocp9z9qlZjyHZAHZIao0quD+FN/aP4AT3QMFlnYciYEWfoKl0YxNL9fwGou5RMIrj57cGtWfsdAboGh43S1td83LJqkCylBlsZYFGsMXtYv2Xemc41oQx803hsN7e/t5Q0bm2/oCkLr2o0vGgoY7u3dTJgLBqZ9JogOdAYbgXsAQmQP/xzaSK6QclEGmzFbaz8PTr39Vi53NGXUN91L2mmgofXKdwkXvifnHrAcImsV6TaLXKeS93H86784rk=~3687220~4339524; bm_mi=79E7809CF9B229E82E904FC98BDDF26E~YAAQLGswFyBFHCuFAQAAJTQSgBKxKl4yXYYll3y2nhfut0IJh47Zdi1fWJDIceomAlZ0/8WwrurbQ9mA3z5+ZhIhPS14gvAj7MiKogWmZCl8UL1vYazRNpv20iDrLRnqxI5inxhc51uzu9i9yasOx7ebiJRZ+JtjihG7Uns/MZWVxYVYruCnbeQ4V7lZ3CLtGf2T1cR3f3fI2Nu3LmfxpqV/y0q3Gq48cOrEvTyJaUIdYEq9RqBT764imXplz388cZ4qpKq3V+WYwqMPiM8M7fW/ezR82IhJG/hnVUVKYp7zMjsCOKPopB7sMgBuSLfDBQ==~1; _SID_Tokopedia_=_Ptyp0-dOo5ZmE4eWgCbtzEDqryMii6xRiE1iNt4XG1r6PTwiPGYNkr_JLrUvH2guplbypiYzNt102gi61403kL7cU9GGutX0CTXeoMHz10X2uDiBS3WsKc8cpYF22Cm; _gid=GA1.2.739952466.1672890958; ak_bmsc=D2054B8C0548F42A1DCF57D5B625E166~000000000000000000000000000000~YAAQLGswF/9FHCuFAQAAF04SgBKjUfcfJTQfTnFqra2AlLe+O/MBIoHnfIp6fgG3EgWaC8kOCyuikCG9c+ax70g8SAHm5JSqlHRxwPW5ELaXVA9FH54GxPPQoYoBDWDy1L9veJi1OOd5ScB0X+4AYL0KX1tiKqciobIB8b9oi+k81Tq8nd0GfEbCAkAwUtQfNjQ5pdRhMvsUYokzUuCdTHNW4iaCAJx/PLFZYrzyewOS8es5RXMEStmhX4zsTQLo4dCMm42YPMRFNfZZgByKewaZasOdx5xXZc4sQJlUaQXehKFAOLRjUPlpA7Os6ZSqZ1kmIKcF8Qw0rfdWuUApn5VAfI37134Rr6tqs499ox+iafMzkzGRv/ipvf6MzeBASHvB/t24yePZmCkmkuIWvysy0y70FcrHWN6WvI8uR4gq7+7168THB3H/fw+9TxeUI4B73RGoFl0rHurHpH+Fx10jt3lDGoXG3ytsGA7TKE+VoYt9U2UapiMVp+TgOuaZwCfc6A==; __asc=b60f2c7018580124f918ffab5af; hfv_banner=true; AMP_TOKEN=%24NOT_FOUND; bm_sv=D9BA677409A4D33B6E8D2B5769A5006E~YAAQZeUcuEqOARqFAQAAgHobgBJdg9mpiOveJKE+mqtu1QfUnFuvrdh4M4aaSt9MjM1kgvbOPgdgTGHdA/gjqyLnXWJrpqZ8/C0xXy6KIriFhcW15n0pCWMZvOms73F5y/iU3ZnvsH+sJngZo3HYgfwiGJegWe1Qhxvup9nAVt/SAcxYR8hiXVH2px+yezWNESru1jTKXuHC+mz6DiQjjOAAlQ4bfSdTrFs99CYHo5U4lXK7jHqPIdihJM7uJByLuMFo~1; _dc_gtm_UA-126956641-6=1; _dc_gtm_UA-9801603-1=1; _abck=F2C7D5EBA2B94554D9B98EAC42F14373~0~YAAQ0awwFzMmgXOFAQAAWPUjgAnYUsNZikWiTn5VY76a9raT08Q3W+/ZvOzWS6/Aqsc46jEs5TeT7rCYKrJaHLpIwvEp31nw83gmco4Q4Nk2jy5UH8ptX/ivuuUhbliLsCMyZSNFmPnCStp1mN99zsYs4T3TuRT0ZzOYSOjZt4N/mjmk5Qkhiu/QbBFVHJcdwGeYBLZ3HEsXlq4avz+gb/8O0ykLxRp6VQpiEX9ygSV0iMPjqSkfF88LBn0CvaeoCPi+T/Pq5nj+/s8qKItjV5Crx8+6XpFS6C8dwtApTcZJlCJK93lToj2Qe9ANYjyoWIhnTaMB63GN3jgn2qpwwUrcbbRFA84hwwJkQvkJRRsidHf3LiZ+LhwZPBP+kOtGqKfZ7HP+m/h/Lp6dRFjt1l6316+fWuYXY69o~-1~-1~-1; _ga=GA1.2.759598861.1670948296; _ga_70947XW48P=GS1.1.1672890958.6.1.1672892126.51.0.0',
    'origin': 'https://www.tokopedia.com',
    'referer': 'https://www.tokopedia.com/wd-official',
    #'referer': 'https://www.tokopedia.com/ellaglo',
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
    """
    Convert Indonesian sales strings like '100+ terjual' or '2rb+ terjual'
    into integer values. If the input doesn't represent a number (e.g. 'Campaign'),
    return 0.
    """
    if not isinstance(sales_str, str):
        return 0

    s = sales_str.lower().replace(' terjual', '').replace('+', '').strip()

    # Handle non-numeric or irrelevant strings
    if not any(char.isdigit() for char in s):
        return 0

    try:
        if 'rb' in s:  # 'rb' = 'ribu' = thousand
            num = float(s.replace('rb', '')) * 1000
        else:
            num = float(s)
        return int(num)
    except ValueError:
        return 0


def parse_rupiah(rp_str: str) -> int:
    """
    Convert Rupiah strings like 'Rp191.890' or 'Rp191,890' into integers (e.g., 191890).
    """
    s = rp_str.lower().replace('rp', '').strip()
    s = s.replace('.', '').replace(',', '')  # remove separators
    return int(s)

for shop_id in shop_ids:
    print(f"Processing shop ID: {shop_id}")
    page_number = 1    
    hasil = []
    flag = True
    while flag:
        #print('Fetching Page', page_number)
        
    #    query = f'[{{"operationName":"ShopProducts","variables":{{"sid":"2706562","page":{page_number},"perPage":80,"etalaseId":"etalase","sort":1,"user_districtId":"2274","user_cityId":"176","user_lat":"","user_long":""}},"query":"query ShopProducts($sid: String\u0021, $page: Int, $perPage: Int, $keyword: String, $etalaseId: String, $sort: Int, $user_districtId: String, $user_cityId: String, $user_lat: String, $user_long: String) {{\\n  GetShopProduct(shopID: $sid, filter: {{page: $page, perPage: $perPage, fkeyword: $keyword, fmenu: $etalaseId, sort: $sort, user_districtId: $user_districtId, user_cityId: $user_cityId, user_lat: $user_lat, user_long: $user_long}}) {{\\n    status\\n    errors\\n    links {{\\n      prev\\n      next\\n      __typename\\n    }}\\n    data {{\\n      name\\n      product_url\\n      product_id\\n      price {{\\n        text_idr\\n        __typename\\n      }}\\n      primary_image {{\\n        original\\n        thumbnail\\n        resize300\\n        __typename\\n      }}\\n      flags {{\\n        isSold\\n        isPreorder\\n        isWholesale\\n        isWishlist\\n        __typename\\n      }}\\n      campaign {{\\n        discounted_percentage\\n        original_price_fmt\\n        start_date\\n        end_date\\n        __typename\\n      }}\\n      label {{\\n        color_hex\\n        content\\n        __typename\\n      }}\\n      label_groups {{\\n        position\\n        title\\n        type\\n        url\\n        __typename\\n      }}\\n      badge {{\\n        title\\n        image_url\\n        __typename\\n      }}\\n      stats {{\\n        reviewCount\\n        rating\\n        __typename\\n      }}\\n      category {{\\n        id\\n        __typename\\n      }}\\n      __typename\\n    }}\\n    __typename\\n  }}\\n}}\\n"}}]'
        query = f'[{{"operationName":"ShopProducts","variables":{{"sid":"{shop_id}","page":{page_number},"perPage":80,"etalaseId":"etalase","sort":1,"user_districtId":"2274","user_cityId":"176","user_lat":"","user_long":""}},"query":"query ShopProducts($sid: String\u0021, $page: Int, $perPage: Int, $keyword: String, $etalaseId: String, $sort: Int, $user_districtId: String, $user_cityId: String, $user_lat: String, $user_long: String) {{\\n  GetShopProduct(shopID: $sid, filter: {{page: $page, perPage: $perPage, fkeyword: $keyword, fmenu: $etalaseId, sort: $sort, user_districtId: $user_districtId, user_cityId: $user_cityId, user_lat: $user_lat, user_long: $user_long}}) {{\\n    status\\n    errors\\n    links {{\\n      prev\\n      next\\n      __typename\\n    }}\\n    data {{\\n      name\\n      product_url\\n      product_id\\n      price {{\\n        text_idr\\n        __typename\\n      }}\\n      primary_image {{\\n        original\\n        thumbnail\\n        resize300\\n        __typename\\n      }}\\n      flags {{\\n        isSold\\n        isPreorder\\n        isWholesale\\n        isWishlist\\n        __typename\\n      }}\\n      campaign {{\\n        discounted_percentage\\n        original_price_fmt\\n        start_date\\n        end_date\\n        __typename\\n      }}\\n      label {{\\n        color_hex\\n        content\\n        __typename\\n      }}\\n      label_groups {{\\n        position\\n        title\\n        type\\n        url\\n        __typename\\n      }}\\n      badge {{\\n        title\\n        image_url\\n        __typename\\n      }}\\n      stats {{\\n        reviewCount\\n        rating\\n        __typename\\n      }}\\n      category {{\\n        id\\n        __typename\\n      }}\\n      __typename\\n    }}\\n    __typename\\n  }}\\n}}\\n"}}]'
    
        res = requests.post(urlTarget, headers=header, data=query, verify=False)
    
        #res = requests.post(urlTarget, headers=header, data=query)
    
        resJson = res.json()
    
        
        product = resJson[0]['data']['GetShopProduct']['data']
        for i in product:
            name = i['name']
            price = parse_rupiah(i['price']['text_idr'])
            image = i['primary_image']['original']
            discount = i['campaign']['discounted_percentage']
            rating = i['stats']['rating']
            sold_dict = i['label_groups']
            product_url =i['product_url']
            for group in sold_dict:
                title = group['title']
                sold=title
                #print("\n\n\nSold\n\n\n",sold)
                break
            
        
            hasil.append({
                'nama': name,
                'harga': price,
                'gambar': image,
                'diskon': discount,
                'rating': rating,
                'sold' : parse_sales(sold),
                'URL' : product_url
                })
        if not product:
            flag = False
        page_number+=1
        #print(hasil)
    df = pd.DataFrame.from_dict(hasil)
    df["product_revenue"] = df["harga"] * df["sold"]
    total_revenue = df["product_revenue"].sum()
    print(f"Total revenue: Rp {total_revenue:,.0f}")
    


print('done')

