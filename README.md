# Minecraft-Bedrock-server-updater
A script that will auto update and run vanilla Minecraft bedrock server

## Requirement

Please install equivalent package if you use another OS
```

apt-get update
apt-get -y install tmux unzip libcurl4 python3 python3-pip
pip3 install beautifulsoup4 requests
```

## How to use
```
python3 mcUpdater.py
```
And than it will auto download and run minecraft bedrock server for you.
And it will check update everyday.

if you want run it in background, run this:
```
tmux new -s MC_BDRK_Updater -d ./mcUpdater.py
```

If you want to access server console, run this command:
```
 tmux a -t MC_BDRK
```
