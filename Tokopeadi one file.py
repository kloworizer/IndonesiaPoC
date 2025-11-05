# -*- coding: utf-8 -*-
"""
Created on Thu Sep 18 16:02:35 2025

@author: wb641752
"""


##################################

import pandas as pd
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Iterator

def shop_resolver(shop_tier):
    ''' Find shop tier by id and badge image '''
    try:
        shop_tier = int(shop_tier)
    except ValueError:
        # More specific error handling
        if 'PM%20Pro%20Small.png' in shop_tier:
            shop_tier = 3
        elif 'official_store_badge' in shop_tier:
            shop_tier = 2
        else:
            shop_tier = 1

    if shop_tier == 1:
        return 'Normal'
    elif shop_tier == 2:
        return 'Mall'
    elif shop_tier == 3:
        return 'Power Shop'
    else:
        return None

@dataclass
class ProductReview:
    feedback_id: int
    variant_name: Optional[str]
    message: str
    rating: float
    review_age: str
    user_full_name: str
    user_url: str
    response_message: Optional[str]
    response_created_text: Optional[str]
    images: List[str] = field(default_factory=list)
    videos: List[str] = field(default_factory=list)
    likes: int = 0

    def json(self):
        ''' Convert the ProductReview to a dictionary '''
        return asdict(self)

@dataclass
class TokopaediShop:
    shop_id: int
    name: str
    city: Optional[str]
    url: str
    shop_type: str

@dataclass
class ProductMedia:
    original: str
    thumbnail: str
    max_res: str

@dataclass
class ProductOption:
    option_id: int
    option_name: str
    option_child: List[str]

@dataclass
class ProductVariant:
    option_ids: List[int]
    option_name: str
    option_url: str
    price: int
    price_string: str
    discount: str
    image_url: Optional[str] = None
    stock: Optional[int] = None

@dataclass
class ProductData:
    product_id: int
    product_sku: str
    product_name: str
    url: str
    main_image: Optional[str] = None
    status: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None
    price_text: Optional[str] = None
    price_original: Optional[str] = None
    discount_percentage: Optional[str] = None
    weight: Optional[int] = None
    weight_unit: Optional[str] = None
    product_media: List[ProductMedia] = field(default_factory=list)
    sold_count: Optional[int] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    discussion_count: Optional[int] = None
    total_stock: Optional[int] = None
    etalase: Optional[str] = None
    etalase_url: Optional[str] = None
    category: str = None
    sub_category: Optional[List[str]] = None
    product_option: Optional[List[ProductOption]] = None
    variants: Optional[List[ProductVariant]] = None
    shop: TokopaediShop = None
    reviews: Optional[List[ProductReview]] = None
    has_detail: bool = False
    has_reviews: bool = False

    def json(self):
        ''' Convert the ProductData to a dictionary '''
        return asdict(self)

    def enrich_details(self, debug: bool = False):
        ''' Enrich product details by fetching additional data '''
        if not self.has_detail:
            
            enriched_details = get_product(product_id=self.product_id, debug=debug)

            if enriched_details:
                for field_name in self.__dataclass_fields__:
                    setattr(self, field_name, getattr(enriched_details, field_name))
            self.has_detail = True

    def enrich_reviews(self, max_result=None, debug: bool = False):
        ''' Enrich product reviews by fetching review data '''
        if not self.has_reviews:
            
            self.reviews = get_reviews(product_id=self.product_id, max_result=max_result, debug=debug)
            self.has_reviews = True

class SearchResults:
    def __init__(self, items: List[ProductData] = None):
        ''' Initialize with an optional list of ProductData '''
        self.items = items or []

    def enrich_details(self, debug=False):
        ''' Enrich the details for all products in the list '''
        for product in self.items:
            product.enrich_details(debug)

    def enrich_reviews(self, max_result=None, debug=False):
        ''' Enrich the reviews for all products in the list '''
        for product in self.items:
            product.enrich_reviews(max_result, debug)

    def append(self, item: ProductData) -> None:
        ''' Append a product to the results list '''
        self.items.append(item)

    def extend(self, more: List[ProductData]) -> None:
        ''' Extend the results list with more products '''
        self.items.extend(more)

    def __getitem__(self, index) -> ProductData:
        ''' Get a product by index '''
        return self.items[index]

    def __iter__(self) -> Iterator[ProductData]:
        ''' Iterate through the products '''
        return iter(self.items)

    def __len__(self) -> int:
        ''' Get the length of the results list '''
        return len(self.items)

    def json(self) -> List[dict]:
        ''' Convert all products to a list of dictionaries '''
        return [item.json() for item in self.items]

    def __repr__(self) -> str:
        ''' String representation of the SearchResults object '''
        return f"<SearchResults total={len(self.items)}>"

    def __add__(self, other: "SearchResults") -> "SearchResults":
        ''' Add two SearchResults objects together '''
        if not isinstance(other, SearchResults):
            return NotImplemented
        return SearchResults(self.items + other.items)

    def __iadd__(self, other: "SearchResults") -> "SearchResults":
        ''' In-place add for SearchResults objects '''
        if not isinstance(other, SearchResults):
            return NotImplemented
        self.extend(other.items)
        return self




###################################

#logging

import logging

def setup_custom_logging():
    SEARCH_LEVEL = 25
    DETAIL_LEVEL = 26
    REVIEWS_LEVEL = 27

    logging.addLevelName(SEARCH_LEVEL, "SEARCH")
    logging.addLevelName(DETAIL_LEVEL, "DETAIL")
    logging.addLevelName(REVIEWS_LEVEL, "REVIEW")

    class CustomLogger(logging.Logger):
        def search(self, message, *args, **kwargs):
            if self.isEnabledFor(SEARCH_LEVEL):
                self._log(SEARCH_LEVEL, message, args, **kwargs)
        
        def detail(self, message, *args, **kwargs):
            if self.isEnabledFor(DETAIL_LEVEL):
                self._log(DETAIL_LEVEL, message, args, **kwargs)
        
        def reviews(self, message, *args, **kwargs):
            if self.isEnabledFor(REVIEWS_LEVEL):
                self._log(REVIEWS_LEVEL, message, args, **kwargs)

    logging.setLoggerClass(CustomLogger)

    logging.basicConfig(
        level=SEARCH_LEVEL,
        format="{asctime} - {levelname} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M",
    )

    return logging.getLogger(__name__)


