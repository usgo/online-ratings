from app import get_app
app = get_app('config.DockerConfiguration')
app.app_context().__enter__()
