# REPORTS.md

# Отчеты

## /orders

Общая сводка последних заказов.

Показывает:
- Telegram Stars;
- Robokassa;
- источник оплаты;
- статус;
- сумму;
- пользователя.

## /orders_rs

Панель Robokassa.

Показывает:
- счетчики created / paid / failed;
- последние заказы по статусам.

## /orders_rs_file

TXT-экспорт всех заказов Robokassa.

Содержит:
- дату и время формирования;
- сводку;
- суммы;
- популярность пакетов;
- раздел CREATED;
- раздел PAID;
- раздел FAILED.

## /orders_tg

Панель Telegram Stars.

## /orders_tg_file

TXT-экспорт заказов Telegram Stars.

Планируется по той же логике, что и Robokassa-экспорт.

## /orders_file

Полный TXT-отчет по заказам.

Содержит:
- дату и время формирования;
- сводку;
- финансы;
- популярность пакетов;
- Telegram Stars;
- Robokassa CREATED;
- Robokassa PAID;
- Robokassa FAILED.