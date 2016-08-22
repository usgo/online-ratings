from flask.ext.script import Manager

from app import get_app

from create_db import drop_all_tables, create_barebones_data, create_all_data, create_server

app = get_app('config.DockerConfiguration')

manager = Manager(app)
manager.command(drop_all_tables)
manager.command(create_barebones_data)
manager.command(create_all_data)
manager.command(create_server)

@manager.command
def config():
    'Print out all config values from the fully assembled flask app'
    print('\n'.join('%s=%s' % item for item in sorted(app.config.items())))

if __name__ == '__main__':
	manager.run()