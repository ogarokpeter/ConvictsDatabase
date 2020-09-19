# Сервис учёта зэков в исправительной колонии №15 города Ангарска Иркутской области

Сервис долгосрочно хранит информацию о зэках, когда-либо отбывавших наказание в ИК-15 г. Ангарска Иркутской области. Каждому зэку выдаётся уникальный id. Можно добавить зэка (имя, статья, срок, закончил ли отбывать наказание, статус в воровской иерархии) в базу, изменить его статус и состояние, удалить зэка из базы.

Для разворачивания сервиса нужно из директории проекта выполнить следующие команды:

```
sudo kubectl apply -f redis-deployment.yml && sudo kubectl apply -f redis-service.yml && sudo kubectl apply -f app-deployment.yml && sudo kubectl apply -f app-service.yml
```
После этого нужно выяснить адрес, который был назначен для доступа в контейнер:
```
ogarokpeter@kuber:~/project$ sudo kubectl get ep
NAME         ENDPOINTS          AGE
app          172.17.0.5:5000    27s
kubernetes   10.128.0.33:8443   56s
redis        172.17.0.4:6379    28s
```
Искомый адрес --- это ENDPOINT приложения app. Теперь всё работает.

## Протокол общения с сервисом

Получение главной страницы:
```
ogarokpeter@kuber:~/project$ curl -i -H "Content-Type: application/json" -X GET  http://172.17.0.5:5000
HTTP/1.0 200 OK
Content-Type: text/html; charset=utf-8
Content-Length: 23
Server: Werkzeug/1.0.1 Python/3.7.7
Date: Sat, 16 May 2020 16:29:37 GMT

This is IK-15 database.
```
Получение (пока ещё пустой) базы заключённых:
```
ogarokpeter@kuber:~/project$ curl -i -H "Content-Type: application/json" -X GET  http://172.17.0.5:5000/convicts
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 16
Server: Werkzeug/1.0.1 Python/3.7.7
Date: Sat, 16 May 2020 16:29:45 GMT

{"convicts":{}}
```
Доавление заключённого:
```
ogarokpeter@kuber:~/project$  curl -i -H "Content-Type: application/json" -X POST -d '{"name":"Ivan Golunov","term":"1000","article":"228/282"}' http://172.17.0.5:5000/convicts
HTTP/1.0 201 CREATED
Content-Type: application/json
Content-Length: 113
Server: Werkzeug/1.0.1 Python/3.7.7
Date: Sat, 16 May 2020 16:30:57 GMT

{"convict":{"article":"228/282","id":4794094434,"name":"Ivan Golunov","released":false,"term":"1000","type":""}}
```
Получение базы заключённых:
```
ogarokpeter@kuber:~/project$ curl -i -H "Content-Type: application/json" -X GET  http://172.17.0.5:5000/convicts
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 129
Server: Werkzeug/1.0.1 Python/3.7.7
Date: Sat, 16 May 2020 16:31:02 GMT

{"convicts":{"4794094434":{"article":"228/282","id":4794094434,"name":"Ivan Golunov","released":false,"term":"1000","type":""}}}
```
(Ошибочное) добавление заключённого:
```
ogarokpeter@kuber:~/project$ curl -i -H "Content-Type: application/json" -X POST -d '{"name":"Ivan Golunov","term":"1000","article":"228/282"}' http://172.17.0.5:5000/convicts
HTTP/1.0 201 CREATED
Content-Type: application/json
Content-Length: 113
Server: Werkzeug/1.0.1 Python/3.7.7
Date: Sat, 16 May 2020 16:31:39 GMT

{"convict":{"article":"228/282","id":2943666121,"name":"Ivan Golunov","released":false,"term":"1000","type":""}}
```
Получение базы заключённых:
```
ogarokpeter@kuber:~/project$ curl -i -H "Content-Type: ap http://172.17.0.5:5000/convicts
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 243
Server: Werkzeug/1.0.1 Python/3.7.7
Date: Sat, 16 May 2020 16:31:55 GMT

{"convicts":{"2943666121":{"article":"228/282","id":2943666121,"name":"Ivan Golunov","released":false,"term":"1000","type":""},"4794094434":{"article":"228/282","id":4794094434,"name":"Ivan Golunov","released":false,"term":"1000","type":""}}}
```
Удаление ошибочно добавленного заключённого:
```
ogarokpeter@kuber:~/project$ curl -i -H "Content-Type: application/json" -X DELETE  http://172.17.0.5:5000/convicts/2943666121
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 16
Server: Werkzeug/1.0.1 Python/3.7.7
Date: Sat, 16 May 2020 16:33:15 GMT

{"result":true}
```
Добавление другого заключённого:
```
ogarokpeter@kuber:~/project$ curl -i -H "Content-Type: application/json" -X POST -d '{"name":"Konstantin Kotov","term":"1,5","article":"212.1"}' http://172.17.0.5:5000/convicts
HTTP/1.0 201 CREATED
Content-Type: application/json
Content-Length: 114
Server: Werkzeug/1.0.1 Python/3.7.7
Date: Sat, 16 May 2020 16:32:39 GMT

{"convict":{"article":"212.1","id":8192327260,"name":"Konstantin Kotov","released":false,"term":"1,5","type":""}}
```
Получение базы заключённых:
```
ogarokpeter@kuber:~/project$ curl -i -H "Content-Type: application/json" -X GET  http://172.17.0.5:5000/convicts
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 359
Server: Werkzeug/1.0.1 Python/3.7.7
Date: Sat, 16 May 2020 16:33:34 GMT

{"convicts":{"4794094434":{"article":"228/282","id":4794094434,"name":"Ivan Golunov","released":false,"term":"1000","type":""},"8192327260":{"article":"212.1","id":8192327260,"name":"Konstantin Kotov","released":false,"term":"1,5","type":""}}}
```
Попытка удаления заключённого с несуществующим id:
```
ogarokpeter@kuber:~/project$ curl -i -H "Content-Type: application/json" -X DELETE  http://172.17.0.5:5000/convicts/2432188641
HTTP/1.0 404 NOT FOUND
Content-Type: text/html; charset=utf-8
Content-Length: 232
Server: Werkzeug/1.0.1 Python/3.7.7
Date: Sat, 16 May 2020 16:34:02 GMT

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
<title>404 Not Found</title>
<h1>Not Found</h1>
```
Изменение состояния (освобождение) заключённого:
```
ogarokpeter@kuber:~/project$ curl -i -H "Content-Type: application/json" -X PUT -d '{"released":true}'  http://172.17.0.5:5000/convicts/8192327260
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 113
Server: Werkzeug/1.0.1 Python/3.7.7
Date: Sat, 16 May 2020 16:36:18 GMT

{"convict":{"article":"212.1","id":8192327260,"name":"Konstantin Kotov","released":true,"term":"1,5","type":""}}
```
Получение базы заключённых:
```
ogarokpeter@kuber:~/project$ curl -i -H "Content-Type: application/json" -X GET  http://172.17.0.5:5000/convicts
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 243
Server: Werkzeug/1.0.1 Python/3.7.7
Date: Sat, 16 May 2020 16:36:21 GMT

{"convicts":{"4794094434":{"article":"228/282","id":4794094434,"name":"Ivan Golunov","released":false,"term":"1000","type":""},"8192327260":{"article":"212.1","id":8192327260,"name":"Konstantin Kotov","released":true,"term":"1,5","type":""}}}
```
Изменение статуса заключённого:
```
ogarokpeter@kuber:~/project$ curl -i -H "Content-Type: application/json" -X PUT -d '{"type":"muzhik"}'  http://172.17.0.5:5000/convicts/8192327260
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 119
Server: Werkzeug/1.0.1 Python/3.7.7
Date: Sat, 16 May 2020 16:48:19 GMT

{"convict":{"article":"212.1","id":8192327260,"name":"Konstantin Kotov","released":true,"term":"1,5","type":"muzhik"}}
```
Получение базы заключённых:
```
ogarokpeter@kuber:~/project$ curl -i -H "Content-Type: application/json" -X GET  http://172.17.0.5:5000/convicts
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 249
Server: Werkzeug/1.0.1 Python/3.7.7
Date: Sat, 16 May 2020 16:48:28 GMT

{"convicts":{"4794094434":{"article":"228/282","id":4794094434,"name":"Ivan Golunov","released":false,"term":"1000","type":""},"8192327260":{"article":"212.1","id":8192327260,"name":"Konstantin Kotov","released":true,"term":"1,5","type":"muzhik"}}}

```