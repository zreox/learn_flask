#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
COV = None
if os.environ.get('ZREOX_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()

from app import create_app, db
from app.models import Role, User, Follow, Permission, Post, Comment
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

app = create_app(os.getenv('ZREOX_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, Role=Role, User=User, Follow=Follow,
                Permission=Permission, Post=Post, Comment=Comment)
manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test(coverage=False):
    """Run the unit test."""
    if coverage and not os.environ.get('ZREOX_COVERAGE'):
        import sys
        import subprocess
        os.environ['ZREOX_COVERAGE'] = '1'
        # os.execvp(sys.executable, [sys.executable] + sys.argv)
        sys.exit(subprocess.call([sys.executable] + sys.argv))

    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print 'Coverage Summary:'
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print 'HTML version: file://%s/index.html' % covdir
        COV.erase()


@manager.command
def profile(length=20, profile_dir=None):
    """Start the application under the code profiler."""
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length],
                                      profile_dir=profile_dir)
    app.run(debug=False)


if __name__ == '__main__':
    manager.run()
