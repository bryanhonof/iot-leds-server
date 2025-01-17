# Example IoT Pynq-Z2 HTTP LED Server With Automation

A small example repo that packages a simple HTTP server that can control the 
Pynq's on-board LEDs. This repo contain some automation to create a `.deb` 
archive/package every time a tag is pushed with git.

The `.deb` package contains 2 services, the actual HTTP server 
`leds-server.service` and a timer/service, `update-leds-server.{timer,service}`, 
to automatically try and update the aforementioned HTTP server.

This repo is meant to be forked and edited so that the student has their own 
auto-updating software running on their Pynq. Fulfilling the requirement of an 
"over-the-air" deployment.

## Installation

To install this program, you'll first have to bootstrap the Pynq with it. You 
can do so as follows.

```console
$ # Download the v1.0.4 release from bryanhonof/iot-leds-server, make sure to 
$ # update this to your own repo and version.
$ wget https://github.com/bryanhonof/iot-leds-server/releases/download/v1.0.4/leds-server.deb
$ # Install the .deb archive.
$ dpkg --install leds-server.deb
$ # Install the dependencies of this program, jq in this case.
$ apt-get --yes --fix-broken install ./leds-server.deb
```

You can check if the program is running by doing the following.

```console
$ systemctl status leds-server.service
● leds-server.service - Simple HTTP server that can control the Pynq's LEDs
     Loaded: loaded (/lib/systemd/system/leds-server.service; enabled; vendor preset: enabled)
     Active: active (running) since Fri 2025-01-17 04:33:53 UTC; 4min 49s ago
   Main PID: 12092 (python3)
      Tasks: 1 (limit: 874)
     Memory: 141.5M
        CPU: 18.896s
     CGroup: /system.slice/leds-server.service
             └─12092 python3 /usr/local/bin/leds_server.py

Jan 17 04:33:53 pynq systemd[1]: Started Simple HTTP server that can control the Pynq's LEDs.
Jan 17 04:33:54 pynq env[12092]: INFO:__main__:Loading Pynq overlay, this might take a while...
Jan 17 04:34:13 pynq env[12092]: INFO:__main__:Reading /etc/leds-server.conf...
Jan 17 04:34:13 pynq env[12092]: INFO:__main__:Doing little LED sequence...
Jan 17 04:34:17 pynq env[12092]: INFO:__main__:Starting HTTP LED server...
Jan 17 04:35:07 pynq env[12092]: 100.109.232.66 - - [17/Jan/2025 04:35:07] "GET / HTTP/1.1" 200 -
```

You should see the `Active: active (running)` status, if not, something went 
wrong durig installation or your system was in an odd state to begin with.

## Usage

To get the current LED status, you can make the following HTTP request. Note 
that `100.115.146.70` is the IPv4 adddress of my Pynq on my tailscale network.


```console
$ curl 100.115.146.70:5050 | jq
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100    23    0    23    0     0     35      0 --:--:-- --:--:-- --:--:--    35
{
  "leds": [
    0,
    0,
    0,
    0
  ]
}
```

You can see the LEDs are currently completely off, let's turn some on.

```console
$ curl -v -X POST 100.115.146.70:5050 -d '{"leds":[0,1,0,1]}'
Note: Unnecessary use of -X or --request, POST is already inferred.
*   Trying 100.115.146.70:5050...
* Connected to 100.115.146.70 (100.115.146.70) port 5050
> POST / HTTP/1.1
> Host: 100.115.146.70:5050
> User-Agent: curl/8.7.1
> Accept: */*
> Content-Length: 18
> Content-Type: application/x-www-form-urlencoded
>
* upload completely sent off: 18 bytes
* HTTP 1.0, assume close after body
< HTTP/1.0 200 OK
< Server: BaseHTTP/0.6 Python/3.10.4
< Date: Fri, 17 Jan 2025 04:41:45 GMT
< Content-type: text/html
<
* Closing connection
```

This should turn on 2 LEDs on the board.
