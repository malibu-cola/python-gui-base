#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高度なファイル選択・操作の例
"""

import tkinter as tk
from tkinter import ttk, filedialog
import os

from src.logic.pipeline import process_data 


class GUI:
    """高度なファイル操作を提供するクラス"""

    @staticmethod
    def select_excel_file():
        """Excelファイル専用の選択ダイアログ"""
        file_types = [
            ("Excelファイル", "*.xlsx *.xls *.xlsm"),
            ("Excel 2007以降", "*.xlsx *.xlsm"),
            ("Excel 97-2003", "*.xls"),
            ("すべてのファイル", "*.*"),
        ]

        return filedialog.askopenfilename(
            title="Excelファイルを選択してください",
            filetypes=file_types,
            initialdir=os.path.expanduser(
                "~"
            ),  # ホームディレクトリから開始
        )

    @staticmethod
    def select_folder():
        """フォルダの選択"""
        return filedialog.askdirectory(
            title="フォルダを選択してください", initialdir=os.path.expanduser("~")
        )




class FileManagerApp:
    """ファイル管理アプリケーションのデモ"""

    def __init__(self, root):
        self.root = root
        self.selected_files = []
        self._setup_window()
        self._create_widgets()

    def _setup_window(self):
        self.root.title("高度なファイル選択デモ")
        self.root.geometry("700x600")

    def _create_widgets(self):
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # ボタンフレーム
        button_frame = ttk.LabelFrame(main_frame, text="ファイル操作", padding="10")
        button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # 各種ボタン
        ttk.Button(
            button_frame, text="Excelファイルを選択", command=self._select_excel
        ).grid(row=0, column=0, padx=5, pady=5)

        ttk.Button(
            button_frame, text="フォルダを選択", command=self._select_folder
        ).grid(row=1, column=0, padx=5, pady=5)
        
        ttk.Button(
            button_frame, text="パイプライン1実行", command=self.run_pipeline1
        ).grid(row=2, column=0, padx=5, pady=5)


    def _select_excel(self):
        """Excelファイル選択"""
        file_path = GUI.select_excel_file()
        if file_path:
            self.selected_files = [file_path]
            self.display_file_info([file_path], "Excelファイル選択結果")

    def _select_folder(self):
        """フォルダ選択"""
        folder_path = GUI.select_folder()
        if folder_path:
            self.result_text.insert(tk.END, f"選択されたフォルダ: {folder_path}\n\n")
            self.result_text.see(tk.END)
            
    def run_pipeline1(self):
        process_data()



def gui_run():
    root = tk.Tk()
    FileManagerApp(root)
    root.mainloop()


if __name__ == "__main__":
    gui_run()
