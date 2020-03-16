# -*- coding: utf-8 -*-

import serial
import cv2
import numpy as np
import time
import datetime
import os
import json
import platform
import logging
import coloredlogs
from turbojpeg import TurboJPEG

DATAPATH = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "./data/")
)
IS_NEW4K = True # 新しいV4Kファームウェア（製造番号10以下ではFalseを指定）

logger = logging.getLogger("システム")
coloredlogs.install(level="DEBUG", fmt="%(asctime)s %(levelname)s %(message)s")
jpeg = TurboJPEG()


def barcode_recognition(images):
    from pyzbar.pyzbar import decode
    from pyzbar.pyzbar import ZBarSymbol

    rs = []
    for image, role in images:
        result = decode(image, symbols=[ZBarSymbol.EAN13, ZBarSymbol.CODABAR])
        for item in result:
            r = {
                "role": role,
                "data": item.data.decode("utf-8"),
                "type": item.type,
                "rect": {
                    "left": item.rect.left,
                    "top": item.rect.top,
                    "width": item.rect.width,
                    "height": item.rect.height,
                },
                "polygon": [],
            }
            for p in item.polygon:
                r["polygon"].append({"x": p.x, "y": p.y})
            rs.append(r)
    return rs


def connect_controller():
    ser = None
    for port in range(1, 10):
        try:
            ser = serial.Serial("COM%d" % port, 115200, timeout=1, write_timeout=1)
            logger.debug("COM%dに接続中..." % port)
            for _ in range(1, 5):
                if ser.in_waiting > 0:
                    ser.read_all()
                ser.write(b"3")
                ser.flush()
                ser.write(b"3")
                ser.flush()
                time.sleep(0.5)
                if ser.in_waiting > 0:
                    line = ser.readline().strip().decode("utf-8")
                    if line == "ACK":
                        return ser
            ser.close()
        except serial.serialutil.SerialException:
            pass
    return None


def calc_white_region(img):
    """
    画像上部(20ピクセル)の白領域の割合を返す
    """
    im = img[0:20, :]
    im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    _, im = cv2.threshold(im, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    hist = cv2.calcHist([im], [0], None, [2], [0, 256])
    return hist[1][0] / (hist[0][0] + hist[1][0])


def write_jpeg(filename, image):
    with open(filename, "wb") as f:
        f.write(jpeg.encode(image))


logger.info("制御装置に接続しています")
ser = connect_controller()
if not ser:
    logger.error("制御装置に接続できませんでした")
    input()
    exit()
logger.info("制御装置に接続しました")


def initialize_camera(cap, role):
    logger.info("カメラ[%s]を初期化しています" % role)

    if IS_NEW4K:
        # しばらく低解像度をデータ取得した後に、高解像度に切り替える
        cap.set(cv2.CAP_PROP_AUTO_EXPOSURE , float(0.25))
        cap.set(cv2.CAP_PROP_EXPOSURE,  float(-6))
        cap.set(cv2.CAP_PROP_FPS, 15)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640) 
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FOURCC,  cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        for x in range(1,50):
            cap.read()
            
    cap.set(cv2.CAP_PROP_FPS, 15)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 2448)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 3264)
    for x in range(1,5):
        cap.read()

    cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)  # オートフォーカスオフ

    if IS_NEW4K:
        cap.set(cv2.CAP_PROP_WHITE_BALANCE_BLUE_U, 5000)  # 色温度（反映されない: https://github.com/opencv/opencv/issues/13130）
    else:
        cap.set(cv2.CAP_PROP_WHITE_BALANCE_BLUE_U, 6000)  # 色温度

    cap.set(cv2.CAP_PROP_SHARPNESS, 2)
    cap.set(cv2.CAP_PROP_SATURATION, 64)
    cap.set(cv2.CAP_PROP_HUE, 0)
    if role == "BOTTOM":
        cap.set(cv2.CAP_PROP_FOCUS,  271 if IS_NEW4K else 112)
        cap.set(cv2.CAP_PROP_BRIGHTNESS, 0 if IS_NEW4K else -50)
        cap.set(cv2.CAP_PROP_GAMMA, 110 if IS_NEW4K else 150)
        if IS_NEW4K:
            cap.set(cv2.CAP_PROP_AUTO_EXPOSURE , float(0.25))
            cap.set(cv2.CAP_PROP_EXPOSURE,  float(-7))
    elif role == "SIDE":
        cap.set(cv2.CAP_PROP_FOCUS, 235 if IS_NEW4K else 95)  # フォーカス設定
        cap.set(cv2.CAP_PROP_BRIGHTNESS, 0 if IS_NEW4K else -100)
        cap.set(cv2.CAP_PROP_GAMMA, 110 if IS_NEW4K else 110)
        if IS_NEW4K:
            cap.set(cv2.CAP_PROP_AUTO_EXPOSURE , float(0.25))
            cap.set(cv2.CAP_PROP_EXPOSURE,  float(-7))
    elif role == "TOP":
        cap.set(cv2.CAP_PROP_FOCUS, 200 if IS_NEW4K else 77)  # フォーカス設定
        cap.set(cv2.CAP_PROP_BRIGHTNESS, 0 if IS_NEW4K else -40)
        cap.set(cv2.CAP_PROP_GAMMA,110 if IS_NEW4K else 130)
        if IS_NEW4K:
            cap.set(cv2.CAP_PROP_AUTO_EXPOSURE , float(0.25))
            cap.set(cv2.CAP_PROP_EXPOSURE,  float(-6))
    else:
        cap.set(cv2.CAP_PROP_FOCUS, 200 if IS_NEW4K else 70)
        cap.set(cv2.CAP_PROP_BRIGHTNESS, 0 if IS_NEW4K else -40)
        cap.set(cv2.CAP_PROP_GAMMA, 100)
        if IS_NEW4K:
             cap.set(cv2.CAP_PROP_AUTO_EXPOSURE , float(1))


