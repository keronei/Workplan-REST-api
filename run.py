from app import launcher
from instance.config import app_config

app = launcher(app_config['development'])

if __name__ == '__main__':
    app.run()
