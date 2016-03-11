from app import get_app
from app.models import db
app = get_app('config.DockerConfiguration')
db.init_app(app)
app.app_context().__enter__()
