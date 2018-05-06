from sqlalchemy import create_engine

def create_alchemy_engine():
    return create_engine('sqlite:///../articles.db')