cameras = []
for x in range(0, 3):
    cameras.append(cv2.VideoCapture(x+700))
    initialize_camera(cameras[x], str(x + 1))

logger.info("カメラの起動を待っています")
time.sleep(3)

white_regions = []
for x in range(0, 3):
    logger.info("カメラ[%d]の撮影テスト中..." % (x + 1))
    err, img = cameras[x].read()
    r = calc_white_region(img)
    logger.info("ホワイト領域比率:%0.2f" % r)
    white_regions.append((r, x))

# 白領域がないカメラが側面
white_regions = sorted(white_regions)
index_side = white_regions[0][1]
index_top = None
index_bottom = None
logger.info("カメラ[SIDE]を検出しました:%d" % (index_side + 1))

# 上照明のみに切り替える
logger.info("残りのカメラをテスト中...")
ser.write(b"1")
while True:
    _, img1 = cameras[white_regions[1][1]].read()
    r1 = calc_white_region(img1)
    _, img2 = cameras[white_regions[2][1]].read()
    r2 = calc_white_region(img2)
    if abs(r1 - r2) > 0.5:
        if r1 > r2:
            logger.info("カメラ[TOP]を検出しました:%d" % (white_regions[1][1] + 1))
            index_top = white_regions[1][1]
            index_bottom = white_regions[2][1]
        else:
            logger.info("カメラ[TOP]を検出しました:%d" % (white_regions[2][1] + 1))
            index_top = white_regions[2][1]
            index_bottom = white_regions[1][1]
        break

ser.write(b"3")
cap_top = cameras[index_top]
initialize_camera(cap_top, "TOP")
cap_bottom = cameras[index_bottom]
initialize_camera(cap_bottom, "BOTTOM")
cap_side = cameras[index_side]
initialize_camera(cap_side, "SIDE")

cap_top.grab()
cap_bottom.grab()
cap_side.grab()

role = "SIDE"
stage = 0
mm = None
stock_side1 = None
stock_side2 = None
stock_side3 = None
stock_top = None
stock_bottom = None

logger.info("動作を開始しました")

