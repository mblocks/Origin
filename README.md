# Origin

## Run

```bash

pipenv shell
pipenv install
python scripts/initial_database.py
python scripts/initial_data.py
python scripts/initial_redis.py
uvicorn app.main:app --reload

```


## TroubleShooting

### Install mysqlclient via pipenv throw errors

```bash
sudo apt install libmysqlclient-dev
```
<https://stackoverflow.com/questions/56133947/install-mysqlclient-via-pipenv-throw-errors/56832071>


## Can not access wsl web server


```bash
# run this app
uvicorn app.main:app --reload --host=0.0.0.0

# find wsl ip address
ip a | grep eth0

# local visit
# visit server by ip:8000

# internel visit
# add proxy
netsh interface portproxy set v4tov4 listenport=8000 listenaddress=0.0.0.0 connectport=8000 connectaddress=192.168.250.199
# delete proxy
netsh interface portproxy delete v4tov4 listenport=8000 listenaddress=0.0.0.0
```
