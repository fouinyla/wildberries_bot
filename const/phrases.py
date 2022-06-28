def phrase_for_start_first_greeting(data):
    return f"Hello, {data['user_name']}!"


def phrase_for_answer_to_main_menu_buttons(data):
    return f"You pressed {data['button_title']}"


def phrase_for_notify_admins_about_some_event(data):
    return f"""❗️{data['user_name']} {data['user_nickname']} что-то сделал в 
    {data['weekday']} <b> {data['date']} </b> в <b> {data['time']}"""


def phrase_for_categories_inline_keyboard(data):
    return "По какой категории собрать данные?\nКатегория: " + data["category"] + "\nСтраница: " + str(data["current_page"]) + " из " + str(data["total_page"])


def phrase_for_categories_inline_keyboard_final(data):
    return f"Вы выбрали <b>{data['category']}</b> категорию"


def phrase_service_unavailable():
    return 'Бот временно недоступен. Попробуйте другой запрос (функцию) или повторите попытку через некоторое время.'


FAQ = ('<b>ИНСТРУКЦИЯ:</b>\n\n1. Выберите команду «Поисковой запрос» и введите название товара, '
       'по которому хотите собрать SEO-ядро. Robot подтянет с Wildberries все самые популярные запросы '
       'на данный момент и напишет их в чат.\n\n<b>Например, на запрос «Футболка»</b>, Robot '
       'выведет следующие популярные запросы на WB:\nфутболка женская\nфутболка мужская\nфутболка женская '
       'оверсайз\nфутболка оверсайз\nфутболка для девочки одежда\nфутболка мужская хлопок\n\n'
       '<b>Далее, вы можете выбрать подходящие для вашего товара запросы из предложенных и '
       'воспользоваться ещё раз функцией «поисковой запрос»\n\nНапример, на запрос «футболка оверсайз»</b> '
       'Robot предложит следующие популярные запросы на WB:\nфутболка оверсайз с принтом\n'
       'футболка оверсайз подросток\nфутболка оверсайз женская большой размер\nфутболка оверсайз длинная\n'
       'футболка оверсайз для девочек с рисунком\nфутболка оверсайз домашняя\n\n'
       '2. Получив все популярные запросы, вы можете выбрать подходящие и перейти к следующему шагу - «Сбор SEO ядра». '
       'Введите выбранные запросы из предыдущего шага\n\n<b>Готово</b> ✅\n'
       'Оптимизируйте свою карточку, исходя из данных, предоставленных Robotom\n\n<b>Желаем хороших продаж, с уважением, команда</b>')


CARD_POSITION_TEXT = '<b>Узнай, на каких позициях находится ' \
                     'твой товар в поисковой выдаче Wildberries</b>\n\n' \
                     'Введи через пробел артикул и запрос, которые тебя интересуют. ' \
                     'Например, <b>14134148 фитнес-браслет</b>\n' \
                     'Из-за динамического формирования списка товаров на Wildberries ' \
                     'полученная позиция на странице может отличаться ' \
                     'от фактического положения товара на сайте на ±2 значения.'
                    

CARD_RENAME_TEXT = '<b>Для смены названия товара необходимо ввести:</b>\n\n' \
                   '1. <b>API-ключ</b>, который можно получить на портале поставщиков\n' \
                   'на платформе seller.wildberries.ru -> профиль -> настройки ' \
                   '-> доступ к новому API -> ввести название ключа (например, "смена наименования")' \
                   ' -> сгенерировать токен и скопировать его\n\n' \
                   '2. <b>supplier-id.</b>\n' \
                   'Чтобы получить supplier-id - есть 2 варианта:\n' \
                   'a. запросить в поддержке Servise Desk, отправив "Здравствуйте, прошу выслать supplier-id",\n' \
                   'выбрав категорию - API, тему - получить supplier-id\n' \
                   'b. получить самому, с помощью видео инструкции https://bit.ly/3v6Uy4l\n\n' \
