# -*- coding: utf-8 -*-
# １つのファイルを任意のバイト数に分割して送受信できるプログラム
# 実行方法は robust/sample 内にこのプログラムファイルを置いて
# 受信側(例) python3 sampleYoshimi.py s ***.***.***.*** 8000　（ipは受信側のipにすること）
# 送信側(例) python3 sever.py c ***.***.***.*** 8000　（ipは受信側のipにすること）

# 設計思想
# 一回に送信するデータが小さければジャマーあっても送受信なんとかなるので
# ファイルをある程度のバイト数に分割して最後にくっつければいいよね的なやつ
# あと、性能よりも極力コード量を減らすように意識した(githubのサンプルコードより読みやすいのを目標にした)

# 動作
# Taro → Hanako はジャミングしてても速いけど、Hanako → Taro はばらつきあるけどかなり遅くなる

# Reference
# 1.Python で Socket 通信 (TCP/UDP サーバ)    https://qiita.com/tick-taku/items/813710328d802829fb4b
# 2.テキストファイルを指定バイト数ごとに分割  https://qiita.com/igarashi_54/items/b879331925a6f76fb00c
# 3.pythonですぐ出来る！ ファイルを転送する方法【TCP通信 応用】
#   https://syachiku-python.com/python%E3%81%A7%E3%81%99%E3%81%90%E5%87%BA%E6%9D%A5%E3%82%8B%EF%BC%81-%E3%83%95%E3%82%A1%E3%82%A4%E3%83%AB%E3%82%92%E8%BB%A2%E9%80%81%E3%81%99%E3%82%8B%E6%96%B9%E6%B3%95%E3%80%90tcp%E9%80%9A%E4%BF%A1/

import os
import socket
import sys
import time

split_byte_size = 128  # 分割するバイト数(ここも適切な値見つけて下さい)

# ここには 102400/split_byte_size * 1000 の値を入れると事足ります。
sys.setrecursionlimit(800000)


def count_files_in_dir(path: str) -> int:
    return sum(os.path.isfile(os.path.join(path, name)) for name in os.listdir(path))


def split_text_by_byte_size(text, split_byte_size):  # ファイルを任意のバイト数に分割する関数
    bytes_text = text  # １つのファイルの全てのデータ取得
    head = bytes_text[:split_byte_size]  # データの先頭から指定した任意のバイト数のデータを取得
    tail = text[len(head) :]  # 分割されていない残りのデータ

    if tail == text:  # 残りのデータが指定したバイト数より小さければ分割しない
        return []

    split_tail = split_text_by_byte_size(tail, split_byte_size)  # データの分割が終わるまで繰り返す（再起）

    results = []  # 分割したデータを格納する変数
    results.append(head)  # 分割したデータを格納
    results.extend(split_tail)  # 最後のデータを格納

    return results


def server(ip, port):
    with socket.socket(
        socket.AF_INET, socket.SOCK_STREAM
    ) as s:  # アドレスファミリをIPv4(AF_INET),ソケットタイプをTCP(SOCK_STREAM)に指定
        s.bind((ip, port))  # ソケットをバインド
        s.listen(1)

        # while True:
        conn, _ = s.accept()
        with conn:

            for i in range(0, count_files_in_dir("./data/send")):
                fname = os.path.join("./data/receive", f"data{i}")
                print(fname)
                # この行にfor 文でdata0からdata999のファイルを取得できるように書く
                # fname = f"../data/data0"  # 受信したファイルのパスを指定。ここではdata0を送るようにしている(一行上でfor文を使う場合、少し変更する必要あり)

                with open(fname, mode="ab") as f:  # ファイルをバイナリモード(書き込み可)で開く
                    size = 0
                    while True:
                        data = conn.recv(split_byte_size)  # 分割されて送られてきたデータを変数"data"に格納
                        size += len(data)  # 送られてきたデータサイズを足し算
                        f.write(data)  # 変数 data の内容をファイルに書き込む

                        # ===== この下にsize == 102400 の場合の処理と size != 102400の場合の処理(failedのファイル数増やさないためにもプログラムを終了させる、再送要求するなど戦略によって変わります)を書く
                        # なおこのサンプルではsize >= 102400 以上のときのプログラムを書いておきます
                        if size == 102400:
                            print(size)
                            break  # 次のファイルの受信、書き込みに移る
                        # =================================================


def client(ip, port):
    with socket.socket(
        socket.AF_INET, socket.SOCK_STREAM
    ) as s:  # アドレスファミリをIPv4(AF_INET),ソケットタイプをTCP(SOCK_STREAM)に指定
        s.connect((ip, port))  # サーバ(受信側)に接続

        for i in range(0, count_files_in_dir("./data/send")):
            fname = os.path.join("./data/send", f"data{i}")
            # この行にfor 文でdata0からdata999のファイルを取得できるように書く
            # fname = f"../data/data0"  # 受信したファイルのパスを指定。ここではdata0を送るようにしている(一行上でfor文を使う場合、少し変更する必要あり)

            print(fname)
            try:
                with open(fname, mode="rb") as f:  # ファイルをバイナリモード(読み取り可)で開く
                    text = f.read()  # ファイルのデータを取得
                    split_texts = split_text_by_byte_size(
                        text, split_byte_size
                    )  # ファイルを指定したバイト数で取得

                    # ======= 分割した数だけ送信する==================
                    for i, split_text in enumerate(split_texts):
                        # print(i)             #データの分割数を確認できる
                        s.sendall(split_text)  # 分割したデータを送信する
                        time.sleep(
                            0.001
                        )  # ここの値は試験しながら最適な値を見つけて下さい（戦略でここの行をコメントアウトしてもらっても構いません
                    # ================================================
            except:
                pass


if __name__ == "__main__":
    if sys.argv[1] == "s":  # server(受信モード)
        server((sys.argv[2]), int(sys.argv[3]))  # ip, port取得
    if sys.argv[1] == "c":  # client(送信モード)
        client((sys.argv[2]), int(sys.argv[3]))
