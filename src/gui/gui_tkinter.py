#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
マルチウィンドウ対応のファイル選択・操作Window1
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os

from src.logic.pipeline import process_data, process_data2


class Window1:
    """高度なファイル操作を提供するクラス"""

    @staticmethod
    def select_excel_file() -> str:
        """Excelファイル専用の選択ダイアログ"""

        return filedialog.askopenfilename(
            title="Excelファイルを選択してください",
            initialdir=os.path.expanduser("~"),
        )

    @staticmethod
    def select_folder() -> str:
        """フォルダの選択"""
        return filedialog.askdirectory(
            title="フォルダを選択してください",
            initialdir=os.path.expanduser("~"),
        )


class Window2:
    """パイプライン2の専用ウィンドウ"""

    def __init__(self, parent=None):
        self.parent = parent
        self.window = tk.Toplevel() if parent else tk.Tk()
        self.selected_files = []
        self._setup_window()
        self._create_widgets()

    def _setup_window(self):
        """ウィンドウの設定"""
        self.window.title("パイプライン2 実行画面")
        self.window.geometry("600x500")

        # 親ウィンドウがある場合は中央に配置
        if self.parent:
            self._center_window_relative_to_parent()

        # ウィンドウを最前面に表示
        self.window.lift()
        self.window.focus_force()

        # ウィンドウクローズ時の処理
        self.window.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _center_window_relative_to_parent(self):
        """親ウィンドウの中央にウィンドウを配置"""
        if self.parent:
            parent_x = self.parent.winfo_x()
            parent_y = self.parent.winfo_y()
            parent_width = self.parent.winfo_width()
            parent_height = self.parent.winfo_height()

            window_width = 600
            window_height = 500

            x = parent_x + (parent_width // 2) - (window_width // 2)
            y = parent_y + (parent_height // 2) - (window_height // 2)

            self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def _create_widgets(self):
        """ウィジェットの作成"""
        # メインフレーム
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # グリッド設定
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)

        # タイトル
        title_label = ttk.Label(
            main_frame, text="パイプライン2 実行画面", font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 20))

        # ファイル選択セクション
        file_frame = ttk.LabelFrame(main_frame, text="ファイル選択", padding="10")
        file_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        file_frame.columnconfigure(1, weight=1)

        # ファイル選択ボタン
        ttk.Button(
            file_frame, text="ファイルを選択", command=self._select_input_file
        ).grid(row=0, column=0, padx=(0, 10), pady=5)

        # 選択されたファイル表示
        self.config_file_var = tk.StringVar(value="入力ファイルが選択されていません")
        config_label = ttk.Label(
            file_frame, textvariable=self.config_file_var, foreground="gray"
        )
        config_label.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)

        # 実行ログ表示エリア
        log_frame = ttk.LabelFrame(main_frame, text="実行ログ", padding="5")
        log_frame.grid(
            row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0)
        )
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        # テキストエリア
        text_frame = ttk.Frame(log_frame)
        text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)

        self.log_text = tk.Text(
            text_frame, height=10, wrap=tk.WORD, font=("Consolas", 9)
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # スクロールバー
        scrollbar = ttk.Scrollbar(
            text_frame, orient=tk.VERTICAL, command=self.log_text.yview
        )
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.log_text.config(yscrollcommand=scrollbar.set)

        # ボタンフレーム
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(10, 0))

        # ボタンを右寄せにするためのフレーム
        right_frame = ttk.Frame(button_frame)
        right_frame.pack(side=tk.RIGHT)

        # 実行ボタン
        ttk.Button(
            right_frame,
            text="パイプライン2を実行",
            command=self._run_pipeline2,
            style="Accent.TButton",
        ).pack(side=tk.LEFT, padx=(0, 10))

        # 閉じるボタン
        ttk.Button(right_frame, text="閉じる", command=self._on_closing).pack(
            side=tk.LEFT
        )

        # 初期ログメッセージ
        self._add_log("パイプライン2実行画面が開かれました。")

    def _select_input_file(self):
        """入力ファイルを選択"""
        file_path = filedialog.askopenfilename(
            title="ファイルを選択してください",
            initialdir=os.path.expanduser("~"),
        )

        if file_path:
            self.config_file_var.set(file_path)
            self.config_file_path = file_path
            self._add_log(
                f"入力ファイルが選択されました: {os.path.basename(file_path)}"
            )
        else:
            self._add_log("入力ファイルの選択がキャンセルされました。")

    def _run_pipeline2(self):
        """パイプライン2を実行"""
        # 実行前チェック
        if not hasattr(self, "config_file_path"):
            messagebox.showwarning("警告", "入力ファイルを選択してください")
            self._add_log("エラー: 入力ファイルが選択されていません")
            return


        # 実行ログ
        self._add_log("パイプライン2の実行を開始します...")
        self._add_log(f"入力ファイル: {self.config_file_path}")
        try:
            process_data2()
        except Exception as e:
            error_msg = f"パイプライン2の実行中にエラーが発生しました: {str(e)}"
            self._add_log(f"エラー: {error_msg}")
            messagebox.showerror("エラー", error_msg)

    def _add_log(self, message):
        """ログメッセージを追加"""
        log_message = f"{message}\n"

        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)
        self.window.update_idletasks()

    def _on_closing(self):
        """ウィンドウを閉じる時の処理"""
        self.window.destroy()


