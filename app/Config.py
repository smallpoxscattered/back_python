import secrets


class Config:
    JWT_SECRET_KEY = "08d7c98a5c0e01fd1f138cb58a5f4bc1203cd9fb7267ffbad2dd62d8c9d88512" # secrets.token_hex(32)
    DATABASE_URI = "mysql+pymysql://root:123456@127.0.0.1:3306/LSZ"
    # ADMIN_TOKEN = 

