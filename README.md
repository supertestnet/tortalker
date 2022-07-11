# Tor talker
A tor proxy for connecting to lnbits and/or lnd over tor, with functions for getting and checking invoices

First install tor and get it running (`sudo apt install tor` should do both) and then run tortalker. Set up nginx to forward traffic on some port to port 5001 and then set a password line 8. Run tortalker.py with python3 tortalker.py and now you can communicate with LND and LNBits over tor.

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