#################################

#Fingerprint


import random
import uuid
import json
import base64

def randomize_fp():
    user_id = [
                "223400020",
                "223400013",
                "223400069",
                "223400121",
                "223400127",
                "223400155",
                "223400222",
                "223400306",
                "223400283",
                "223400333",
                "223400375",
                "223400401",
                "223400518",
                "223400645",
                "223400790",
                "223400813",
                "223400873",
                "223400897",
                "223400963",
                "223401040",
                "223401175",
                "223401183",
                "223401452",
                "223401492",
                "223401493",
                "223401538",
                "223401665",
                "223401754",
                "223401902",
                "223401916",
                "223401917",
                "223401930",
                "223401947",
                "223401978",
                "223402015",
                "223402029",
                "223402064",
                "223402123",
                "223402191",
                "223402301",
                "223402349",
                "223402559",
                "223402574",
                "223402628",
                "223402629",
                "223402704",
                "223402725",
                "223402769",
                "223403073",
                "223403136",
                "223403203",
                "223403259",
                "223403265",
                "223403307",
                "223403378",
                "223403449",
                "223403480",
                "223403556",
                "223403607",
                "223403658",
                "223403693",
                "223403697",
                "223403724",
                "223403781",
                "223403814",
                "223403968",
                "223403994",
                "223404084",
                "223404155",
                "223404217",
                "223404226",
                "223404296",
                "223404394",
                "223404413",
                "223404427",
                "223404433",
                "223404477",
                "223404522",
                "223404617",
                "223404632",
                "223404679",
                "223404815",
                "223404840",
                "223404898",
                "223404906",
                "223405003",
                "223405034",
                "223405188",
                "223405199",
                "223405266",
                "223405302",
                "223405343",
                "223405359"
            ]
    iphone_models = [
        "iPhone SE", "iPhone 8", "iPhone X", "iPhone 11", "iPhone 12",
        "iPhone 13", "iPhone 14 Pro", "iPhone 15 Pro Max"
    ]
    ios_versions = ["15.7", "16.6", "17.0", "17.5", "18.0", "18.5"]
    screen_resolutions = [
        "1334x750", "1792x828", "2532x1170", "2778x1284", "2556x1179"
    ]
    user_agents = [
        "Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
        "Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_0_1 like Mac OS X; en-us) AppleWebKit/532.9 (KHTML, like Gecko) Version/4.0.5 Mobile/8A306 Safari/6531.22.7",
        "Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_0 like Mac OS X; en-us) AppleWebKit/532.9 (KHTML, like Gecko) Version/4.0.5 Mobile/8A293 Safari/6531.22.7",
        "Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3_1 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8G4 Safari/6533.18.5",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 5_1_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9B206 Safari/7534.48.3",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A403 Safari/8536.25",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 6_1_2 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10B146 Safari/8536.25",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 7_0 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) Version/7.0 Mobile/11A465 Safari/9537.53",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 7_0_2 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) Version/7.0 Mobile/11A501 Safari/9537.53",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 7_1 like Mac OS X) AppleWebKit/537.51.2 (KHTML, like Gecko) Version/7.0 Mobile/11D167 Safari/9537.53",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/600.1.3 (KHTML, like Gecko) Version/8.0 Mobile/12A4345d Safari/600.1.4",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 9_3_5 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13G36 Safari/601.1",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E277 Safari/602.1",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Mobile/16A366 Safari/604.1",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 13_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0 Mobile/15E148 Safari/604.1"
    ]

    # Java Island bounds only
    longitudes = (104.5, 114.0)
    latitudes = (-8.8, -5.5)


    ios_version = random.choice(ios_versions)

    fingerprint = {
        "device_manufacturer": "Apple",
        "timezone": "Asia/Jakarta",
        "location_longitude": str(random.uniform(*longitudes)),
        "location_latitude": str(random.uniform(*latitudes)),
        "idfa": str(uuid.uuid4()).upper(),
        "is_emulator": False,
        "unique_id": str(uuid.uuid4()).upper(),
        "access_type": 1,
        "device_system": "iOS",
        "device_model": "iPhone",
        "is_tablet": False,
        "user_agent": random.choice(user_agents),
        "is_jailbroken_rooted": False,
        "screen_resolution": random.choice(screen_resolutions),
        "versionName": f"2.{random.randint(300, 350)}.{random.randint(0, 9)}",
        "current_os": ios_version,
        "language": "id",
        "device_name": random.choice(iphone_models)
    }

    json_str = json.dumps(fingerprint)
    b64_str = base64.b64encode(json_str.encode("utf-8")).decode("utf-8")

    return random.choice(user_id), b64_str





#######################################




from curl_cffi import requests
import logging
import traceback
import json


logger = setup_custom_logging()

