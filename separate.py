from grab import Grab
import psycopg2
import os
import urllib.request
import time
import gc


def downloadpage(url):
    for j in range(1, 6):
        try:
            html = urllib.request.urlopen(url).read()
        except urllib.request.HTTPError:
            try:
                html = urllib.request.urlopen(url).read()
            except Exception as e:
                # html = 'Error 404'
                f = open(str(i) + '.html', 'wb')
                f.close()
                if e.code:
                    print("Error " + str(e.code) + ": " + url)
                break
            else:
                f = open(str(i) + '.html', 'wb')
                f.write(html)
                f.close()
                print("Downloaded: " + url)
                break
        except Exception:
            print ("Waiting " + str(5 * j) + " seconds...")
            time.sleep(5 * j)
        else:
            f = open(str(i) + '.html', 'wb')
            f.write(html)
            f.close()
            print("Downloaded: " + url)
            break


def debugoutput():
    global header
    global topic
    global author
    global raiting
    global date
    global numberoftags
    global tags
    print(header)
    print(topic)
    print(author)
    print(raiting)
    print(date)
    print(numberofcomments)
    print(tags)


def authoradd(a):
    SQL = "SELECT author_table.author_id FROM author_table WHERE author_table.author_nick='{0}'"
    cur.execute(SQL.format(a))
    ans = cur.fetchone()
    if ans is None:
        SQL = "INSERT INTO author_table(author_nick) VALUES ('{0}')"
        cur.execute(SQL.format(a))
        SQL = "SELECT author_table.author_id FROM author_table WHERE author_table.author_nick='{0}'"
        cur.execute(SQL.format(a))
        ans = cur.fetchone()

    authorid = int(ans[0])
    return authorid


def tagadd(t):
    t = t.replace("'", '')
    SQL = "SELECT tag_table.tag_id FROM tag_table WHERE tag_table.tag_name='{0}'"
    cur.execute(SQL.format(t))
    ans = cur.fetchone()
    if ans is None:
        SQL = '''INSERT INTO tag_table(tag_name) VALUES ('{0}')'''
        cur.execute(SQL.format(t))
        SQL = "SELECT tag_table.tag_id FROM tag_table WHERE tag_table.tag_name='{0}'"
        cur.execute(SQL.format(t))
        ans = cur.fetchone()
    tagid = int(ans[0])
    return tagid


def formatdate(d):
    # print(d)
    dd, mm, yyyy = d.split(' ', 2)
    yyyy = yyyy[:4:]
    try:
        int(yyyy)
    except:
        yyyy = '1970'
        if i > 247197:
            yyyy = '2015'

    mounth = {'января': '01',
              'февраля': '02',
              'марта': '03',
              'апреля': '04',
              'мая': '05',
              'июня': '06',
              'июля': '07',
              'августа': '08',
              'сентября': '09',
              'октября': '10',
              'ноября': '11',
              'декабря': '12'}
    mm = mounth[mm]
    newdate = yyyy + '-' + mm + '-' + dd
    return newdate


def getheader():
    try:
        header = g.doc.select('//h1[@class="title"]').text()
    except:
        try:
            header = g.doc.select('//span[@class="post_title"]').text()
        except:
            header = g.doc.select('//h1[@class="megapost-head__title"]').text()
        finally:
            return header
    finally:
        return header


def gettopic():
    try:
        topic = g.doc.select('//div[@class="content html_format"]').text()
    except:
        topic = g.doc.select('//div[@class="content-text"]').text()
    return topic


def getauthor():
    try:
        author = g.doc.select('//*[@class="author-info__nickname"]').text()
    except:
        try:
            author = g.doc.select('//*[@class="author-info__name"]').text()
        except:
            author = g.doc.select('//*[@class="megapost-cover__blog-link"]').text()
    if author[0] == '@':
        author = author[1::]
    return author


def getraiting():
    try:
        raitingstr = g.doc.select('//span[@class="voting-wjt__counter-score js-score"]').text()
    except:
        raiting = 0
    else:
        if raitingstr[0] == '–':
            raitingstr = '-' + raitingstr[1::]
        raiting = int(raitingstr)
    return raiting


def getdate():
    try:
        date = g.doc.select('//div[@class="published"]').text()
    except:
        date = g.doc.select('//ul[@class="list list_inline"]/li[@class="list__item"][1]').text()
    return formatdate(date)


