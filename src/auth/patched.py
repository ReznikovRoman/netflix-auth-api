from gevent import monkey

monkey.patch_all()

from auth.main import create_app  # noqa, isort:skip

app = create_app()