def product_details_extractor(json_data):
    pdp = json_data.get("data", {}).get("pdpGetLayout", {})
    components = pdp.get("components", [])

    def find_component(name):
        for c in components:
            if c.get("name") == name:
                return c.get("data", [])
        return []

    product_content = find_component("product_content")
    product_content = product_content[0] if product_content else {}
    product_media_raw = find_component("product_media")
    product_media_raw = product_media_raw[0].get("media", []) if product_media_raw else []
    basic_info = pdp.get("basicInfo", {})
    product_url = basic_info.get("url", "")
    product_media = [
        ProductMedia(
            original=media.get("URLOriginal", ""),
            thumbnail=media.get("URLThumbnail", ""),
            max_res=media.get("URLMaxRes", ""),
        )
        for media in product_media_raw
    ]

    product_option = []
    variants = []
    mini_variant = find_component("mini_variant_options")
    if mini_variant:
        mini_variant = mini_variant[0] if mini_variant else {}
        for option in mini_variant.get('variants', []):
            option_id = int(option.get('productVariantID', 0) or 0)
            option_name = option.get('name', '')
            option_child = [x.get('value', '') for x in option.get('option', [])]
            product_option.append(ProductOption(
                option_id=option_id,
                option_name=option_name,
                option_child=option_child
            ))

        for child in mini_variant.get("children", []):
            variants.append(
                ProductVariant(
                    option_ids=child.get("optionID", []),
                    option_name=child.get('productName', ""),
                    option_url=child.get('productURL', ""),
                    price=child.get("price", 0),
                    price_string=child.get("priceFmt", ""),
                    discount=child.get('discPercentage', ""),
                    image_url=child.get("picture", {}).get("url", ""),
                    stock=child.get("stock", {}).get('stock', None),
                )
            )

    description = None
    description_element = find_component('product_detail')
    if description_element is not None and isinstance(description_element, list) and len(description_element) > 0:
        content = description_element[0].get('content')
        if content is not None and isinstance(content, list):
            for line in content:
                if isinstance(line, dict) and line.get('key') == 'deskripsi':
                    description = line.get('subtitle', '')
                    break

    pdpdSession = pdp.get('pdpSession')
    shop_type = json.loads(pdpdSession).get('stier', {}) if pdpdSession else None

    return ProductData(
        product_id=basic_info.get('productID'),
        product_sku = basic_info.get("ttsSKUID"),
        product_name=product_content.get("name", ""),
        url=product_url,
        main_image=basic_info.get("defaultMediaURL"),
        status=basic_info.get("status", ""),
        description=description,
        price=product_content.get("price", {}).get("value", 0),
        price_text=product_content.get("price", {}).get("priceFmt", ""),
        price_original=product_content.get("price", {}).get("slashPriceFmt", ""),
        discount_percentage=product_content.get("price", {}).get("discPercentage", ""),
        weight=int(basic_info.get("weight", 0) or 0),
        weight_unit=basic_info.get("weightUnit", ""),
        product_media=product_media,
        sold_count=int(basic_info.get("txStats", {}).get("countSold", 0) or 0),
        rating=float(basic_info.get("stats", {}).get("rating", 0) or 0),
        review_count=int(basic_info.get("stats", {}).get("countReview", 0) or 0),
        discussion_count=int(basic_info.get("stats", {}).get("countTalk", 0) or 0),
        total_stock=int(basic_info.get("totalStockFmt", "0").replace(".", "") or 0),
        etalase=basic_info.get("menu", {}).get("name", ""),
        etalase_url=basic_info.get("menu", {}).get("url", ""),
        category=basic_info.get("category", {}).get("name", ""),
        sub_category=[d.get("name", "") for d in basic_info.get("category", {}).get("detail", [])],
        product_option=product_option,
        variants=variants,
        shop=TokopaediShop(
            shop_id=int(basic_info.get("shopID", 0) or 0),
            name=basic_info.get("shopName", ""),
            city=basic_info.get('shopMultilocation', {}).get('cityName', ""),
            url='/'.join(product_url.split('/')[:-1]),
            shop_type=shop_resolver(shop_type)
        )
    )

def parse_tokped_url(url):
    temp = url.split('?')[0]
    temp = url.split('tokopedia.com/')[1].split('/')
    shop_id = temp[0] if len(temp) > 0 else ""
    product_key = temp[1] if len(temp) > 1 else ""
    return shop_id, product_key

