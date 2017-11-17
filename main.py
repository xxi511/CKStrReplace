import requests
import hashlib
from bs4 import BeautifulSoup as bs
import re

def pwhash(origin):
    # password hash
    md5 = hashlib.md5()
    md5.update(origin.encode('utf-8'))
    return md5.hexdigest()

def checkurl(self):
    # https://ck101.com/thread-3885080-1-1.html
    # https://ck101.com/forum.php?mod=viewthread&tid=3434923&page=13
    # https://ck101.com/forum.php?mod=viewthread&tid=3434923&page=13&extra=#pid99055328
    urlStr = self.urlEntry.get()
    if urlStr.startswith('https://ck101.com/thread'):
        tid = urlStr.split('-')[1]
    elif urlStr.startswith('https://ck101.com/forum.php?'):
        tid = urlStr.split('&')[1][4:]
    else:
        tid = None

    return tid if tid else None

def login(session, agent, infoDic):
    '''
    CK login
    :param session: session
    :param agent: user agent
    :param infoDic: user info dic
    :return: tuple, (success, errMsg)
    '''
    hashedPW = pwhash(infoDic['pwStr'])
    login_data = {
        'username': infoDic['idStr'],
        'password': hashedPW,
        'quickforward': 'yes',
        'handlekey': 'ls'
    }

    loginUrl = 'https://ck101.com/member.php?mod=logging&action=login&loginsubmit=yes&infloat=yes&lssubmit=yes&inajax=1'
    login = session.post(loginUrl, data=login_data, headers=agent)
    resp = login.text
    if '歡迎您回來' in resp:
        return True, ''
    else:
        find = re.findall("CDATA\[.*<script type=", resp, re.U)[0]
        return False, find[6:-13]

def composeURL(tid, page):
    return 'https://ck101.com/thread-{}-{}-1.html'.format(tid, page)

def getValue(data, name):
    return data.find('input', attrs={'name': name})['value']

def modify(session, agent, url, shot):
    rawdata = session.get(url, headers=agent)
    data = bs(rawdata.text, 'lxml')
    content = data.find('textarea').text
    for strs in shot:
        content = content.replace(strs[0], strs[1])

    hashid = getValue(data, 'formhash')
    posttime = getValue(data, 'posttime')
    delattachop = getValue(data, 'delattachop')
    wysiwyg = getValue(data, 'wysiwyg')
    fid = getValue(data, 'fid')
    tid = getValue(data, 'tid')
    pid = getValue(data, 'pid')
    page = getValue(data, 'page')
    subject = getValue(data, 'subject')
    # checkbox, message
    editurl = 'https://ck101.com/forum.php?mod=post&action=edit&extra=&editsubmit=yes'


    print('d')

def findTarget(session, agent, url, strdb):
    pagedata = session.get(url, headers=agent)
    data = bs(pagedata.text, 'lxml')

    for article in data.find_all('div', class_='plhin'):
        content = article.find('td', class_='t_f')
        shot = []
        for target in strdb:
            if target[0] in content.text:
                shot.append(target)

        if len(shot) > 0:
            editUrl = 'https://ck101.com/' + article.find('a', attrs={'class': 'operateBtn editp'})['href']
            modify(session, agent, editUrl, shot)


def start(infoDic):
    # Start a session so we can have persistant cookies
    session = requests.session()
    agent = {'user-agent': 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'}

    success, errMsg = login(session, agent, infoDic)
    if not success:
        print(errMsg)
        return

    p1, p2 = infoDic['limit']
    for i in range(p1, p2+1):
        url = composeURL(infoDic['tid'], 16)
        findTarget(session, agent, url, infoDic['strdb'])
    print('d')


if __name__ == '__main__':
    with open('data.txt', 'r') as f:
        strdb = [n[:-1:].split(' ') for n in f.readlines()]

    infoDic = {
        'tid': '4226739',
        'strdb': strdb,
        'idStr': '',
        'pwStr': '',
        'limit': (1, 1)
    }

    start(infoDic)
