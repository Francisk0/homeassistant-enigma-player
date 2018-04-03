# Readme

This is a custom component for the media_player component of [Home Assistant][1].

It allows you to remotely control your enigma2 compatible satellite/cable receivers.

You must install OpenWebif from your enigma2 image.

  
# What is working:
  - Power status: on, off, standby. 
  - Loads all sources from first bouquet. (Current channel and possibility to change channels)
  - Volume regulation (mute, set, step)
  - Change channel (Selecting from source list or via Right/Left - from remote controller)
  - Current channel and current event
  - Picon from current channel
  - Supports authentication and multiple receivers
    
# Tested with OpenWebif versions:
  - 0.2.7
  - 1.3.0

# Install:
To use this custom component, place the file `enigma.py` inside your folder `~/custom_components/media_player` which is inside your Home Assistant configuration directory.

You need to install (if not yet) the BeautifoulSoup module for Pyhton.

Activate the virtual environment:
``` 
$ source bin/activate
```

Install BeautifoulSoup:
``` 
$ python3 -m pip install BeautifoulSoup4
```

# Configuration Example:
``` python
- platform: enigma
    host: 192.168.1.50
    port: 80
    name: Gigablue
    icon: mdi:satellite-variant
    timeout: 20
    username: root
    password: !secret enigma_password
  - platform: enigma
    host: 192.168.1.51
    port: 80
    name: Dreambox
    timeout: 20
    icon: mdi:satellite-variant
    username: root
    password: !secret enigma_password
```
# Screenshots

![Channel example 1](../master/screenshots/1.png)
![Channel example 2](../master/screenshots/2.png)
![In detail](../master/screenshots/3.png)
![Change source](../master/screenshots/4.png)

# Contact
joao.amaro@gmail.com

# License

# References

[1]: https://home-assistant.io

