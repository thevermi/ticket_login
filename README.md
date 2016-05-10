## Pre-Requisites
The `python-ldap` module must be installed for this script to function.
```
pip install python-ldap
```
We make some assumptions about your environment, mainly:

1. You're using Active Directory
2. Your Linux username is the same as your AD sAMAccountName
3. Your email address is different than your AD sAMAccountName--otherwise, you could just pin @whatever.com to the end of your username and avoid the LDAP lookup altogether.

## Usage
This script is intended to be used in conjunction with `sshd`, but could probably be modified for other situations.

To enable the functionality of this script, add the following line to `/etc/ssh/sshd_config`:
```
ForceCommand /usr/bin/ticket_login.py
```

Users will be prompted as follows:

![Example Image](https://raw.githubusercontent.com/thevermi/ticket_login/master/xterm-example.png)
