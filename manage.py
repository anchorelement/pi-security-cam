def deploy():
    """Run deployment tasks."""
    from __init__ import create_app, db
    from flask_migrate import upgrade, migrate, init, stamp
    from models import User

    app = create_app()
    app.app_context().push()
    db.create_all()

    # migrate database to latest revision
    init()
    stamp()
    migrate()
    upgrade()


if __name__ == "__main__":
    deploy()
