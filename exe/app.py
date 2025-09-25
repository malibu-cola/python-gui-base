#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os

# PyInstallerでのパス解決を考慮
if hasattr(sys, '_MEIPASS'):
    # exe化された場合
    base_path = sys._MEIPASS
else:
    # 開発環境の場合
    base_path = os.path.dirname(__file__)

# プロジェクトルートをパスに追加
project_root = os.path.abspath(os.path.join(base_path, ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from src.gui.gui_tkinter import gui_run
except ImportError as e:
    print(f"Import error: {e}")
    # フォールバック：相対パスで直接インポート
    gui_dir = os.path.join(project_root, "src", "gui")
    sys.path.insert(0, gui_dir)
    from gui_tkinter import gui_run


class App:
    def __init__(self):
        print("App initialized.")

    def run(self):
        print("App is running...")
        gui_run()


def main():
    """メイン関数"""
    try:
        app = App()
        app.run()
    except Exception as e:
        import tkinter.messagebox as messagebox
        messagebox.showerror("起動エラー", f"アプリケーションの起動に失敗しました:\n{str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()