while True:
    f = 0
    while ser.inWaiting():
        line = ser.readline().strip().decode("utf-8")
        if line == "ON":
            logger.warning("[検出]自動スキャンプロセスを開始します")
            f = 1
        elif line == "LEAVE":
            logger.warning("撮影対象が離脱しました")
        elif line == "SKIP":
            pass
        elif line.startswith("HEIGHT"):
            mm = int(line.split(":")[1])
            if IS_NEW4K:
                focus = int(0.5 * mm + 180)
            else:
                focus = int(0.0145 * mm + 85.886)
            logger.info("撮影対象の高さは%dmm、カメラ[TOP]のフォーカスを%dに設定します" % (mm, focus))
            cap_top.set(cv2.CAP_PROP_FOCUS, focus)
            cap_top.read()
        else:
            logger.info("制御装置からのメッセージ:%s" % line)

    if role == "TOP":
        err, image = cap_top.read()
        if stage:
            err, image = cap_top.read()
            stock_top = image
            cap_side.read()
            err, stock_side2 = cap_side.read()
    elif role == "BOTTOM":
        err, image = cap_bottom.read()
        if stage:
            stock_bottom = image
            cap_side.read()
            err, stock_side3 = cap_side.read()
    elif role == "SIDE":
        err, image = cap_side.read()
        if stage:
            stock_side1 = image

    halfImg = cv2.resize(
        image, (int(3264 / 3), int(2448 / 3)), interpolation=cv2.INTER_AREA
    )
    cv2.putText(
        halfImg,
        "BC-SCANNER %s" % role,
        (10, 30),
        cv2.FONT_HERSHEY_PLAIN,
        1.5,
        (255, 255, 255),
        1,
        cv2.LINE_AA,
    )
    if mm is not None:
        cv2.putText(
            halfImg,
            "%dmm" % mm,
            (10, 60),
            cv2.FONT_HERSHEY_PLAIN,
            2,
            (255, 255, 255),
            1,
            cv2.LINE_AA,
        )

    cv2.imshow("BC-SCANNER", halfImg)

    key = cv2.waitKey(1)

    if key == ord("0"):
        ser.write(b"0")
    if key == ord("1"):
        ser.write(b"1")
        role = "TOP"
    if key == ord("2"):
        ser.write(b"2")
        role = "BOTTOM"
    if key == ord("3"):
        ser.write(b"3")
        role = "SIDE"
    if key == ord("4"):
        ser.write(b"4")
        role = "SIDE"
    if key == ord("c"):
        if role == "TOP":
            cap_top.set(cv2.CAP_PROP_SETTINGS, 1)
        if role == "BOTTOM":
            cap_bottom.set(cv2.CAP_PROP_SETTINGS, 1)
        if role == "SIDE":
            cap_side.set(cv2.CAP_PROP_SETTINGS, 1)

    if key == 13 or f == 1:
        stage = 1
        mm = None
        book_title = None
        cap_top.set(cv2.CAP_PROP_FOCUS, 77)
        cap_top.read()
        ser.write(b"4")
        role = "SIDE"
        for x in range(3):
            err, image = cap_side.read()
        continue
    if stage == 1:
        ser.write(b"1")
        role = "TOP"
        stage = 2
        for x in range(3):
            err, image = cap_top.read()
        continue
    if stage == 2:
        ser.write(b"2")
        role = "BOTTOM"
        stage = 3
        for x in range(4):
            err, image = cap_bottom.read()
        continue
    if stage == 3:
        ser.write(b"3")
        role = "SIDE"
        now = datetime.datetime.now()
        save_id = now.strftime("%Y%m%d_%H%M%S")
        fn = DATAPATH + "/" + save_id + "/"
        logger.warning("撮影ID[%s]" % (save_id))

        os.makedirs(fn)

        for m in [
            ("TOP", "top.jpg", stock_top),
            ("BOTTOM", "bottom.jpg", stock_bottom),
            ("SIDE1", "side1.jpg", stock_side1),
            ("SIDE2", "side2.jpg", stock_side2),
            ("SIDE3", "side3.jpg", stock_side3),
        ]:
            write_jpeg(fn + m[1], m[2])
            logger.info("[%s]書き込み完了" % m[0])

        with open(fn + "metadata.json", "w") as f:
            f.write(
                json.dumps(
                    {
                        "version": 1,
                        "thickness": mm,
                        "timestamp": now.strftime("%Y/%m/%d %H:%M:%S"),
                    },
                    indent=4,
                )
            )
        barcode = barcode_recognition([(stock_top, "top"), (stock_bottom, "bottom")])
        with open(fn + "barcode.json", "w") as f:
            f.write(
                json.dumps(
                    {
                        "recognition_engine": "zbar",
                        "platform": platform.system(),
                        "result": barcode,
                    },
                    indent=4,
                )
            )
        for p in barcode:
            logger.info("バーコードを認識しました [%s]" % p["data"])

        stage = 0
        logger.warning("次の撮影を待機しています...")
        continue

    if key == ord("q") or key == 27:  # ESC
        break

cap_top.release()
cap_bottom.release()
cap_side.release()
cv2.destroyAllWindows()
ser.close()
