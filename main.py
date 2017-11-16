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

def leaderStr():
    leader = """
    ------WebKitFormBoundaryIvQoJyA7syjz1oMt
    Content-Disposition: form-data; name="formhash"

    {}
    ------WebKitFormBoundaryIvQoJyA7syjz1oMt
    Content-Disposition: form-data; name="posttime"

    {}
    ------WebKitFormBoundaryIvQoJyA7syjz1oMt
    Content-Disposition: form-data; name="delattachop"

    {}
    ------WebKitFormBoundaryIvQoJyA7syjz1oMt
    Content-Disposition: form-data; name="wysiwyg"

    {}
    ------WebKitFormBoundaryIvQoJyA7syjz1oMt
    Content-Disposition: form-data; name="fid"

    {}
    ------WebKitFormBoundaryIvQoJyA7syjz1oMt
    Content-Disposition: form-data; name="tid"

    {}
    ------WebKitFormBoundaryIvQoJyA7syjz1oMt
    Content-Disposition: form-data; name="pid"

    {}
    ------WebKitFormBoundaryIvQoJyA7syjz1oMt
    Content-Disposition: form-data; name="page"

    {}
    ------WebKitFormBoundaryIvQoJyA7syjz1oMt
    Content-Disposition: form-data; name="typeid"

    3115
    ------WebKitFormBoundaryIvQoJyA7syjz1oMt
    Content-Disposition: form-data; name="subject"

    測試
    ------WebKitFormBoundaryIvQoJyA7syjz1oMt
    Content-Disposition: form-data; name="checkbox"

    0
    ------WebKitFormBoundaryIvQoJyA7syjz1oMt
    Content-Disposition: form-data; name="message"
    """

def getValue(data, name):
    return data.find('input', attrs={'name': name})['value']

def modify(session, agent, url, old, new):
    rawdata = session.get(url, headers=agent)
    data = bs(rawdata.text, 'lxml')
    content = data.find('textarea').text.replace(old, new)

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

def findTarget(session, agent, url, old, new):
    pagedata = session.get(url, headers=agent)
    if old not in pagedata.text:
        return

    data = bs(pagedata.text, 'lxml')
    for article in data.find_all('div', class_='plhin'):
        content = article.find('td', class_='t_f')
        if old not in content.text:
            continue

        # pid = content['id'][12::]
        editUrl = 'https://ck101.com/' + article.find('a', attrs={'class':'operateBtn editp'})['href']
        modify(session, agent, editUrl, old, new)
        print('d')
    print('d')

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
        findTarget(session, agent, url, infoDic['old'], infoDic['new'])
    print('d')


if __name__ == '__main__':
    infoDic = {
        'tid': '4226739',
        'old': '鄭咤',
        'new': '王小名',
        'idStr': '',
        'pwStr': '',
        'limit': (1, 1)
    }

    start(infoDic)