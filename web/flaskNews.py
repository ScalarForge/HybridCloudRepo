__author__ = 'tv'


from libs.article import Article
from libs.sqlcreator import create_alchemy_engine

from sqlalchemy import desc
from sqlalchemy.orm import sessionmaker
from flask import Flask, render_template, request

app = Flask(__name__)
app.secret_key = '0823##*_OJKH*Gjjuu&&&55(*&(*&(7^%%'

@app.route('/article/<id>')
def getArticle(id=None):
    if not id:
        return

    return render_template('article.html', article = [x for x in session.query(Article).filter(Article.id == id)][0])



@app.route('/search/page_<page>/', methods=['GET', 'POST'])
def getSearch(page=0, search=None):
    global session

    per_page = 10
    offset = int(page) * per_page

    if request.args.get('search'):
        search = request.args.get('search')

    if not search or len(search) == 0:
        return getNews()

    print("Searching:", search)

    search_list = search.split(" ")

    query_hdl = session.query(Article)

    for srch in search_list:
        srch = srch.lower()

        if ":" in srch:
            col = srch.split(":")[0].strip()
            val = srch.split(":")[1].strip()

            query_hdl = query_hdl.filter(getattr(Article, col).contains())

        else:
            query_hdl = query_hdl.filter(Article.most_common.contains(srch))

    total_count = query_hdl.count()
    articles = query_hdl.order_by(desc(Article.date)).limit(10).offset(offset)

    return render_template('index.html', articles=articles,
                           page=int(page), start=offset + 1, end=offset + per_page,
                           count=total_count, search=search)


@app.route("/", methods=['GET', 'POST'])
@app.route('/page_<page>/')
def getNews(page=0):

    global session

    per_page = 10
    offset = int(page)*per_page

    return render_template('index.html', articles=session.query(Article).
                           order_by(desc(Article.date)).limit(10).offset(offset),
                           page=int(page), start=offset+1, end=offset + per_page, count=session.query(Article).count())


if __name__ == '__main__':
    engine = create_alchemy_engine()

    Session = sessionmaker(bind=engine)
    session = Session()

    app.debug = True
    app.run(host='0.0.0.0', port=8080)