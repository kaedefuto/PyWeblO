from pywebio.output import put_text
from pywebio.input import input, PASSWORD, FLOAT, TEXT
from pywebio.output import put_text, put_table

from pywebio.input import select, checkbox, radio, textarea, file_upload, input_group
from pywebio.output import put_markdown, put_table, put_buttons, put_image
from pywebio.session import hold

from pywebio.output import put_text, put_buttons, put_link
from pywebio.session import hold, go_app
from pywebio.platform.tornado import start_server

import sqlite3
import os

if not os.path.exists('./main.db'):
    dbname = 'main.db'
    conn = sqlite3.connect(dbname)
    cur = conn.cursor()
    cur.execute('CREATE TABLE items(user STRING PRIMARY KEY , name STRING)')
    cur.execute('CREATE TABLE todo(user STRING PRIMARY KEY , name STRING)')
    conn.close()


def sign_up():
    result = input_group("ログイン", [
        input("ユーザ名", type=TEXT, name="user"),
        input("パスワード", type=PASSWORD, name="path"),
        checkbox(options=['ログインを記憶する'], name="agree"),
    ])
    dbname = 'main.db'
    conn = sqlite3.connect(dbname)
    cur = conn.cursor()
    cur.execute('SELECT * FROM items')
    count=0
    for row in cur:
        if result['user']==row[0] and result['path']==row[1]:
            count=1
    if count==1:
        put_text('ログインが完了しました')
        put_buttons(['start'], [lambda: go_app('main', new_window=False)])
        hold()
    else:
        put_text('パスワードが一致しません')
        put_buttons(['sign_in'], [lambda: go_app('sign_in', new_window=False)])
        hold()
    conn.close()

def sign_in():
    result = input_group("アカウント登録", [
        input("ユーザ名", type=TEXT, name="user"),
        select('性別', ['選択してください','男性', '女性', 'どちらでもない'], name="gender"),
        input("パスワード", type=PASSWORD, help_text='（8字以上）他で利用していないもの', name="path"),
        input("パスワード（確認用）", type=PASSWORD, name="path_c"),
        checkbox("アプリに同意", options=['アプリに同意します'], name="agree"),
    ])


    if len(result['agree'])==0 or len(result['user'])==0 or len(result['path'])==0 or len(result['path_c']) == 0 or len(result['gender']) == 8:
        put_text('アカウント登録に失敗しました')
        put_buttons(['sign_in'], [lambda: go_app('sign_in', new_window=False)])
        hold()

    elif result['path'] == result['path_c']:
        put_text('アカウント登録が完了しました')
        dbname = 'main.db'
        conn = sqlite3.connect(dbname)
        cur = conn.cursor()
        cur.execute('INSERT INTO items values(?, ?)',(result['user'],result['path']))
        conn.commit()
        conn.close()
        put_buttons(['sign_up'], [lambda: go_app('sign_up', new_window=False)])
        hold()

    else:
        put_text('パスワードが一致しません')
        put_buttons(['sign_in'], [lambda: go_app('sign_in', new_window=False)])
        hold()


def register():
    put_text('Todoアプリ')
    result = input_group(
        "登録",
        [
            #select('選択', ['正解', '不正解'], name="war"),
            #checkbox("チェックボックス", options=['適当'], name="agree"),
            #radio("ラジオボタン", options=['1','2'], name="answer"),
            input("タイトル", type=TEXT, name="title"),
            textarea('テキスト', rows=3, placeholder='Some text',name="text"),
            #file_upload("Select a image:", accept="image/*", name="img")
        ])
    put_table([
        ["この内容で登録しました", ""],
        ["タイトル", result["title"]],
        ["テキスト", result["text"]],
        ["",put_buttons(["OK"],onclick=lambda _: go_app('main', new_window=False))]
    ])
    dbname = 'main.db'
    conn = sqlite3.connect(dbname)
    cur = conn.cursor()
    cur.execute('INSERT INTO todo values(?, ?)',(result['title'],result['text']))
    conn.commit()
    conn.close()
    hold()

def delete():
    put_text('Todoアプリ')
    result = input_group(
        "削除",
        [
            input("タイトル", type=TEXT, name="title"),
        ])
    put_table([
        ["この内容を削除しました", ""],
        ["タイトル", result["title"]],
        ["",put_buttons(["OK"],onclick=lambda _: go_app('main', new_window=False))]
    ])
    dbname = 'main.db'
    conn = sqlite3.connect(dbname)
    cur = conn.cursor()
    sql = 'DELETE FROM todo where user = "{}"'.format(result['title'])
    cur.execute(sql)
    conn.commit()
    conn.close()
    hold()

def main():
    put_text('Todoアプリ')
    put_buttons(['登録'], [lambda: go_app('register', new_window=False)])
    put_buttons(['削除'], [lambda: go_app('delete', new_window=False)])
    put_text('一覧')

    dbname = 'main.db'
    conn = sqlite3.connect(dbname)
    cur = conn.cursor()
    try:
        cur.execute('SELECT * FROM todo')
        for row in cur:
            put_table([
            ["タイトル", row[0]],
            ["内容", row[1]],
            ])
        hold()
    except:
        print("")


def index():
    put_text('PyWebIOアプリ')
    put_link('ログイン', app='sign_up')
    put_text('')
    put_link('新規登録', app='sign_in')

start_server([index, main, sign_up, sign_in,register, delete], port=8080)