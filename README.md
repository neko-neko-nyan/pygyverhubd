
# Реализация сервера (устройства) GyverHub на python

## Проект находится в стадии активной разработки, api может быть изменено без уведомления!

На данный момент работает только WebSocket

Текущая версия клиента - https://github.com/GyverLibs/GyverHub/tree/90f29e638044aaf8f1ec751ac6518434dcd0de02

Пример использования [здесь](examples/components_ui.py)

# Текущий прогресс
## Сеть
- [x] Интерфейс: WebSocket
- [ ] Интерфейс: MQTT
- [ ] Интерфейс: Bluetooth
- [ ] Интерфейс: Serial
- [x] Device discovery
- [ ] Встроенный клиент

## GUI
- [x] Базовые компоненты
- [ ] Canvas
- [ ] Вкладки

## Устройство
- [x] Базовая информация - название, иконка
- [x] Расширенная информация - сеть, память
- [ ] Автоматический сбор расширенной информации

## OTA
- [x] OTA API
- [ ] Обновление сервера через OTA
- [ ] Автообновление
- [ ] Автоматическая упаковка обновлений

## ФС
- [x] API файловой системы
- [ ] Отражение API ФС на реальную папку

## Другие компоненты
- [ ] Перезапуск сервера по команде reboot
- [x] CLI API