class FileManagerApp:
    """ファイル管理アプリケーションのメインクラス"""

    def __init__(self, root):
        self.root = root
        self.selected_files = []
        self.pipeline2_window = None
        self._setup_window()
        self._create_widgets()

    def _setup_window(self):
        self.root.title("HOGE v.0.1")
        self.root.geometry("700x600")

    def _create_widgets(self):
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # グリッド設定
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # ボタンフレーム
        button_frame = ttk.LabelFrame(main_frame, text="ファイル操作", padding="10")
        button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # 既存のボタン（左側に配置）
        left_buttons_frame = ttk.Frame(button_frame)
        left_buttons_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        ttk.Button(
            left_buttons_frame, text="Excelファイルを選択", command=self._select_excel
        ).grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        ttk.Button(
            left_buttons_frame, text="フォルダを選択", command=self._select_folder
        ).grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)

        ttk.Button(
            left_buttons_frame, text="パイプライン1実行", command=self._run_pipeline1
        ).grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)

        # 右下にパイプライン2ボタンを配置
        right_buttons_frame = ttk.Frame(button_frame)
        right_buttons_frame.pack(side=tk.RIGHT, anchor=tk.SE)

        ttk.Button(
            right_buttons_frame,
            text="パイプライン2を起動",
            command=self._open_pipeline2_window,
            style="Accent.TButton",  # 強調スタイル
        ).pack(pady=5)

        # 結果表示エリア
        result_frame = ttk.LabelFrame(main_frame, text="結果表示", padding="10")
        result_frame.grid(
            row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0)
        )
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)

        # テキストエリア
        text_frame = ttk.Frame(result_frame)
        text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)

        self.result_text = tk.Text(text_frame, height=25, wrap=tk.WORD)
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # スクロールバー
        scrollbar = ttk.Scrollbar(
            text_frame, orient=tk.VERTICAL, command=self.result_text.yview
        )
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.result_text.config(yscrollcommand=scrollbar.set)

    def _select_excel(self):
        """Excelファイル選択"""
        file_path = Window1.select_excel_file()
        if file_path:
            self.selected_files = [file_path]

    def _select_folder(self):
        """フォルダ選択"""
        folder_path = Window1.select_folder()
        if folder_path:
            self.result_text.insert(tk.END, f"選択されたフォルダ: {folder_path}\n\n")
            self.result_text.see(tk.END)

    def _run_pipeline1(self):
        """パイプライン1を実行"""
        try:
            self.result_text.insert(tk.END, "パイプライン1を実行中...\n")
            self.result_text.see(tk.END)
            self.root.update()  # Window1を更新

            process_data()  # 実際のパイプライン実行

            self.result_text.insert(tk.END, "パイプライン1の実行が完了しました。\n\n")
            self.result_text.see(tk.END)

        except Exception as e:
            error_msg = f"パイプライン1の実行中にエラーが発生しました: {str(e)}\n\n"
            self.result_text.insert(tk.END, error_msg)
            self.result_text.see(tk.END)
            messagebox.showerror(
                "エラー", f"パイプライン1の実行に失敗しました:\n{str(e)}"
            )

    def _open_pipeline2_window(self):
        """パイプライン2のウィンドウを開く"""
        # 既にウィンドウが開いている場合はフォーカスを当てる
        if self.pipeline2_window and hasattr(self.pipeline2_window, "window"):
            try:
                self.pipeline2_window.window.lift()
                self.pipeline2_window.window.focus_force()
                return
            except tk.TclError:
                # ウィンドウが既に閉じられている場合
                self.pipeline2_window = None

        # 新しいウィンドウを作成
        self.pipeline2_window = Window2(parent=self.root)
        self.result_text.insert(tk.END, "パイプライン2のウィンドウを開きました。\n\n")
        self.result_text.see(tk.END)


def gui_run():
    """Window1アプリケーションを起動"""
    root = tk.Tk()
    FileManagerApp(root)
    root.mainloop()


if __name__ == "__main__":
    gui_run()
