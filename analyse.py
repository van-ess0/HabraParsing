import psycopg2
import matplotlib.pyplot as plt
import pymorphy2
import matplotlib.ticker as ticker
from gensim.models.ldamodel import LdaModel


def top5tags():
    SQL = 'SELECT tag_name FROM \
    (\
    SELECT tag_id, COUNT(tag_id) as numb FROM tag_to_article_table GROUP BY tag_id\
    ) AS t\
    JOIN tag_table ON t.tag_id=tag_table.tag_id ORDER BY numb DESC\
    LIMIT 5'

    cur.execute(SQL)
    tag = ['', '', '', '', '']
    for i in range(5):
        tag[i] = cur.fetchone()[0]
    SQL = 'SELECT tag_id, COUNT(tag_id) as numb FROM tag_to_article_table\
            GROUP BY tag_id ORDER BY numb DESC'
    cur.execute(SQL)
    tagid = [0, 0, 0, 0, 0]
    for i in range(5):
        tagid[i] = cur.fetchone()[0]

    tag_population = [[0 for j in range(10)] for i in range(5)]

    SQL = 'SELECT numb AS numb4tag FROM\
        (\
         SELECT tag_id, COUNT(tag_id) AS numb FROM\
         (\
          SELECT tag_id FROM\
          (\
            SELECT article_id FROM article_table\
            WHERE Extract(YEAR from article_date)={0}\
          ) AS a\
          JOIN tag_to_article_table AS tat ON (tat.article_id=a.article_id)\
         ) AS t\
         GROUP BY t.tag_id ORDER BY numb DESC\
        ) as ct\
        WHERE tag_id={1}'

    for j in range(10):
        for i in range(5):
            cur.execute(SQL.format(str(2006+j), str(tagid[i])))
            a = cur.fetchone()
            if a is not None:
                tag_population[i][j] = a[0]
            else:
                tag_population[i][j] = 0
    plt.title('Population of the 5 most popular tags by year.')
    plt.xlabel('Year 2006+')
    plt.ylabel('Number of articles')
    for i in range(5):
        plt.plot(tag_population[i], label=tag[i])
    plt.legend()
    plt.show()


def articlesbydow():
    SQL = '''SELECT COUNT(article_id) FROM article_table WHERE date_part('dow', article_date)={0}'''
    dow = [0 for i in range(7)]
    for i in range(7):
        cur.execute(SQL.format(i))
        dow[i] = cur.fetchone()[0]

    # Sunday - Saturday => Monday - Sunday
    temp = dow[0]
    dow[:6:] = dow[1::]
    dow[6] = temp

    plt.title('Number of articles by Day of Week.')
    plt.xlabel('Monday - Sunday')
    plt.ylabel('Number of articles')
    plt.plot(dow)
    # plt.legend()
    plt.show()


def getarticles():
    articles = []
    SQL = 'SELECT article_topic FROM article_table'
    cur.execute(SQL)
    article = cur.fetchone()
    number = 0
    while article is not None:
        articles.append(article[0])
        article = cur.fetchone()
        number += 1

    '''SQl = 'SELECT COUNT(article_id) FROM article_table'
    cur.execute(SQL)
    number = cur.fetchone()[0]'''
    return articles, number


def smartsplit(str):
    l = str.split()
    newl = []
    symb = {'!', '?',
            ',', '.',
            "'", '@',
            '#'}
    for i in l:
        if i[len(i) - 1] in symb:
            i = i[:len(i) - 1:]
            if i[0] in symb:
                i = i[1::]
            newl.append(i)
        else:
            if i[0] in symb:
                i = i[1::]
            newl.append(i)
    return newl


def normalaisestr(str):
    parsedstring = []
    morph = pymorphy2.MorphAnalyzer()
    l = smartsplit(str)
    for i in l:
        parsedstring.append(morph.parse(i)[0].normal_form)
    return parsedstring

db = psycopg2.connect(database='db_name', user='db_username', host='db_ip', port=db_port)

cur = db.cursor()

top5tags()
articlesbydow()
numberofarticles = 0
#articles, numberofarticles = getarticles()
#lda = LdaModel(articles, num_topics=100)
