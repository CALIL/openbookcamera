# 書影撮影システム

## コンセプト

- 書影（本の表示画像）キャプチャ用のスキャナデバイス
- 本を置いたら自動撮影
- 表紙・裏表紙・背の3面を高速撮影（2秒程度）
- ネットワーク接続なしでスタンドアロン動作

## システム構成

![](doc/diagram.png)

## Installation

Windows:

- [Anaconda](https://www.anaconda.com/download/) Python3.6 をインストール
- [LAVFilters](https://github.com/Nevcairiel/LAVFilters/releases)をインストール（任意） Motion-JPEGの処理速度改善

```sh
conda install numpy
conda install -c menpo opencv
pip install -r requirements.txt
```

## 制御ボード

![](doc/circuit.png)

- Arudinoシールド互換サイズ
- MOSFETによる12V制御回路×4
- 各種センサ向けのコネクタ（2.5mmピッチ・XHシリーズ）
- [Pololu Arduino library for VL53L0X](https://github.com/pololu/vl53l0x-arduino)
- 光電センサ [Z2T-2000N](https://www.optex-fa.jp/products/photo_sensor/amp/z_eco/index.html) を本が置かれたことを検出するセンサとして採用

## UVCカメラ

- [UVC規格](https://en.wikipedia.org/wiki/USB_video_device_class)の汎用的なUSBカメラに対応
- 試作機では[IPEVO社製V4K](https://www.ipevo.jp/v4k.html)を採用（800万画素）
- 各カメラを独立したUSBポートに接続すること（USBハブを用いた場合は帯域不足となる）

## Release History

* 0.0.1
    * Work in progress
