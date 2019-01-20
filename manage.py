import os
import pytest
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from app import launcher, db


app = launcher()

migrate = Migrate(app, db)

manager = Manager(app)

manager.add_command('db', MigrateCommand)

@manager.command
def test():
    """Run tests"""
    pytest.main(["-s", "app/tests"])

if __name__ == '__main__':
    manager.run()