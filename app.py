from app import create_app
from quart_sqlalchemy import SQLAlchemy
from app.database import init_db
from sqlalchemy import text
from app.database import engine


app = create_app()
init_db()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8852)
