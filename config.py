import os

class Config:
    SECRET_KEY = 'your_secret_key_here'
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:%40vaibhav29v@localhost:5432/chatdb'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
