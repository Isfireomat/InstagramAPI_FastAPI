### Запуск
Для запуска нужно:
- ACCESS_TOKEN поместить в .env (Его берёте от аккаунта инстаграмма https://developers.facebook.com/apps/963694342366854/instagram-business/API-Setup/?business_id=4098838467014991)
- VERIFY_TOKEN поместить в .env (Придумываете сами)
- Запустить через консоль при помощи команды 'docker-compose up --build'
- Далее подключить к Webhook через в https://developers.facebook.com/apps/963694342366854/instagram-business/API-Setup/?business_id=4098838467014991 
    Там нужно указа указать "URL обратного вызова" - https://{путь к вашему серверу}/api/webhook (Если запускаете на локальной машине, то тунель можно сделать через ngrok)
    "Подтверждение маркера" - указанныйв .env VERIFY_TOKEN
    После подписываете Webhook на messages

Бэкенд готов к работе
Проверить api можно в http://127.0.0.1:8000/docs