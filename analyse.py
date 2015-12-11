import psycopg2
import matplotlib.pyplot as plt
import pymorphy2
from gensim.models.ldamodel import LdaModel
from gensim import corpora
import gc


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
    plt.show()


def getarticles():
    # TODO: Make getiing thread-safe (get number of articles and articles in single request)
    articles = []
    SQL = 'SELECT COUNT(article_id) FROM article_table'
    cur.execute(SQL)
    number = cur.fetchone()[0]
    SQL = 'SELECT article_topic FROM article_table'
    cur.execute(SQL)
    # number = 100
    for i in range(number):
        article = cur.fetchone()
        articles.append(article[0])

    return articles, number


def normalaisestr(str):
    parsedstring = []
    l = str.split()
    for i in l:
        parsedstring.append(morph.parse(i)[0].normal_form)
    return parsedstring


def ldaforhabr():
    numberofarticles = 0
    articles, numberofarticles = getarticles()
    print("Got articles")
    # Normalaize texts
    i = 0
    for article in articles:
        article = replacesymbols(article)
        articles[i] = normalaisestr(article.lower())
        i += 1
    print('Normalaised')
    # Remove unnecessary words
    texts = [[word for word in article if word not in stoplist]
             for article in articles]
    print('Deleted stopwords')
    dictionary = corpora.Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in texts]
    print('Starting training')
    f = open('lda.log', 'w')
    for i in range(i // numberofarticles):
            begin = 100 * i
            end = 100 * (i + 1)
            if end > numberofarticles:
                end = numberofarticles
            lda = LdaModel(corpus[begin:end:], id2word=dictionary, num_topics=end - begin)

            for j in range(lda.num_topics):
                topics = lda.get_topic_terms(j, 15)
                f.write(str(begin + j) + ": ")
                # print(topics)
                for topic in topics[0]:

                    top = dictionary.get(topic)
                    if top is not None:
                        f.write(top + '\n')

                f.write('-----------\n')
            # i += 1
            del lda
    f.close()


def getarticlesbyyear(year):

    # TODO: Make getiing thread-safe (get number of articles and articles in single request)
    SQL = 'SELECT COUNT(article_id) FROM article_table WHERE Extract(YEAR from article_date)={0}'
    cur.execute(SQL.format(year))
    number = cur.fetchone()[0]
    articles = []
    SQL = 'SELECT article_topic FROM article_table WHERE Extract(YEAR from article_date)={0}'
    cur.execute(SQL.format(year))
    for i in range(number):
        article = cur.fetchone()
        articles.append(article[0])

    return articles, number


def replacesymbols(article):
    article = article.replace('.', '')
    article = article.replace(',', '')
    article = article.replace('!', '')
    article = article.replace('?', '')
    article = article.replace('—', '')
    article = article.replace('=', '')
    article = article.replace('+', '')
    article = article.replace('-', '')
    article = article.replace('/', '')
    article = article.replace('\\', '')
    article = article.replace(';', '')
    article = article.replace(':', '')
    article = article.replace('^', '')
    article = article.replace('&', '')
    article = article.replace('*', '')
    article = article.replace('[', '')
    article = article.replace(']', '')
    article = article.replace('{', '')
    article = article.replace('}', '')
    article = article.replace('(', '')
    article = article.replace(')', '')
    article = article.replace('<', '')
    article = article.replace('>', '')
    article = article.replace('"', '')
    article = article.replace("'", '')
    article = article.replace('~', '')
    article = article.replace('$', '')
    article = article.replace('|', '')
    return article


def plottopicpop():
    internet = [0 for i in range(10)]
    developing = [0 for i in range(10)]
    habr = [0 for i in range(10)]
    n = 0
    for year in range(2006, 2016):
        articles, numberofarticles = getarticlesbyyear(year)
        print("Got articles for", str(year))
        # Normalaize texts
        i = 0
        for article in articles:
            article = replacesymbols(article)
            articles[i] = normalaisestr(article.lower())
            i += 1
        print('Normalaised')
        
        # Remove unnecessary words
        texts = [[word for word in article if word not in stoplist]
                 for article in articles]
        print('Deleted stopwords')
        dictionary = corpora.Dictionary(texts)
        corpus = [dictionary.doc2bow(text) for text in texts]
        print('Starting training')
        # Щадящий режим для ОЗУ
        for i in range(numberofarticles // 100):
            begin = 100 * i
            end = 100 * (i + 1)
            if end > numberofarticles:
                end = numberofarticles
            lda = LdaModel(corpus[begin:end:], id2word=dictionary, num_topics=end - begin)

            for j in range(lda.num_topics):
                topics = lda.get_topic_terms(j, 15)
                # print(topics)
                for topic in topics[0]:
                    top = dictionary.get(topic)
                    # print(top)
                    if "интернет" == top:
                        internet[n] += 1
                    if "разработка" == top:
                        developing[n] += 1
                    if "хабра" == top:
                        habr[n] += 1
            del lda
        n += 1

        print(internet,'\n', developing, '\n', habr)

    plt.title('Population of 3 topics.')
    plt.xlabel('Year 2006 - 2015')
    plt.ylabel('Number of articles')
    plt.plot(internet, label="Интернет")
    plt.plot(developing, label="Разработка")
    plt.plot(habr, label="Хабра")
    plt.legend()
    plt.show()


gc.enable()

db = psycopg2.connect(database='', user='', host='', port=)

cur = db.cursor()

morph = pymorphy2.MorphAnalyzer()

stoplist = ["из", "из", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "a", "b",
            "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n",
            "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
            "а", "б", "в", "г", "д", "е", "ё", "ж", "з", "и", "л", "м", "н", "о",
            "п", "р", "с", "т", "у", "ф", "х", "ц", "ш", "щ", "ъ", "ь", "э", "ю", "я",
            "большой", "бы", "быть", "весь", "вот", "все",
            "всей", "вы", "говорить", "год", "да", "для", "до", "еще",
            "же", "знать", "и", "из", "к", "как", "который", "мочь",
            "мы", "на", "наш", "не", "него", "нее", "нет", "них", "но",
            "о", "один", "она", "они", "оно", "оный", "от", "ото", "по",
            "с", "свой", "себя", "сказать", "та", "такой", "только", "тот",
            "ты", "у", "что", "это", "этот", "я", "без", "более", "больше",
            "будет", "будто", "бы", "был", "была", "были", "было", "быть",
            "вам", "вас", "ведь", "весь", "вдоль", "вдруг", "вместо",
            "вне", "вниз", "внизу", "внутри", "во", "вокруг", "вот",
            "впрочем", "все", "всегда", "всего", "всех", "всю", "вы",
            "где", "да", "давай", "давать", "даже", "для", "до",
            "достаточно", "другой", "его", "ему", "ее", "её", "ей", "если",
            "есть", "ещё", "еще", "же", "за", "здесь",
            "из", "изза", "из", "или", "им", "иметь", "иногда", "их",
            "както", "кто", "когда", "кроме", "кто", "куда", "ли", "либо",
            "между", "меня", "мне", "много", "может", "мое", "моё", "мои",
            "мой", "мы", "на", "навсегда", "над", "надо", "наконец", "нас",
            "наш", "не", "него", "неё", "нее", "ней", "нет", "ни",
            "нибудь", "никогда", "ним", "них", "ничего", "но", "ну", "об",
            "однако", "он", "она", "они", "оно", "опять", "от", "отчего",
            "очень", "перед", "по", "под", "после", "потом", "потому",
            "потому что", "почти", "при", "про", "раз", "разве", "свою",
            "себя", "сказать", "снова", "с", "со", "совсем", "так", "также",
            "такие", "такой", "там", "те", "тебя", "тем", "теперь",
            "то", "тогда", "того", "тоже", "той", "только", "том", "тот",
            "тут", "ты", "уже", "хоть", "хотя", "чего", "чегото", "чей",
            "чем", "через", "что", "чтото", "чтоб", "чтобы", "чуть",
            "чьё", "чья", "эта", "эти", "это", "эту", "этого", "этом",
            "этот", "к", "около", "будут", "нас", "нам", "например",
            "пока", "чаще", "to", "other", "you", "is", "was", "were",
            "the", "того", "которые", "то", "свое", "сами", "можно",
            "всем", "этому", "сколько"]
# TODO: Make everything work in different threads

# Uncomment necessary func

# top5tags()
# articlesbydow()
# ldaforhabr()
plottopicpop()