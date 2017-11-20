import requests
from multiprocessing import Queue
from tkinter import messagebox, Tk
from tkinter.ttk import Label, Button, Entry, Progressbar, Frame
import tkinter.font as tkFont
from helper import *


class FrameUI(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.pack()
        self.parent = parent
        self.parent.title('CKStrReplace')
        st = tkFont.Font(family='song ti', size=12)

        self.set_account_frame(st)
        self.set_url_frame(st)
        self.set_page_frame(st)
        self.bar = Progressbar(self, orient="horizontal",
                               mode="determinate")
        self.bar.pack(fill='x')
        self.progress_label = Label(self, text='', anchor='center', font=st)
        self.progress_label.pack(fill='x')

    def set_account_frame(self, st):
        account_frame = Frame(self)
        account_frame.pack(fill='x', expand=1, pady=5)

        id_label = Label(account_frame, text='帳號：', font=st)
        id_label.pack(side='left')
        self.id_entry = Entry(account_frame)
        self.id_entry.pack(side='left')

        pw_label = Label(account_frame, text='密碼：', font=st)
        pw_label.pack(padx=5, side='left')
        self.pw_entry = Entry(account_frame, show='*')
        self.pw_entry.pack(side='left')

    def set_url_frame(self, st):
        url_frame = Frame(self)
        url_frame.pack(fill='x', expand=1, pady=5)

        url_label = Label(url_frame, text='網址：', font=st)
        url_label.pack(side='left')
        self.url_entry = Entry(url_frame)
        self.url_entry.pack(side='left', fill='x', expand=1)

    def set_page_frame(self, st):
        page_frame = Frame(self)
        page_frame.pack(fill='x', expand=1, pady=5)

        title_label = Label(page_frame, text='頁數：', font=st)
        title_label.pack(side='left')
        self.p1_entry = Entry(page_frame, width=8)
        self.p1_entry.pack(side='left')
        range_label = Label(page_frame, text='~', font=st)
        range_label.pack(side='left')
        self.p2_entry = Entry(page_frame, width=8)
        self.p2_entry.pack(side='left')

        self.send = Button(page_frame, text='send', command=self.click_send)
        self.send.pack(side='right')

    def click_send(self):
        success, infoDic = self.checkdata()
        if not success:
            messagebox.showerror('錯誤', '請檢查各欄位是否填寫正確')
            return

        self.send.config(state="disabled")
        self.start(infoDic)

    def checkdata(self):
        # p1, p2不防呆
        account = self.id_entry.get().strip()
        password = self.pw_entry.get().strip()
        url = self.url_entry.get().strip()
        tid = checkurl(url)
        p1 = str2int(self.p1_entry.get().strip())
        p2 = str2int(self.p2_entry.get().strip())

        if account is '' or password is '' or not tid or p1 is -1 or p2 is -1:
            return False, {}
        else:
            with open('data.txt', 'r') as f:
                strdb = [n[:-1].split('->') for n in f.readlines()]

            infoDic = {
                'tid': tid,
                'strdb': strdb,
                'idStr': account,
                'pwStr': password,
                'limit': (p1, p2)
            }
            return True, infoDic

    def start(self, infoDic):
        # Start a session so we can have persistant cookies
        session = requests.session()
        agent = {'user-agent': 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'}

        success, errMsg = login(session, agent, infoDic)
        if not success:
            messagebox.showerror('登入失敗', errMsg)
            self.send.config(state="active")
            return

        with open('failure.txt', 'w') as f:
            f.write('')

        p1, p2 = infoDic['limit']
        self.progress_label['text'] = ''
        maximum = p2 - p1 + 1
        self.bar['value'] = 0
        self.bar['maximum'] = maximum

        # 怕高頻率的修改CK會ban，就不做平行迴圈了
        showdone = True
        for i in range(p1, p2 + 1):
            url = composeURL(infoDic['tid'], i)
            editable = findTarget(session, agent, url, infoDic['strdb'])
            if editable:
                now = i - p1 + 1
                self.progress_label['text'] = '{}/{}'.format(now, maximum)
                self.bar['value'] = now
                self.update()
            else:
                messagebox.showerror('錯誤', '你似乎沒有修改權限喔')
                showdone = False
                break

        # all done
        self.send.config(state="active")
        self.bar['value'] = 0
        self.update()
        if showdone:
            messagebox.showinfo(message='修改完成')


if __name__ == '__main__':
    root = Tk()
    root.resizable(0, 0)
    root.geometry("440x140")  # wxh
    app = FrameUI(root)
    app.mainloop()
