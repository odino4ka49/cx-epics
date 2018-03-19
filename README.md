# cx-epics

Конвертор предназначен для синхронизации значений каналов cx и pv.
А именно: используя список каналов из конфигурационного файла gateway_config.json, он копирует данные в соответствующие каналы при инициализации, а также при изменении данных в канале посредством подписки.

Расположен на машине vepp4-vm1
/home/oidin/projects/cx-gateway - здесь лежат файлы для конвертора

gateway.py - программа конвертора
gateway_config.json - здесь хранится список связей между каналами cx и pv
listing.py - выведет список связей в удобном для пользователя виде

Про обозначения в конфигурационном файле gateway_config.json:
“channel” и “pv” - полный адрес канала или pv
“datatype”: “str” - указывает на текстовый тип данных каналов
“direction” - направление для синхронизации:
p - из pv в channel
x - из channel в pv
b - в обе стороны
    “priority” - нужно при “direction”: “b”; указывает на то, какие данные являются приоритетными при старте программы gateway (x или p)
Пример записи:
    [
        …,
        {
           "channel": "vepp4-pult6:2.cgvi.prescaler",
           "pv": "K500:0CGVI:Resolution-SP",
           "direction": "b",
           "priority": "x"
        },
        …
    ]

Чтобы подключить свою конфигурацию:
    Либо заменить gateway_config.json, 
либо добавить другой файл “-----.json” и подставить название в строку openConfigFile(“-----.json”) в gateway.py

Чтобы получить список не всех устройств, а с определенными параметрами:
    python listing.py -s регулярное_выражение
Если вы помните только часть названия, этого достаточно для регулярного выражения. Например, “Curr”.
Если вы помните только отрывки из названий, вам нужно вставлять между отрывками знак “.*” - это значит сколько угодно любых знаков. Например, “V4.*pol”

Конвертор запущен через систему Systemd для того, чтобы при возникновении неполадок или перезапуска машины, процесс перезапускался.
Файлы для работы с systemd находятся в папке /etc/systemd/system
Конфигурационный файл: gateway.service
Чтобы перезапустить процесс самостоятельно:
systemctl restart gateway.service