def get_product(product_id=None, url=None, debug=False):
    assert url or product_id
    user_id, fingerprint = randomize_fp()
    if url:
        shop_id, product_key = parse_tokped_url(url)
        if not product_id:
            assert shop_id or product_key, "Failed to resolve product from URL"
    if product_id:
        product_id = str(product_id)
        shop_id, product_key = None, None

    headers = {
        'Host': 'gql.tokopedia.com',
        'Fingerprint-Data': fingerprint,
        'X-Tkpd-Userid': user_id,
        'X-Tkpd-Path': '/graphql/ProductDetails/getPDPLayout',
        'X-Method': 'POST',
        'Request-Method': 'POST',
        'X-Tkpd-Akamai': 'pdpGetLayout',
        'X-Device': 'ios-2.318.0',
        'Accept-Language': 'id;q=1.0, en;q=0.9',
        'User-Agent': 'Tokopedia/2.318.0 (com.tokopedia.Tokopedia; build:202505022018; iOS 18.5.0) Alamofire/2.318.0',
        'Content-Type': 'application/json; encoding=utf-8',
        'X-App-Version': '2.318.0',
        'Accept': 'application/json',
        'X-Theme': 'default',
        'X-Dark-Mode': 'false',
        'X-Price-Center': 'true',
    }

    json_data = {
        'variables': {
            'apiVersion': 1,
            'userLocation': {
                'addressID': '',
                'addressName': '',
                'receiverName': '',
                'postalCode': '',
                'districtID': '',
                'cityID': '',
                'latlon': '',
            },
            'tokonow': {
                'shopID': '0',
                'warehouses': [],
                'whID': '0',
                'serviceType': 'ooc',
            },
            'extParam': '',
            'productId': product_id if product_id else "",
            'shopDomain': shop_id if url else "",
            'productKey': product_key if url else "",
            'whID': '',
            'layoutID': '',
        },
        'query': 'query PDP_getPDPLayout($productId: String, $shopDomain: String, $productKey: String, $apiVersion: Float, $whID: String, $layoutID: String, $userLocation: pdpUserLocation, $extParam: String, $tokonow: pdpTokoNow) {\npdpGetLayout(productID: $productId, shopDomain: $shopDomain, productKey: $productKey, apiVersion: $apiVersion, whID: $whID, layoutID: $layoutID, userLocation: $userLocation, extParam: $extParam, tokonow: $tokonow) {\nrequestID\nname\npdpSession\nbasicInfo {\nproductID\ninitialVariantOptionID\ncategory {\nid\nname\ntitle\nbreadcrumbURL\nisAdult\nisKyc\ndetail {\nid\nname\nbreadcrumbURL\n}\nttsID\nttsDetail {\nid\nname\nbreadcrumbURL\n}\n}\nmenu {\nid\nname\nurl\n}\nshopID\nshopName\nalias\nminOrder\nmaxOrder\nurl\ncatalogID\nneedPrescription\nweight\nweightUnit\nstatus\ntxStats {\ntransactionReject\ntransactionSuccess\ncountSold\nitemSoldFmt\n}\nstats {\nrating\ncountTalk\ncountView\ncountReview\n}\ndefaultOngkirEstimation\nisTokoNow\ntotalStockFmt\nisGiftable\ndefaultMediaURL\nshopMultilocation {\ncityName\n}\nisBlacklisted\nblacklistMessage {\ntitle\ndescription\nbutton\n}\nweightWording\nttsPID\nttsSKUID\nttsShopID\n}\nadditionalData {\nfomoSocialProofs {\nname\ntext\nicons\ntypeIcon\nbackgroundColor\nposition\n}\n}\ncomponents {\nname\ntype\nkind\ndata {\n... on pdpDataComponentSocialProofV2 {\nsocialProofContent {\nsocialProofType\nsocialProofID\ntitle\nsubtitle\nicon\napplink {\nappLink\n}\nbgColor\nchevronColor\nshowChevron\nhasSeparator\n}\n}\n... on pdpDataProductMedia {\nmedia {\ntype\nURLOriginal\nURLThumbnail\ndescription\nvideoURLIOS\nisAutoplay\nindex\nvariantOptionID\nURLMaxRes\n}\nrecommendation{\nlightIcon\ndarkIcon\niconText\nbottomsheetTitle\nrecommendation\n}\nvideos {\nsource\nurl\n}\ncontainerType\nliveIndicator {\nisLive\nchannelID\nmediaURL\napplink\n}\nshowJumpToVideo\n}\n... on pdpDataProductContent {\nname\nprice {\nvalue\ncurrency\nlastUpdateUnix\npriceFmt\nslashPriceFmt\ndiscPercentage\ncurrencyFmt\nvalueFmt\n}\ncampaign {\ncampaignID\ncampaignType\ncampaignTypeName\npercentageAmount\noriginalPrice\ndiscountedPrice\noriginalStock\nstock\nstockSoldPercentage\nendDateUnix\nisActive\nhideGimmick\nisUsingOvo\ncampaignIdentifier\nbackground\npaymentInfoWording\nproductID\ncampaignLogo\nshowStockBar\n}\nthematicCampaign {\nproductID\ncampaignName\nbackground\nicon\ncampaignLogo\nsuperGraphicURL\n}\nstock {\nuseStock\nvalue\nstockWording\n}\nvariant {\nisVariant\n}\nwholesale {\nminQty\nprice {\nvalue\ncurrency\nlastUpdateUnix\n}\n}\nisFreeOngkir {\nisActive\nimageURL\n}\npreorder {\nduration\ntimeUnit\nisActive\npreorderInDays\n}\nisCashback {\npercentage\n}\nisTradeIn\nisOS\nisPowerMerchant\nisWishlist\nisCOD\nparentName\nisShowPrice\nlabelIcons {\niconURL\nlabel\n}\n}\n... on pdpDataProductInfo {\nrow\ncontent {\ntitle\nsubtitle\napplink\n}\n}\n... on pdpDataInfo {\ntitle\napplink\nisApplink\nicon\nlightIcon\ndarkIcon\ncontent {\nicon\ntext\n}\nseparator\n}\n... on pdpDataProductVariant {\nparentID\ndefaultChild\nsizeChart\nmaxFinalPrice\ncomponentType\nlandingSubText\nsocialProof {\nbgColor\ncontents {\nname\ncontent\niconURL\n}\n}\nvariants {\nproductVariantID\nvariantID\nname\nidentifier\noption {\nproductVariantOptionID\nvariantUnitValueID\nvalue\nhex\npicture {\nurl\nurl100\n}\n}\n}\nchildren {\nproductID\nprice\npriceFmt\nslashPriceFmt\ndiscPercentage\nsku\noptionID\nproductName\nproductURL\npicture {\nurl\nurl100\n}\nstock {\nstock\nisBuyable\nstockWording\nstockWordingHTML\nminimumOrder\nmaximumOrder\nstockFmt\nstockCopy\n}\nisCOD\nisWishlist\ncampaignInfo {\ncampaignID\ncampaignType\ncampaignTypeName\ndiscountPercentage\noriginalPrice\ndiscountPrice\nstock\nstockSoldPercentage\nendDateUnix\nappLinks\nisActive\nhideGimmick\nisUsingOvo\nminOrder\ncampaignIdentifier\nbackground\npaymentInfoWording\ncampaignLogo\nshowStockBar\n}\nthematicCampaign {\ncampaignName\nicon\nbackground\nproductID\ncampaignLogo\nsuperGraphicURL\n}\nsubText\npromo {\nvalue\niconURL\nproductID\npromoPriceFmt\nsubtitle\napplink\ncolor\nbackground\npromoType\nsuperGraphicURL\npriceAdditionalFmt\nseparatorColor\nbottomsheetParam\npromoCodes {\npromoID\npromoCode\npromoCodeType\n}\n}\ncurrencyFmt\nvaluePriceFmt\ncomponentPriceType\nisTopSold\nlabelIcons {\niconURL\nlabel\n}\nttsPID\nttsSKUID\n}\n}\n... on pdpDataCustomInfo {\nicon\ntitle\nisApplink\napplink\nseparator\ndescription\nlabel {\nvalue\ncolor\n}\nlightIcon\ndarkIcon\n}\n... on pdpDataComponentReviewV2 {\nmostHelpfulReviewParam {\nlimit\n}\n}\n... on pdpDataProductDetail {\ntitle\ncontent {\ntype\nkey\nextParam\naction\ntitle\nsubtitle\napplink\nshowAtFront\nshowAtBottomsheet\ninfoLink\nicon\n}\ncatalogBottomsheet {\nactionTitle\nbottomSheetTitle\nparam\n}\nbottomsheet {\nactionTitle\nbottomSheetTitle\nparam\n}\n}\n... on pdpDataOneLiner {\nproductID\noneLinerContent\nlinkText\napplink\nseparator\nisVisible\ncolor\nicon\neduLink {\nappLink\n}\n}\n... on pdpDataCategoryCarousel {\nlinkText\ntitleCarousel\napplink\nlist {\ncategoryID\nicon\ntitle\nisApplink\napplink\n}\n}\n... on pdpDataBundleComponentInfo {\ntitle\nwidgetType\nproductID\nwhID\n}\n... on pdpDataDynamicOneLiner {\nname\napplink\nseparator\nicon\nstatus\nchevronPos\ntext\nbgColor\nchevronColor\npadding {\nt\nb\n}\nimageSize {\nw\nh\n}\n}\n... on pdpDataComponentDynamicOneLinerVariant {\nname\napplink\nseparator\nicon\nstatus\nchevronPos\ntext\nbgColor\nchevronColor\npadding {\nt\nb\n}\nimageSize {\nw\nh\n}\n}\n... on pdpDataCustomInfoTitle {\ntitle\nstatus\ncomponentName\n}\n... on pdpDataProductDetailMediaComponent {\ntitle\ndescription\ncontentMedia {\nurl\nratio\ntype\n}\nshow\nctaText\n}\n... on pdpDataOnGoingCampaign {\ncampaign {\ncampaignID\ncampaignType\ncampaignTypeName\npercentageAmount\noriginalPrice\ndiscountedPrice\noriginalStock\nstock\nstockSoldPercentage\nendDateUnix\nisActive\nhideGimmick\nisUsingOvo\ncampaignIdentifier\nbackground\npaymentInfoWording\nproductID\ncampaignLogo\nshowStockBar\n}\nthematicCampaign {\nproductID\ncampaignName\nbackground\nicon\ncampaignLogo\nsuperGraphicURL\n}\n}\n... on pdpDataProductListComponent {\nthematicID\nqueryParam\n}\n... on pdpDataComponentPromoPrice {\nprice {\nvalue\ncurrency\nlastUpdateUnix\npriceFmt\nslashPriceFmt\ndiscPercentage\ncurrencyFmt\nvalueFmt\n}\npromo {\nvalue\niconURL\nproductID\npromoPriceFmt\nsubtitle\napplink\ncolor\nbackground\npromoType\nsuperGraphicURL\npriceAdditionalFmt\nseparatorColor\nbottomsheetParam\npromoCodes {\npromoID\npromoCode\npromoCodeType\n}\n}\ncomponentPriceType\n}\n... on pdpDataComponentSDUIDivKit {\ntemplate\n}\n... on pdpDataComponentShipmentV4 {\ndata {\nproductID\nwarehouse_info {\nwarehouse_id\nis_fulfillment\ndistrict_id\npostal_code\ngeolocation\ncity_name\nttsWarehouseID\n}\nuseBOVoucher\nisCOD\nmetadata\n}\n}\n... on pdpDataComponentShipmentV5 {\ndata {\nproductID\nwarehouse_info {\nwarehouse_id\nis_fulfillment\ndistrict_id\npostal_code\ngeolocation\ncity_name\nttsWarehouseID\n}\nuseBOVoucher\nisCOD\nmetadata\n}\n}\n...on pdpDataAffordabilityGroupLabel {\naffordabilityData{\nproductID\nproductVouchers {\nidentifier\ntype\ntext\nbackgroundColor\n}\nshowChevron\nchevronColor\nappliedVoucherTypeIDs\n}\n}\n}\n}\n}\n}',
    }

    try:
        response = requests.post(
            'https://gql.tokopedia.com/graphql/ProductDetails/getPDPLayout',
            headers=headers,
            json=json_data,
            verify=False,
        )
        result_json = response.json()
        product_data = product_details_extractor(result_json)
        if debug:
            logger.detail(f"{product_data.product_id} - {product_data.product_name[0:40]}...")
        return product_data
    except Exception as e:
        print(traceback.format_exc())
        exit()
     
        
     


