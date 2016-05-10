#!/usr/bin/env python
"""ticket_login.py: Prompts a user for a login justification, and emails a notification to that user."""

import smtplib
import email
import os
import ldap
import sys
import signal

from email import utils
from email.mime.text import MIMEText
from time import strftime
from socket import gethostname
from subprocess import check_call as call, CalledProcessError

try:
    from pwd import getpwuid
    pwd = True

except ImportError:
    from getpass import getuser
    pwd = False

__author__        = "Justin Vermillion"
__copyright__     = "Copyright 2016, Synchronoss Technologies, Inc."
__license__       = "GPL"
__version__       = "2.13"
__maintainer__    = "Justin Vermillion"
__email__         = "justin.vermillion@synchronoss.com"
__status__        = "Production"

# Global Configuration
from_addr   = ''    # The email used for sending notifications.
from_name   = ''    # Display name of the notification email.
reply_to    = ''    # Where do you want users to reply in the case of an unauthorized attempt?
smtp_server = ''    # Server used for sending notification emails.
smtp_port   = 25    # SMTP Port; 25 is usually sufficient.
ldap_server = ''    # Path to your LDAP server, in the format ldap://server.domain.tld
bind_acct   = ''    # Account with permissions to bind to LDAP
bind_pw     = ''    # Bind account password
search_root = ''    # The search root for your LDAP lookup; for example: dc=domain,dc=tld
fail_email  = ''    # Email to notify in case of script failures.
shell       = ''    # Preferred shell for Linux systems.

pre_cmds    =		# A list of commands to run before dropping to shell. (Optional)
				[
                '/bin/echo "Your last login information:"',
                '/usr/bin/lastlog -u `whoami`',
                '/bin/cat /etc/motd'
				]

# Don't edit this stuff.
def send_email(msg):
    s = smtplib.SMTP(smtp_server, smtp_port)

    try:
        s.sendmail(from_addr, msg['To'], msg.as_string())
        s.quit()

    except smtplib.SMTPException as e:
        print 'Unable to send email. %s' % str(e)
        s.quit()


def notify_fail(host, user, details, error):
    body = (
            "On {0} at {1}, the user account {2} was used to login to {3}.\n\n"
            "The user entered the following details: {4}\n\n"
            "The login script failed with the following error: {5}"
           )

    msg = MIMEText(body.format(strftime('%x'), strftime('%X'), user, host, details, error))

    msg['Subject'] = 'Recent System Login Activity'
    msg['From']    = '{0} <{1}>'.format(from_name, from_addr)
    msg['To']      = fail_email
    msg['Date']    = utils.formatdate(localtime=1)

    send_email(msg)

def notify_user(host, user, email, details):
    body = (
            "On {0} at {1}, your user account {2} was used to login to {3}.\n\n"
            "The following explanation or ticket number was provided: {4}\n\n"
            "If you do not recognize this login attempt, please reply to this email, or contact {5}"
           )

    msg = MIMEText(body.format(strftime('%x'), strftime('%X'), user, host, details, reply_to))

    msg['Subject'] = 'Recent System Login Activity'
    msg['From']    = '{0} <{1}>'.format(from_name, from_addr)
    msg['To']      = email
    msg['Date']    = utils.formatdate(localtime=1)
    msg.add_header('reply-to', reply_to)

    send_email(msg)

def drop_to_shell():
    print 'Thank you.\n'

    if sys.platform == 'linux' or sys.platform == 'linux2':
        cmd = os.environ.get('SSH_ORIGINAL_COMMAND')
        try:
            if cmd != None:
                call(cmd)
            else:
                if pre_cmds:
                    for x in pre_cmds:
                        call(x, shell=True)
        
        except CalledProcessError as e:
            print "Tried to execute some commands that failed."
            print e
        
        call(shell)
    
    sys.exit(0)

def main():
    if pwd:
        user = getpwuid(os.geteuid()).pw_name
    else:
        user = getuser()

    details = raw_input('Please enter a justification or ticket number associated with this login.\n> ')

    l = ldap.initialize(ldap_server)

    try:
        l.protocol_version = ldap.VERSION3
        l.simple_bind_s(bind_acct, bind_pw)

    except ldap.INVALID_CREDENTIALS:
        notify_fail(host, user, details, 'Unable to bind to LDAP. Invalid credentials.')
        drop_to_shell()

    except ldap.LDAPError as e:
          if type(e.message) == dict and e.message.has_key('desc'):
              notify_fail(user, host, details, e.message['desc'])
        else:
            notify_fail(user, host, details, e)
        drop_to_shell()

    try:
        _, result_data = l.result(l.search(search_root, ldap.SCOPE_SUBTREE, '(sAMAccountName={0})'.format(user), ['mail']), 0)
        for dn, entry in result_data:
            if dn != None:
                to_addr = str(entry['mail']).strip('[]\'')
            else:
                notify_fail(gethostname(), user, details, 'User not found in LDAP.')
                drop_to_shell()

    except ldap.LDAPError as e:
        notify_fail(user, host, details, e)
        drop_to_shell()

    l.unbind_s()

    notify_user(gethostname(), user, to_addr, details)

    drop_to_shell()

main()