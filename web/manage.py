from flask.ext.script import Manager, Server

from app import get_app

app = get_app('config.DockerConfiguration')

manager = Manager(app)
manager.add_command('runserver', Server(host='0.0.0.0'))

if __name__ == '__main__':
	manager.run()
