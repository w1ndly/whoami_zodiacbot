# PROJECT_STRUCTURE.md

# Структура проекта

## bot.py

Главная точка запуска Telegram-бота.

## database.py

SQLite-база данных и SQL-запросы.

## storage.py

Промежуточный слой между логикой бота и базой данных.

## handlers/

Обработчики команд и пользовательских действий.

### handlers/admin.py

Админские команды.

### handlers/birth.py

Обработка даты рождения.

### handlers/callbacks.py

Inline-кнопки и callback-логика.

### handlers/payments.py

Telegram Stars.

## services/

Сервисные модули.

### services/payment_service.py

Магазин, пакеты, тексты оплаты.

### services/payment_gateway.py

Создание платежей Robokassa.

### services/robokassa_service.py

Подписи и ссылки Robokassa.

### services/report_service.py

Формирование TXT-отчетов.

## user_profile.py

Профиль пользователя и лимиты.

## limits.py

Тексты и логика ограничений.

## VERSION.md

Текущая версия проекта.

## CHANGELOG.md

История изменений.

## PROJECT_STATE.md

Актуальное состояние проекта.

## SUMMARY.md

Краткая сводка последних этапов.