from curl_cffi import requests
import logging
import traceback

logger = setup_custom_logging()

def extract_reviews(json_data):
    reviews = []
    
    data = json_data.get("data", {})
    productrev_list = data.get("productrevGetProductReviewList", {})
    items = productrev_list.get("list", [])
    
    if not items:
        return reviews

    for item in items:
        images = item.get("imageAttachments", [])
        videos = item.get("videoAttachments", [])
        like_dislike = item.get("likeDislike", {})
        user = item.get("user", {})
        review_response = item.get("reviewResponse", {})

        review = ProductReview(
            feedback_id=int(item.get("feedbackID", 0)),
            variant_name=item.get("variantName", ""),
            message=item.get("message", ""),
            rating=float(item.get("productRating", 0)),
            review_age=item.get("reviewCreateTimestamp", ""),
            user_full_name=user.get("fullName", ""),
            user_url=user.get("url", ""),
            response_message=review_response.get("message", ""),
            response_created_text=review_response.get("createTime", ""),
            images=[img.get("imageUrl", "") for img in images],
            videos=[v for v in videos],
            likes=like_dislike.get("totalLike", 0),
        )
        reviews.append(review)

    return reviews

def get_reviews(product_id=None, url=None, max_result=10, page=1, result_count=0, debug=False):
    assert product_id or url, "You must provide either 'product_id' or 'url' to fetch reviews."
    user_id, fingerprint = randomize_fp()
    if url:
        ''' Resolve product_id from url using get_product '''
        product_detail = get_product(url=url)
        if product_detail:
            product_id = product_detail.product_id
            assert product_id, "Failed to resolve product_id from URL"

    headers = {
        'Host': 'gql.tokopedia.com',
        'Fingerprint-Data': fingerprint,
        'X-Tkpd-Userid': user_id,
        'X-Tkpd-Path': '/graphql/ProductReview/getProductReviewReadingList',
        'X-Device': 'ios-2.318.0',
        'Request-Method': 'POST',
        'X-Method': 'POST',
        'Accept-Language': 'id;q=1.0, en;q=0.9',
        'User-Agent': 'Tokopedia/2.318.0 (com.tokopedia.Tokopedia; build:202505022018; iOS 18.5.0) Alamofire/2.318.0',
        'Content-Type': 'application/json; encoding=utf-8',
        'X-App-Version': '2.318.0',
        'Accept': 'application/json',
        'X-Dark-Mode': 'true',
        'X-Theme': 'default',
        'X-Price-Center': 'true',
    }

    json_data = {
        'query': 'query productrevGetProductReviewList($productID: String!, $page: Int!, $limit: Int!, $sortBy: String,\n$filterBy: String, $opt: String) {\nproductrevGetProductReviewList(productID: $productID, page: $page, limit: $limit, sortBy: $sortBy,\nfilterBy: $filterBy, opt: $opt) {\nlist {\nfeedbackID\nvariantName\nmessage\nproductRating\nreviewCreateTime\nreviewCreateTimestamp\nisAnonymous\nisReportable\nreviewResponse {\nmessage\ncreateTime\n}\nuser {\nuserID\nfullName\nimage\nurl\nlabel\n}\nimageAttachments {\nattachmentID\nimageThumbnailUrl\nimageUrl\n}\nvideoAttachments {\nattachmentID\nvideoUrl\n}\nlikeDislike {\ntotalLike\nlikeStatus\n}\nstats {\nkey\nformatted\ncount\n}\nbadRatingReasonFmt\n}\nshop {\nshopID\nname\nurl\nimage\n}\nvariantFilter {\nisUnavailable\nticker\n}\nhasNext\n}\n}',
        'variables': {
            'productID': str(product_id),
            'page': page,
            'filterBy': '',
            'opt': '',
            'limit': 10,
            'sortBy': 'informative_score desc',
        },
    }

    try:
        response = requests.post(
            'https://gql.tokopedia.com/graphql/ProductReview/getProductReviewReadingList',
            headers=headers,
            json=json_data
        )
        result_json = response.json()
        has_next = result_json.get('data', {}).get('productrevGetProductReviewList', {}).get('hasNext', False)
        current_result =  extract_reviews(result_json)
        if current_result:

            # Debug
            if debug:
                for line in current_result:
                    review_message = line.message.replace('\n','')[0:40]
                    logger.reviews(f"{line.feedback_id} - {review_message}...")

            result_count += len(current_result)
            if result_count >= max_result:
                return current_result

            next_result = get_reviews(
                    product_id = str(product_id) if product_id else None,
                    url = url if url else None,
                    max_result = max_result,
                    page = page+1,
                    result_count = result_count,
                    debug = debug
                )
            return current_result+next_result
        return current_result
    except:
        print(traceback.format_exc())
        return None


        
