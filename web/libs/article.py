try:
    from sqlcreator import create_alchemy_engine
except ImportError:
    try:
        from libs.sqlcreator import create_alchemy_engine
    except:
        pass

from sqlalchemy import Column, Integer, String, TEXT, ARRAY
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

class Article(Base):
    __tablename__ = 'articles'

    id = Column(Integer, primary_key=True)
    
    title = Column(String(80), nullable=False)
    url = Column(String(80), nullable=False)
    text = Column(TEXT, nullable=False)
    most_common = Column(String(256), nullable=False)
    date = Column(String(24), nullable=False) 
        
    def __init__(self, title, text, url, most_common, date):
        self.title = title
        self.text = text
        self.url = url
        self.most_common = ','.join(most_common)
        self.date = date
        
    def get_most_common(self):
        return self.most_common.split(",")

    def summary(self, count):
        return ' '.join(self.text.replace("\n\n", "\n").split(" ")[:count])


engine = create_alchemy_engine()
Base.metadata.bind = engine
Base.metadata.create_all(engine)


##
## Test code
##

if __name__ == '__main__':
    
    if False:
        with open("../npr_article_572945894.txt") as file_hdl:
            article_text = file_hdl.read()

        title = article_text.split("\n")[0]
        url = "npr.org/testing"
        most_common = "word1,word2,word3"
        date = "2015-01-01"

        from sqlalchemy.orm import sessionmaker

        Session = sessionmaker(bind=engine)
        session = Session()

        article = Article(title, article_text, url, most_common, date)
        session.add(article)

        session.commit()

        for instance in session.query(Article).order_by(Article.id):
            print(instance.title, instance.url)
