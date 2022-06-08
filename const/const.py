CUSTOMER_CHANNEL_ID = '@wb_sales_test'

MPSTATS_MAIN_PAGE_URL = 'https://mpstats.io/'
MPSTATS_SKU_URL = 'https://mpstats.io/wb/bysearch'
MPSTATS_SEO_URL = 'https://mpstats.io/api/seo/keywords/expanding'
MPSTATS_TRENDS_URL = 'https://mpstats.io/api/wb/get/category/trends'
MPSTATS_PRICE_SEGMENTATION_URL = 'https://mpstats.io/api/wb/get/category/price_segmentation'
MPSTATS_SALES_URL = 'https://mpstats.io/api/wb/get/item/ARTICLE/by_category'

COOKIES_PART = '_ym_uid=1651240592234847018; _ym_d=1651240592; ' \
    '_ga=GA1.1.2054104203.1651240592; _ym_isad=2; ' \
    'supportOnlineTalkID=r85EpoyBIxTRA3agMH9GXs5yZQOApJun; ' \
    '_ym_hostIndex=0-3%2C1-0; _ym_visorc=w; ' \
    'userlogin=a%3A2%3A%7Bs%3A3%3A%22lgn%22%3Bs%3A29%3A%22ip.' \
    'evgeniy.bogdanov%40gmail.com%22%3Bs%3A3%3A%22pwd%22%3Bs%' \
    '3A32%3A%2299fa197de27558f79782ea8373471beb%22%3B%7D; ' \
    '_ga_8S8Y1X62NG=GS1.1.1651240592.1.1.1651240652.0'

MPSTATS_TRENDS = {'Число продаж': 'sales',
                  'Суммарная выручка в рубрике': 'revenue',
                  'Число товаров': 'items',
                  'Товаров с продажами': 'items_with_sells',
                  'Число брендов': 'brands',
                  'Брендов с продажами': 'brands_with_sells',
                  'Число продавцов': 'sellers',
                  'Продавцов с продажами': 'sellers_with_sells',
                  'Выручка на товар': 'product_revenue',
                  'Cредний чек': 'average_order_value'}

MPSTATS_SECTIONS = {'По товарам в категории': 'itemsInCategory',
                    'По категории': 'category'}

WB_HINTS_URL = 'https://suggestions.wildberries.ru/api/v2/hint'
WB_SEARCH_URL = 'https://wbxsearch.wildberries.ru/exactmatch/v2/common'

ENDINGS_FOR_WORD_USER = {1: 'ь', 2: 'я', 3: 'я', 4: 'я', 5: 'ей',
                         6: 'ей', 7: 'ей', 8: 'ей', 9: 'ей', 0: 'ей'}

INLINE_CATS_COUNT_PER_PAGE = 7