from curl_cffi import requests
import json
import traceback
from urllib.parse import quote, parse_qs, urlencode
import logging
import logging
from dataclasses import dataclass
from typing import Optional


logger = setup_custom_logging()


def search_extractor(result):
    if result['products']:
        product_result = []
        for product in result['products']:
            price_data = product.get('price',{})
            shop_info = product.get('shop')

            product_id = product.get('id')
            product_sku = product.get('stock', {}).get('ttsSKUID') 
            name = product.get('name')
            category = product.get('category',{}).get('name')
            url = product.get('url')
            sold_count = product.get('stock',{}).get('sold')
            price_original = price_data.get('original')
            price = price_data.get('number')
            price_text = price_data.get('text')
            rating = float(product.get('rating')) if product.get('rating') else None
            main_image = product.get('mediaURL',{}).get('image700')

            shop_id = shop_info.get('id')
            shop_name = shop_info.get('name')
            city = shop_info.get('city')
            shop_url = shop_info.get('url')
            shop_type = str(product.get('badge',{}).get('url'))

            product_result.append(ProductData(
                    product_id=product_id,
                    product_sku=product_sku,
                    product_name=name,
                    category=category,
                    url=url,
                    sold_count=sold_count,
                    price_original=price_original,
                    price=price,
                    price_text=price_text,
                    rating=rating,
                    main_image=main_image,
                    shop=TokopaediShop(
                            shop_id=shop_id,
                            name=shop_name,
                            city=city,
                            url=shop_url,
                            shop_type=shop_resolver(shop_type)
                        )
                ))
        return product_result
    else:
        return []

def dedupe(items):
    if not items:
        return SearchResults()
    return SearchResults(list({item.product_id: item for item in items}.values()))

def filters_to_query(filters) -> str:
    filter_dict = {k: v for k, v in vars(filters).items() if v is not None}
    return "&".join(f"{k}={quote(str(v), safe=',')}" for k, v in filter_dict.items())

def merge_params(original, additional=None):
    original_dict = {k: v[0] for k, v in parse_qs(original).items()}
    if additional:
        additional_dict = {k: v[0] for k, v in parse_qs(additional).items()}
    else:
        additional_dict = {}

    merged = {**original_dict, **additional_dict}

    return "&".join(f"{k}={quote(str(v), safe=',')}" for k, v in merged.items())

