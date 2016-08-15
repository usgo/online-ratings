from flask.ext.script import Manager

from app import get_app

app = get_app('config.DockerConfiguration')

manager = Manager(app)

if __name__ == '__main__':
	manager.run()