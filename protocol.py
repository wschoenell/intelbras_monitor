# Intelbras AMT 2018 protocol parser.
# This parser was developed by reverse engineering the communication protocol between the alarm system and its software
import binascii
import csv
import datetime

# load event description files
with open("events.txt") as fp:
    events_desc = {int(a[0]): a[1] for a in csv.reader(fp, delimiter=",")}

decode_numbers = lambda p: "".join([str(a)[-1] for a in p])


def parser_amt2018(packet):
    return dict(ip=packet[2] - 0x10,
                account=decode_numbers(packet[3:7]),
                event=int(decode_numbers(packet[9:13])),
                event_desc=events_desc[int(decode_numbers(packet[9:13]))],
                partition=decode_numbers(packet[13:15]),
                user=decode_numbers(packet[15:18]),
                datetime=datetime.datetime(2000 + packet[20], packet[19], packet[18], packet[21], packet[22],
                                           packet[23])
                )


def parse_amt2018_mac(packet):
    return binascii.hexlify(packet[2:-1]).decode()