def search(keyword="zenbook 14 32gb", max_result=100, result_count=0, base_param=None, next_param=None, filters=None, debug=False):
    user_id, fingerprint = randomize_fp()
    headers = {
        'Host': 'gql.tokopedia.com',
        'Os_type': '2',
        'Fingerprint-Data': fingerprint,
        'X-Tkpd-Userid': user_id,
        'X-Tkpd-Path': '/graphql/SearchResult/getProductResult',
        'X-Method': 'POST',
        'X-Device': 'ios-2.318.0',
        'Request-Method': 'POST',
        'Accept-Language': 'id;q=1.0, en;q=0.9',
        'Content-Type': 'application/json; encoding=utf-8',
        'User-Agent': 'Tokopedia/2.318.0 (com.tokopedia.Tokopedia; build:202505022018; iOS 18.5.0) Alamofire/2.318.0',
        'Date': 'Sun, 29 Jun 2025 14:44:51 +0700',
        'X-App-Version': '2.318.0',
        'Accept': 'application/json',
        'X-Dark-Mode': 'false',
        'X-Theme': 'default',
        'Tt-Request-Time': '1751183091059',
        'X-Price-Center': 'true',
        'Device-Type': 'iphone',
        'Bd-Device-Id': '7132999401249080838',
    }

    if not base_param:
        base_param = f'user_warehouseId=0&user_shopId=0&user_postCode=10110&srp_initial_state=false&breadcrumb=true&ep=product&user_cityId=0&q={quote(keyword)}&related=true&source=search&srp_enter_method=normal_search&enter_method=normal_search&l_name=sre&user_districtId=0&srp_feature_id=&catalog_rows=0&page=1&srp_component_id=02.01.00.00&ob=0&srp_sug_type=&src=search&with_template=true&show_adult=false&srp_direct_middle_page=false&channel=product%20search&rf=false&navsource=home&use_page=true&dep_id=&device=ios'

    if filters:
        base_param = merge_params(base_param, filters_to_query(filters))

    json_data = {
        'query': 'query Search_SearchProduct($params: String!, $query: String!) {\n global_search_navigation(keyword: $query, size: 5, device: \"ios\", params: $params){\n data {\n source\n keyword\n title\n nav_template\n background\n see_all_applink\n show_topads\n info\n list {\n category_name\n name\n info\n image_url\n subtitle\n strikethrough\n background_url\n logo_url\n applink\n component_id\n }\n component_id\n tracking_option\n }\n }\n searchInspirationCarouselV2(params: $params){\n process_time\n data {\n title\n type\n position\n layout\n tracking_option\n color\n options {\n title\n subtitle\n icon_subtitle\n applink\n banner_image_url\n banner_applink_url\n identifier\n meta\n component_id\n card_button {\n  title\n  applink\n }\n bundle {\n  shop {\n  name\n  url\n  }\n  count_sold\n  price\n  original_price\n  discount\n  discount_percentage\n }\n  product {\n id\n ttsProductID\n name\n price\n price_str\n image_url\n rating\n count_review\n applink\n description\n original_price\n discount\n discount_percentage\n rating_average\n badges {\n title\n image_url\n show\n }\n shop {\n id\n name\n city\n ttsSellerID\n }\n label_groups {\n position\n title\n type\n url\n styles {\n key\n value\n }\n }\n freeOngkir {\n isActive\n image_url\n }\n ads {\n id\n productClickUrl\n productWishlistUrl\n productViewUrl\n }\n wishlist\n component_id\n customvideo_url\n label\n bundle_id\n parent_id\n min_order\n category_id\n stockbar {\n percentage_value\n value\n color\n ttsSkuID\n }\n warehouse_id_default\n sold\n }\n }\n }\n }\n searchInspirationWidget(params: $params){\n data {\n title\n header_title\n header_subtitle\n type\n position\n layout\n options {\n text\n img\n color\n applink\n multi_filters{\n  key\n  name\n  value\n  val_min\n  val_max\n }\n component_id\n }\n tracking_option\n input_type\n }\n }\n productAds: displayAdsV3(displayParams: $params) {\n status {\n error_code\n message\n }\n header {\n process_time\n total_data\n }\n data{\n id\n ad_ref_key\n redirect\n sticker_id\n sticker_image\n product_click_url\n product_wishlist_url\n shop_click_url\n tag\n creative_id\n log_extra\n product{\n id\n tts_product_id\n tts_sku_id\n parent_id\n name\n wishlist\n image{\n  m_url\n  s_url\n  xs_url\n  m_ecs\n  s_ecs\n  xs_ecs\n }\n uri\n relative_uri\n price_format\n price_range\n campaign {\n  discount_percentage\n  original_price\n }\n wholesale_price {\n  price_format\n  quantity_max_format\n  quantity_min_format\n }\n count_talk_format\n count_review_format\n category {\n  id\n }\n category_breadcrumb\n product_preorder\n product_wholesale\n product_item_sold_payment_verified\n free_return\n product_cashback\n product_new_label\n product_cashback_rate\n product_rating\n product_rating_format\n labels {\n  color\n  title\n }\n free_ongkir {\n  is_active\n  img_url\n }\n label_group {\n  position\n  type\n  title\n  url\n  style {\n  key\n  value\n  }\n }\n top_label\n bottom_label\n product_minimum_order\n customvideo_url\n }\n shop{\n id\n tts_seller_id\n name\n domain\n location\n city\n gold_shop\n gold_shop_badge\n lucky_shop\n uri\n shop_rating_avg\n owner_id\n is_owner\n badges{\n  title\n  image_url\n  show\n }\n }\n applinks\n }\n template {\n is_ad\n }\n }\n searchProductV5(params: $params) {\n header {\n totalData\n responseCode\n keywordProcess\n keywordIntention\n componentID\n meta {\n productListType\n hasPostProcessing\n hasButtonATC\n dynamicFields\n }\n isQuerySafe\n additionalParams\n autocompleteApplink\n backendFilters\n backendFiltersToggle\n }\n data {\n totalDataText\n banner {\n position\n text\n applink\n imageURL\n componentID\n trackingOption\n }\n redirection {\n applink\n }\n related {\n relatedKeyword\n position\n trackingOption\n otherRelated {\n  keyword\n  applink\n  componentID\n  products {\n  id\n  name\n  applink\n  mediaURL {\n  image\n  }\n  shop {\n  name\n  city\n  }\n  badge {\n  title\n  url\n  }\n  price {\n  text\n  number\n  }\n  freeShipping {\n  url\n  }\n  labelGroups {\n  id\n  position\n  title\n  type\n  url\n  styles {\n  key\n  value\n  }\n  }\n  rating\n  wishlist\n  ads {\n  id\n  productClickURL\n  productViewURL\n  productWishlistURL\n  }\n  meta {\n  parentID\n  warehouseID\n  componentID\n  isImageBlurred\n  }\n  }\n }\n }\n suggestion {\n currentKeyword\n suggestion\n query\n text\n componentID\n trackingOption\n }\n ticker {\n id\n text\n query\n applink\n componentID\n trackingOption\n }\n violation {\n headerText\n descriptionText\n imageURL\n ctaApplink\n buttonText\n buttonType\n }\n products {\n id\n ttsProductID\n name\n url\n applink\n mediaURL {\n  image\n  image300\n  image500\n  image700\n  videoCustom\n }\n shop {\n  id\n  name\n  url\n  city\n  ttsSellerID\n }\n badge {\n  title\n  url\n }\n price {\n  text\n  number\n  range\n  original\n  discountPercentage\n }\n freeShipping {\n  url\n }\n labelGroups {\n  id\n  position\n  title\n  type\n  url\n  styles {\n  key\n  value\n  }\n }\n labelGroupsVariant {\n  title\n  type\n  typeVariant\n  hexColor\n }\n category {\n  id\n  name\n  breadcrumb\n  gaKey\n }\n rating\n wishlist\n ads {\n  id\n  productClickURL\n  productViewURL\n  productWishlistURL\n  tag\n  creativeID\n  logExtra\n }\n meta {\n  parentID\n  warehouseID\n  isPortrait\n  isImageBlurred\n  dynamicFields\n }\n stock {\n  sold\n  ttsSKUID\n }\n }\n shopWidget {\n headline {\n  badge {\n  url\n  }\n  shop {\n  id\n  imageShop {\n  sURL\n  }\n  City\n  name\n  ratingScore\n  ttsSellerID\n  products {\n  id\n  ttsProductID\n  name\n  applink\n  mediaURL {\n  image300\n  }\n  price {\n  text\n  original\n  discountPercentage\n  }\n  freeShipping {\n  url\n  }\n  labelGroups {\n  position\n  title\n  type\n  styles {\n   key\n   value\n  }\n  url\n  }\n  rating\n  meta {\n  parentID\n  dynamicFields\n  }\n  shop {\n  ttsSellerID\n  }\n  stock {\n  ttsSKUID\n  }\n  }\n  }\n }\n meta {\n  applinks\n }\n }\n filters {\n title\n template_name: templateName\n isNew\n subTitle: subtitle\n search: searchInfo {\n  searchable\n  placeholder\n }\n options {\n  name\n  key\n  value\n  icon\n  isPopular\n  isNew\n  hexColor\n  inputType\n  valMin\n  valMax\n  Description: description\n  child {\n  name\n  key\n  value\n  isPopular\n  child {\n  name\n  key\n  value\n  }\n  }\n }\n }\n quickFilters {\n title\n chip_name: chipName\n options {\n  name\n  key\n  value\n  icon\n  is_popular: isPopular\n  is_new: isNew\n  hex_color: hexColor\n  input_type: inputType\n  image_url_active: imageURLActive\n  image_url_inactive: imageURLInactive\n }\n }\n sorts {\n name\n key\n value\n }\n }\n }\n fetchLastFilter(param: $params) {\n data {\n title\n description\n category_id_l2\n applink\n tracking_option\n filters {\n title\n key\n name\n value\n }\n component_id\n }\n }\n }',
        'variables': {
            'params': base_param,
            'query': keyword,
        },
    }

    if next_param:
        params = merge_params(base_param, next_param)
        json_data['variables']['params'] = params

    try:
        response = requests.post(
            'https://gql.tokopedia.com/graphql/SearchResult/getProductResult',
            headers=headers,
            json=json_data,
            verify=False,
        )

        if 'searchProductV5' in response.text:
            result = response.json()['data']['searchProductV5']['data']
            result = SearchResults(search_extractor(result))
            if result:
                result_count += len(result)
                if debug:
                    for line in result:
                        logger.search(f'{line.product_id} - {line.product_name[0:40]}...')
                if result_count >= max_result:
                    return dedupe(result)

                next_param = response.json()['data']['searchProductV5']['header']['additionalParams']
                next_result = search(
                    keyword=keyword,
                    max_result=max_result,
                    result_count=result_count,
                    base_param=base_param,
                    next_param = next_param,
                    debug = debug
                )
                return dedupe(result+next_result)

        return dedupe(result)
    except:
        print(traceback.format_exc())
        return None
    
