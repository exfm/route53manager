#! /usr/bin/env python

from flaskext.script import Manager
from route53 import app

manager = Manager(app)


@manager.command
def createdb():
    """Drop and recreate database"""
    from route53.models import db
    db.drop_all()
    db.create_all()

if __name__ == "__main__":
    manager.run()