def fillarticletable():
    SQL = """INSERT INTO article_table(\
    article_id, article_head, article_topic, article_rating, author_id, article_date)\
    VALUES (%s, %s, %s, %s, %s, %s)"""
    cur.execute(SQL, (i, header, topic, raiting, author_id, date))


def gettags():
    tags = g.doc.select('//ul[@class="tags"]').text_list()
    if not tags:
        tags = g.doc.select('//ul[@class="tags icon_tag"]').text_list()
    return tags


def filltagstable():
    if tags:
        for j in tags[0].split(', '):
            j.lower()
            # print(j)
            tag_id = tagadd(j)
            SQL = '''INSERT INTO tag_to_article_table(tag_id, article_id) VALUES (%s, %s)'''
            cur.execute(SQL, (tag_id, i))


def getnumberofcomments():
    try:
        numberofcomments = g.doc.select('//span[@id="comments_count"]').text()
        return numberofcomments
    except:
        return 0

def fillnumberofcomments():
    SQL = '''UPDATE article_table SET article_comments_number = {0} WHERE article_id={1}'''
    cur.execute(SQL.format(numberofcomments, i))


def fillcommentstable():
    j = 1
    while True:
        # Comment id
        # print(j)
        try:
            commentid = g.doc.select('//div[@class="comment_item"][{0}]/@id'.format(j)).text()[8::]
            # print(commentid)
        except:
            # print("No comments")
            break

        # Comment text
        try:
            commenttext = g.doc.select('//div[@id="comment_{0}"]/div[@class="comment_body "]\
                                    /div[@class="message html_format "]'.format(commentid)).text()
            # print(commenttext)
        except:
            # Only in case of UFO (author banned)
            j += 1
            continue

        # Comment parent
        try:
            commentparent = g.doc.select('//div[@id="comment_{0}"]/span[@class="parent_id"]\
                                        /@data_parent_id'.format(commentid)).text()
        except:
            # In case of root comment
            commentparent = 0
        # finally:
            # print(commentparent)

        # Comment author
        try:
            commentauthor = g.doc.select('//div[@rel="{0}"]/a[@class="comment-item__username"]'.format(commentid)).text()
        except:
            commentauthor = g.doc.select('//div[@rel="{0}"]/a[@class="username"]'.format(commentid)).text()
        finally:
            commentauthorid = authoradd(commentauthor)
            # print(commentauthor)

        # DB filling

        SQL = '''INSERT INTO comments_table\
            (comment_id, comment_text, comment_parent_id, comment_article_id, comment_author_id)\
            VALUES (%s, %s, %s, %s, %s);'''
        cur.execute(SQL, (commentid, commenttext, commentparent, i, commentauthorid))
        j += 1


# MAIN
gc.enable()

db = psycopg2.connect(database='', user='', host='', port=)

cur = db.cursor()
# os.chdir('')
g = Grab

for i in range(258593, 268278):    # 268278
    print(i)
    try:
        if os.path.getsize(str(i) + '.html') < 5500:  # Draft or 404 Error
            continue
    except FileNotFoundError:
        print('File {0}.html not found.\nTrying to download.'.format(str(i)))
        url = 'http://habrahabr.ru/post/' + str(i)
        downloadpage(url)
        if os.path.getsize(str(i) + '.html') < 5500:  # Draft or 404 Error
            continue
    f = open(str(i) + '.html', 'rb')
    g = Grab(f.read())
    f.close()
    try:
        g.doc.select('//title').text()
    except:
        url = 'http://habrahabr.ru/post/' + str(i)
        downloadpage(url)
        if os.path.getsize(str(i) + '.html') < 5500:  # Draft or 404 Error
            continue
        f = open(str(i) + '.html', 'rb')
        g = Grab(f.read())
        f.close()
    # Header
    header = getheader()

    # Topic
    topic = gettopic()

    # Author
    author = getauthor()
    author_id = authoradd(author)

    # Raiting
    raiting = getraiting()

    # Publishing date
    date = getdate()

    # Filling article table
    fillarticletable()

    # Tags
    tags = gettags()
    filltagstable()

    # Comments
    numberofcomments = getnumberofcomments()
    fillnumberofcomments()
    if int(numberofcomments) > 0:
        fillcommentstable()

    db.commit()
    # gc.collect()
    # debugoutput()
