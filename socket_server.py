import ast
import binascii
import datetime
import socket
import threading
from configparser import ConfigParser, NoSectionError

import requests

from protocol import parser_amt2018, parse_amt2018_mac

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(("0.0.0.0", 9009))
sock.listen(5)


def client_thread(connection):
    sock = connection[0]
    # recv header
    data = sock.recv(9)
    # print("Received: " + binascii.hexlify(data).decode())
    sock.send(bytes.fromhex("fe"))
    sock.send(bytes.fromhex("01c43a"))
    packet = sock.recv(9)
    sock.send(bytes.fromhex("fe"))
    print(binascii.hexlify(packet))
    mac = parse_amt2018_mac(packet)
    print("MAC ADDR: " + mac)
    last_ping = datetime.datetime.now()

    try:
        name = config.get(mac, "name")
        users = ast.literal_eval(config.get(mac, "users"))
        if config.has_option(mac, "bot_token") and config.has_option(mac, "bot_chatid"):
            bot = "https://api.telegram.org/bot%s/sendMessage?chat_id=%s&text=" % (config.get(mac, "bot_token"),
                                                                                   config.get(mac, "bot_chatid"))
        else:
            bot = None

    except NoSectionError:
        name = ""
        users = {}
        bot = None

    while True:
        r = sock.recv(1)
        if len(r) > 0:
            # print(r)
            if r == bytes.fromhex("f7"):
                print("fe")
                sock.send(bytes.fromhex("fe"))
                last_ping = datetime.datetime.now()
            else:
                r += sock.recv(30)
                print("data: " + binascii.hexlify(r).decode())
                print("fe")
                sock.send(bytes.fromhex("fe"))
                if len(r) == 31:
                    decoded = parser_amt2018(r)
                    decoded["name"] = name
                    if int(decoded["user"]) in users:
                        decoded["user"] = users[int(decoded["user"])]
                    print("data decoded:" + str(decoded) + decoded["datetime"].isoformat())
                    msg = "{name}: usuário {user} - {event_desc} - partição {partition} - ".format(**decoded) + decoded[
                        "datetime"].isoformat()
                    print(msg)
                    if bot:
                        print(bot + msg)
                        print(requests.get(bot + msg))


if __name__ == "__main__":

    # Read configuration
    config = ConfigParser()
    config.read("config.ini")

    threads = []
    while True:
        connection = sock.accept()
        print("Connected", connection)
        t = threading.Thread(target=client_thread, args=(connection,))
        t.start()
        threads.append(t)
