import urllib.request
import time

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

'''habrahabr redirects to geektimes/megamozg automatically'''
urlbase = 'http://habrahabr.ru/post/'
for i in range(1, 271605):
    time.sleep(1)
    url = urlbase + str(i)
    downloadpage(url)