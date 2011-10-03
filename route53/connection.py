import boto
from flask import current_app


def get_connection(service='route53'):
    meth = getattr(boto, 'connect_%s' % service)
    return meth(current_app.config['AWS_ACCESS_KEY_ID'],
        current_app.config['AWS_SECRET_ACCESS_KEY']
    )
