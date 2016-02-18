from app import get_app

if __name__ == "__main__":
    app = get_app('config.DockerConfiguration')
    app.run(host='0.0.0.0')