"""    
filters = SearchFilters(
            bebas_ongkir_extra = True,
            pmin = 15000000,
            pmax = 25000000,
            rt = 4.5
        )
"""
#results = search("Asus Zenbook S14 32GB", max_result=5, debug=True)

results = search("ladies shoes", max_result=50, debug=True)


#results = search("Asus Zenbook S14 32GB", max_result=100, debug=True, filters=filters)
results.enrich_details(debug=True)
#results.enrich_reviews(max_result=5, debug=True)

df = pd.json_normalize(results.json())

with open('result.json','w') as f:
    f.write(json.dumps(results.json(), indent=4))

''' Get individual product info '''
#results2 = get_product(url='https://www.tokopedia.com/wd-official/wd-my-passport-ultra-6tb-hd-hdd-hardisk-eksternal-external-2-5-usb-c-usb-a-biru-c0f1c?extParam=whid%3D19486', debug=True)
results2 = get_product(url='https://www.tokopedia.com/rowey/rowey-sepatu-balet-wanita-flat-shoes-ballerina-sepatu-flat-wanita-layla-1732453439147246903?extParam=src%3Dshop%26whid%3D16229270&aff_unique_id=&channel=others&chain_key=', debug=True)


#results = get_product(url='https://www.tokopedia.com/larocheposayofficial/la-roche-posay-pure-vit-c-eye-yeux-cream-15ml?source=homepage.top_carousel.0.38456', debug=True)
#results.enrich_reviews(debug=True)
print(json.dumps(results.json(), indent=4))

with open('results.json','w') as f:
    f.write(json.dumps(results.json(), indent=4))
    
