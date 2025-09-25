#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最小構成のtkinter GUIアプリケーション
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

class MinimalApp:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.create_widgets()
    
    def setup_window(self):
        """ウィンドウの基本設定"""
        self.root.title("最小構成アプリ")
        self.root.geometry("400x300")
        
        # ウィンドウを中央に配置
        self.center_window()
        
        # アイコンの設定（ファイルが存在する場合）
        try:
            if hasattr(sys, '_MEIPASS'):
                # PyInstallerでexe化された場合
                icon_path = os.path.join(sys._MEIPASS, 'icon.ico')
            else:
                icon_path = 'icon.ico'
            
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception:
            pass  # アイコンがない場合は無視
    
    def center_window(self):
        """ウィンドウを画面中央に配置"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """ウィジェットの作成"""
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # グリッドの重み設定
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # タイトルラベル
        title_label = ttk.Label(
            main_frame, 
            text="最小構成GUIアプリ", 
            font=('Arial', 16, 'bold')
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # 入力フィールド
        ttk.Label(main_frame, text="名前:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.name_entry = ttk.Entry(main_frame, width=30)
        self.name_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # ボタン
        hello_button = ttk.Button(
            main_frame, 
            text="挨拶", 
            command=self.show_greeting
        )
        hello_button.grid(row=2, column=0, pady=10)
        
        exit_button = ttk.Button(
            main_frame, 
            text="終了", 
            command=self.root.quit
        )
        exit_button.grid(row=2, column=1, pady=10)
        
        # 結果表示エリア
        self.result_text = tk.Text(main_frame, height=8, width=50)
        self.result_text.grid(row=3, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        
        # スクロールバー
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        scrollbar.grid(row=3, column=2, sticky=(tk.N, tk.S), pady=10)
        self.result_text.config(yscrollcommand=scrollbar.set)
        
        # フォーカスを入力フィールドに設定
        self.name_entry.focus()
        
        # Enterキーでの実行
        self.root.bind('<Return>', lambda event: self.show_greeting())
    
    def show_greeting(self):
        """挨拶を表示"""
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("警告", "名前を入力してください")
            return
        
        greeting = f"こんにちは、{name}さん！\n"
        self.result_text.insert(tk.END, greeting)
        self.result_text.see(tk.END)
        
        # 入力フィールドをクリア
        self.name_entry.delete(0, tk.END)
        self.name_entry.focus()

def main():
    """メイン関数"""
    try:
        root = tk.Tk()
        MinimalApp(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("エラー", f"アプリケーションエラーが発生しました:\n{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()