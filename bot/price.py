# -*- coding: utf-8 -*-
PRICE = [
    {
        "label": "IDR 23.000 : 1 Bulan",
        "price": {
            "qris": 23000,
            "trakteer": 23
        },
        "duration": 30
    },
    {
        "label": "IDR 130.000 : 6 Bulan",
        "price": {
            "qris": 130000,
            "trakteer": 130
        },
        "duration": 180
    },
    {
        "label": "IDR 276.000 : 1 Tahun",
        "price": {
            "qris": 276000,
            "trakteer": 276
        },
        "duration": 365
    }
]

PROMO_V1 = {
    "label": "IDR 18.000",
    "price": {
        "qris": 18000,
        "trakteer": 18
    },
    "duration": 30
}

PERMANENT = {
    "host_pilihan_v1": {
        "label": "LIVE RECORD : HOST PILIHAN",
        "price": {
            "default": {
                "price": 170000,
                "label": "IDR 170.000"
            },
            "promo": {
                "price": 100000,
                "label": "IDR 100.000"
            }
        }
    },
    "database_record_v2": {
        "label": "DATABASE RECORD",
        "price": {
            "default": {
                "price": 500000,
                "label": "IDR 500.000"
            },
            "promo": {
                "price": 350000,
                "label": "IDR 350.000"
            }
        }
    }
}


""" Qris generator """
def convert_crc16(data):
    crc = 0xFFFF
    for char in data:
        crc ^= ord(char) << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc = crc << 1
    hex_crc = hex(crc & 0xFFFF)[2:].upper()
    return hex_crc.zfill(4)

def generate_qris(amount):
    amount = str(amount)
    qris = "00020101021126670016COM.NOBUBANK.WWW01189360050300000879140214510401201018130303UMI51440014ID.CO.QRIS.WWW0215ID20232612457400303UMI5204481253033605802ID5920WINDASHOPP OK11304556006SERANG61054211162070703A0163042758"
    qris = "00020101021126670016COM.NOBUBANK.WWW01189360050300000879140214451524662597130303UMI51440014ID.CO.QRIS.WWW0215ID20232633000480303UMI5204481253033605802ID5920KLMX STORE OK11646236006SERANG61054211162070703A01630438B3"
    qris = qris[:-4]
    step1 = qris.replace("010211", "010212")
    step2 = step1.split("5802ID")
    price = f"54{len(amount):02d}{amount}"
    price += "5802ID"
    fix = step2[0].strip() + price + step2[1].strip()
    fix += convert_crc16(fix)
    return fix

def create_qr_code(data):
    return f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={data}"

def get_qris_payment(amount):
    qris_code = generate_qris(amount)
    qris_url  = create_qr_code(qris_code)
    return qris_url, qris_code