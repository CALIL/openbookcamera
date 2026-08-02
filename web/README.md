# OpenBookCamera Web Site

https://openbookcamera.com

ビルドの無い静的サイトです。`index.html` / `css/style.css` / `img/` をそのまま配信しています。

## Development

このディレクトリのファイルを直接編集してください。確認はブラウザで `index.html` を開くだけです。

以前は sass を Parcel でビルドしていましたが、1ページの静的サイトに
ビルドを挟む必要が無いため廃止しました。CSS は `css/style.css` が原本です。

## Deploy

https://dash.cloudflare.com/9f2a842113dbb9618c3d37c24fa23af4/pages/view/openbookcamera

master にコミットすると Cloudflare Pages に配信されます。ビルドは走りません。
