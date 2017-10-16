from sender import Mail, Message

from .config import config

email_conf = {}
for setting in ('host', 'port', 'username', 'password', 'use_tls', 'use_ssl'):
    email_conf[setting] = config['email'][setting]
MAIL = Mail(**email_conf)
if 'from_pretty' in config['email']:
    MAIL.fromaddr = (config['email']['from_pretty'], config['email']['from_address'])
else:
    MAIL.fromaddr = config['email']['from_address']


def send_jobs(jobs):
    "Send an email notifying of current jobs"
    msg = Message(
        config['email']['subject'].format(n=len(jobs)),
        to=config['email_address'],
    )

    msg.body = "Found {n} potential jobs:\n\n"
    for idx, job in enumerate(jobs):
        idx += 1
        msg.body += "{}. {}\n\n\n".format(idx, job.to_string())

    MAIL.send(msg)
