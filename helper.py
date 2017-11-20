import hashlib
from bs4 import BeautifulSoup as bs
import re

def pwhash(origin):
    # password hash
    md5 = hashlib.md5()
    md5.update(origin.encode('utf-8'))
    return md5.hexdigest()


def checkurl(urlStr):
    # https://ck101.com/thread-3885080-1-1.html
    # https://ck101.com/forum.php?mod=viewthread&tid=3434923&page=13
    # https://ck101.com/forum.php?mod=viewthread&tid=3434923&page=13&extra=#pid99055328
    if urlStr.startswith('https://ck101.com/thread'):
        tid = urlStr.split('-')[1]
    elif urlStr.startswith('https://ck101.com/forum.php?'):
        tid = urlStr.split('&')[1][4:]
    else:
        tid = None

    return tid

def str2int(num):
    try:
        return int(num)
    except ValueError:
        return -1

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
        new = '' if strs[1] is '!@#$' else strs[1]
        content = content.replace(strs[0], new)

    hashid = getValue(data, 'formhash')
    posttime = getValue(data, 'posttime')
    delattachop = getValue(data, 'delattachop')
    wysiwyg = getValue(data, 'wysiwyg')
    fid = getValue(data, 'fid')
    tid = getValue(data, 'tid')
    pid = getValue(data, 'pid')
    page = getValue(data, 'page')
    subject = getValue(data, 'subject')
    editurl = 'https://ck101.com/forum.php?mod=post&action=edit&extra=&editsubmit=yes'
    typeid = ''

    select = data.find('select', attrs={'name': 'typeid'})
    if select:
        for option in select.find_all('option'):
            try:
                _ = option['selected']
                typeid = option['value']
                break
            except KeyError:
                continue

    body = {
        'formhash': hashid,
        'posttime': posttime,
        'delattachop': delattachop,
        'wysiwyg': wysiwyg,
        'fid': fid,
        'tid': tid,
        'pid': pid,
        'page': page,
        'subject': subject,
        'checkbox': 0,
        'message': content,
        'usesig': 1,
        'delete': 0,
        'save': '',
        'uploadalbum': -2,
        'newalbum': '請輸入相冊名稱'
    }

    if typeid is not '':
        body['typeid'] = typeid

    edit = session.post(editurl, data=body, headers=agent)
    if '帖子編輯成功' not in edit.text:
        with open('failure.txt', 'a') as f:
            f.write('https://ck101.com/forum.php?mod=viewthread&tid={}&page={}#pid{}\n'.format(tid, page, pid))


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
            try:
                editUrl = 'https://ck101.com/' + article.find('a', attrs={'class': 'operateBtn editp'})['href']
                modify(session, agent, editUrl, shot)
            except TypeError:
                return False

    return True