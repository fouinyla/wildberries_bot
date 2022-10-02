CUSTOMER_CHANNEL_ID = '@opt_tyrke'

MPSTATS_MAIN_PAGE_URL = 'https://mpstats.io/'
MPSTATS_SKU_URL = 'https://mpstats.io/wb/bysearch'
MPSTATS_SEO_URL = 'https://mpstats.io/api/seo/keywords/expanding'
MPSTATS_TRENDS_URL = 'https://mpstats.io/api/wb/get/category/trends'
MPSTATS_PRICE_SEGMENTATION_URL = 'https://mpstats.io/api/wb/get/category/price_segmentation'
MPSTATS_SALES_URL = 'https://mpstats.io/api/wb/get/item/ARTICLE/by_keywords'

COOKIES_PART = 'tmr_reqNum=21; tmr_detect=0%7C1664710499716; supportOnlineTalkID=CLBFGobV' \
               'EM8St3UaTzzGTxcOvpAqcAQD; _comagic_id5brIg=5703612438.8569687065.1664710369' \
               '; _ga=GA1.1.820842487.1664644592; _ga_8S8Y1X62NG=GS1.1.1664710362.3.1.16647' \
               '10497.0.0.0; _ym_visorc=b; popmechanic_sbjs_migrations=popmechanic_14184743' \
               '75998%3D1%7C%7C%7C1471519752600%3D1%7C%7C%7C1471519752605%3D1; tmr_lvid=3f5' \
               'a0166ad465f9bd1d7b40209b72030; tmr_lvidTS=1664644592457; _gr_session=%7B%22s' \
               '_id%22%3A%22e41f91d4-52d3-439c-a1de-7f8ccabbcf1c%22%2C%22s_time%22%3A1664710' \
               '497262%7D; _mpsuid=21197ff06ab8f2c1a424e9d26d0115ac; userlogin=a%3A2%3A%7Bs%3' \
               'A3%3A%22lgn%22%3Bs%3A29%3A%22ip.evgeniy.bogdanov%40gmail.com%22%3Bs%3A3%3A%22' \
               'pwd%22%3Bs%3A32%3A%2299fa197de27558f79782ea8373471beb%22%3B%7D; _cmg_csst5brI' \
               'g=1664710365; __lhash_=8100f13f404b5dfe21de0380953110d2; _ym_isad=2; _ym_d=16' \
               '64644591; _ym_uid=1664644591509828735; directCrm-session=%7B%22deviceGuid%22%' \
               '3A%2293cc2701-545a-429b-a612-7a65f49c1124%22%7D; mindboxDeviceUUID=93cc2701-54' \
               '5a-429b-a612-7a65f49c1124; mpgd=1664644585.60086208.59765316'

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


WB_HINTS_URL = 'https://search.wb.ru/suggests/api/v2/hint'
WB_CARD_SEARCH_URL = 'https://suppliers-api.wildberries.ru/card/list'
WB_CARD_UPDATE_URL = 'https://suppliers-api.wildberries.ru/card/update'

ENDINGS_FOR_WORD_USER = {1: 'ь', 2: 'я', 3: 'я', 4: 'я', 5: 'ей',
                         6: 'ей', 7: 'ей', 8: 'ей', 9: 'ей', 0: 'ей'}

INLINE_CATS_COUNT_PER_PAGE = 7
