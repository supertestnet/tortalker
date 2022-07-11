# Tor talker
A tor proxy for connecting to lnbits and/or lnd over tor, with functions for getting and checking invoices

First install tor and get it running (`sudo apt install tor` should do both) and then run tortalker. Set up nginx to forward traffic on some port to port 5001 and then set a password line 8. Run tortalker.py with `python3 tortalker.py` and suddenly have a rest api endpoint that you can use to communicate with LND and LNBits over tor.

BTW here is what I use for nginx:

```
server {
    listen 5000;
    server_name myserver.example.com;

    location / {
        proxy_pass http://localhost:5001;
    }
}
```

Here is my systemd service file (which I put into `/etc/systemd/system`):

```
[Unit]
Description=Tortalker as systemd service
After=network-online.target

[Service]
User=debian
WorkingDirectory=/home/debian/tortalker/
ExecStart=nohup python tortalker.py &
SyslogIdentifier=tortalker-starter
Restart=always

[Install]
WantedBy=multi-user.target
```
