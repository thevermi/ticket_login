## Pre-Requisites
The `python-ldap` module must be installed for this script to function.
```
pip install python-ldap
```

## Usage
This script is intended to be used in conjunction with `sshd`, but could probably be modified for other situations.

To enable the functionality of this script, add the following line to `/etc/ssh/sshd_config`:
```
ForceCommand /usr/bin/ticket_login.py
```

Users will be prompted as follows:

![Example Image](https://raw.githubusercontent.com/thevermi/ticket_login/master/xterm-example.png)
