# GUIアプリ

## exe作成コマンド

```bash
# プロジェクトルートディレクトリで実行
pyinstaller --onefile --windowed --name "miniapp" --add-data "src;src" --paths "." --paths "src" exe/app.py
```
