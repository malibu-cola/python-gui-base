#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
loguruログ統合対応のマルチウィンドウGUI
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import queue
import threading
from loguru import logger

from src.logic.pipeline import process_data, process_data2


class LogHandler:
    """ログをGUIに転送するためのハンドラー"""

    def __init__(self):
        self.log_queue = queue.Queue()
        self.gui_widgets = []  # ログを表示するテキストウィジェットのリスト
        self.is_setup = False

    def setup_logger(self):
        """loguruの設定とGUI用シンクの追加"""
        if self.is_setup:
            return

        # GUI用のカスタムシンク
        logger.add(
            self._gui_sink,
            level="DEBUG",
            format="{time:HH:mm:ss} | <level>{level: <8}</level> | {message}",
            colorize=False,
            catch=True,
        )

        # ファイル出力も追加（オプション）
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        logger.add(
            os.path.join(log_dir, "app_{time:YYYY-MM-DD}.log"),
            level="INFO",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            rotation="1 day",
            retention="30 days",
            compression="zip",
            encoding="utf-8",
        )

        self.is_setup = True
        logger.info("ログシステムが初期化されました")

    def _gui_sink(self, message):
        """GUI用のログシンク"""
        try:
            # ANSIエスケープシーケンスを削除
            import re

            clean_message = re.sub(
                r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", str(message)
            )

            # キューに追加（メインスレッドで処理するため）
            self.log_queue.put(clean_message)
        except Exception as e:
            print(f"GUI log sink error: {e}")

    def register_widget(self, text_widget, root_widget):
        """ログを表示するテキストウィジェットを登録"""
        self.gui_widgets.append((text_widget, root_widget))

        # 定期的にキューをチェックしてログを表示
        self._check_log_queue(text_widget, root_widget)

    def unregister_widget(self, text_widget):
        """テキストウィジェットの登録を解除"""
        self.gui_widgets = [
            (widget, root) for widget, root in self.gui_widgets if widget != text_widget
        ]

    def _check_log_queue(self, text_widget, root_widget):
        """ログキューをチェックして新しいログを表示"""
        try:
            while True:
                try:
                    log_message = self.log_queue.get_nowait()
                    self._append_log_to_widget(text_widget, log_message)
                except queue.Empty:
                    break
        except tk.TclError:
            # ウィジェットが削除されている場合
            self.unregister_widget(text_widget)
            return

        # 100ms後に再チェック
        try:
            root_widget.after(
                100, lambda: self._check_log_queue(text_widget, root_widget)
            )
        except tk.TclError:
            pass

    def _append_log_to_widget(self, text_widget, message):
        """テキストウィジェットにログメッセージを追加"""
        try:
            text_widget.insert(tk.END, message)
            text_widget.see(tk.END)

            # 行数制限（パフォーマンス対策）
            lines = int(text_widget.index("end-1c").split(".")[0])
            if lines > 1000:
                text_widget.delete("1.0", "500.0")
        except tk.TclError:
            # ウィジェットが削除されている場合
            self.unregister_widget(text_widget)


# グローバルなログハンドラーインスタンス
log_handler = LogHandler()


class Window1:
    """高度なファイル操作を提供するクラス"""

    @staticmethod
    def select_excel_file() -> str:
        """Excelファイル専用の選択ダイアログ"""
        logger.debug("Excelファイル選択ダイアログを開いています")

        file_path = filedialog.askopenfilename(
            title="Excelファイルを選択してください",
            filetypes=[
                ("Excelファイル", "*.xlsx *.xls *.xlsm"),
                ("すべてのファイル", "*.*"),
            ],
            initialdir=os.path.expanduser("~"),
        )

        if file_path:
            logger.info(f"Excelファイルが選択されました: {os.path.basename(file_path)}")
        else:
            logger.info("Excelファイル選択がキャンセルされました")

        return file_path

    @staticmethod
    def select_folder() -> str:
        """フォルダの選択"""
        logger.debug("フォルダ選択ダイアログを開いています")

        folder_path = filedialog.askdirectory(
            title="フォルダを選択してください",
            initialdir=os.path.expanduser("~"),
        )

        if folder_path:
            logger.info(f"フォルダが選択されました: {folder_path}")
        else:
            logger.info("フォルダ選択がキャンセルされました")

        return folder_path


class Window2:
    """パイプライン2の専用ウィンドウ"""

    def __init__(self, parent=None):
        self.parent = parent
        self.window = tk.Toplevel() if parent else tk.Tk()
        self.selected_files = []
        self._setup_window()
        self._create_widgets()

        logger.info("パイプライン2ウィンドウが開かれました")

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
        main_frame.grid(row=0, column=0, sticky=tk.W + tk.E + tk.N + tk.S)

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
        file_frame.grid(row=1, column=0, sticky=tk.W + tk.E, pady=(0, 20))
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
        config_label.grid(row=0, column=1, sticky=tk.W + tk.E, pady=5)

        # 実行ログ表示エリア
        log_frame = ttk.LabelFrame(main_frame, text="実行ログ", padding="5")
        log_frame.grid(
            row=2,
            column=0,
            columnspan=2,
            sticky=tk.W + tk.E + tk.N + tk.S,
            pady=(10, 0),
        )
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        # テキストエリア
        text_frame = ttk.Frame(log_frame)
        text_frame.grid(row=0, column=0, sticky=tk.W + tk.E + tk.N + tk.S)
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)

        self.log_text = tk.Text(
            text_frame, height=10, wrap=tk.WORD, font=("Consolas", 9)
        )
        self.log_text.grid(row=0, column=0, sticky=tk.W + tk.E + tk.N + tk.S)

        # スクロールバー
        scrollbar = ttk.Scrollbar(
            text_frame, orient=tk.VERTICAL, command=self.log_text.yview
        )
        scrollbar.grid(row=0, column=1, sticky=tk.N + tk.S)
        self.log_text.config(yscrollcommand=scrollbar.set)

        # ログハンドラーにウィジェットを登録
        log_handler.register_widget(self.log_text, self.window)

        # ボタンフレーム
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, sticky=tk.W + tk.E, pady=(10, 0))

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

        # ログクリアボタン
        ttk.Button(
            right_frame,
            text="ログクリア",
            command=self._clear_log,
        ).pack(side=tk.LEFT, padx=(0, 10))

        # 閉じるボタン
        ttk.Button(right_frame, text="閉じる", command=self._on_closing).pack(
            side=tk.LEFT
        )

    def _select_input_file(self):
        """入力ファイルを選択"""
        file_path = filedialog.askopenfilename(
            title="ファイルを選択してください",
            initialdir=os.path.expanduser("~"),
        )

        if file_path:
            self.config_file_var.set(file_path)
            self.config_file_path = file_path
            logger.info(f"入力ファイルが選択されました: {os.path.basename(file_path)}")
        else:
            logger.info("入力ファイルの選択がキャンセルされました")

    def _run_pipeline2(self):
        """パイプライン2を実行"""
        # 実行前チェック
        if not hasattr(self, "config_file_path"):
            logger.warning("入力ファイルが選択されていません")
            messagebox.showwarning("警告", "入力ファイルを選択してください")
            return

        logger.info("=" * 50)
        logger.info("パイプライン2の実行を開始します...")
        logger.info(f"入力ファイル: {self.config_file_path}")

        try:
            # 別スレッドでパイプラインを実行（GUIがブロックされないように）
            def run_pipeline():
                try:
                    process_data2()
                    logger.success("パイプライン2の実行が完了しました！")
                    logger.info("=" * 50)

                    # メインスレッドで成功メッセージを表示
                    self.window.after(
                        0,
                        lambda: messagebox.showinfo(
                            "完了", "パイプライン2の実行が完了しました"
                        ),
                    )
                except Exception as e:
                    logger.error(
                        f"パイプライン2の実行中にエラーが発生しました: {str(e)}"
                    )
                    # メインスレッドでエラーメッセージを表示
                    self.window.after(
                        0,
                        lambda e=e: messagebox.showerror(
                            "エラー", f"パイプライン2の実行に失敗しました:\n{str(e)}"
                        ),
                    )

            # 別スレッドで実行
            threading.Thread(target=run_pipeline, daemon=True).start()

        except Exception as e:
            logger.error(f"パイプライン2の起動中にエラーが発生しました: {str(e)}")
            messagebox.showerror(
                "エラー", f"パイプライン2の起動に失敗しました:\n{str(e)}"
            )

    def _clear_log(self):
        """ログ表示エリアをクリア"""
        self.log_text.delete(1.0, tk.END)
        logger.info("ログ表示がクリアされました")

    def _on_closing(self):
        """ウィンドウを閉じる時の処理"""
        logger.info("パイプライン2ウィンドウが閉じられました")
        log_handler.unregister_widget(self.log_text)
        self.window.destroy()


class FileManagerApp:
    """ファイル管理アプリケーションのメインクラス"""

    def __init__(self, root):
        self.root = root
        self.selected_files = []
        self.pipeline2_window = None
        self._setup_window()
        self._create_widgets()

        logger.info("メインアプリケーションが起動されました")

    def _setup_window(self):
        self.root.title("HOGE v.0.1")
        self.root.geometry("700x600")

    def _create_widgets(self):
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=tk.W + tk.E + tk.N + tk.S)

        # グリッド設定
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)  # 右側（ログエリア）を拡張可能に
        main_frame.rowconfigure(0, weight=1)

        # 左側: ボタンエリア
        left_frame = ttk.Frame(main_frame)
        left_frame.grid(row=0, column=0, sticky=tk.N + tk.W, padx=(0, 10))

        # ファイル操作ボタン
        button_frame = ttk.LabelFrame(left_frame, text="ファイル操作", padding="10")
        button_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(
            button_frame, text="Excelファイルを選択", command=self._select_excel
        ).pack(fill=tk.X, pady=5)

        ttk.Button(
            button_frame, text="フォルダを選択", command=self._select_folder
        ).pack(fill=tk.X, pady=5)

        ttk.Button(
            button_frame, text="パイプライン1実行", command=self._run_pipeline1
        ).pack(fill=tk.X, pady=5)

        # 右側: ログ・結果表示エリア
        result_frame = ttk.LabelFrame(main_frame, text="ログ・結果表示", padding="10")
        result_frame.grid(row=0, column=1, sticky=tk.W + tk.E + tk.N + tk.S)
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)

        # テキストエリア
        text_frame = ttk.Frame(result_frame)
        text_frame.grid(row=0, column=0, sticky=tk.W + tk.E + tk.N + tk.S)
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)

        self.result_text = tk.Text(
            text_frame, height=25, wrap=tk.WORD, font=("Consolas", 9)
        )
        self.result_text.grid(row=0, column=0, sticky=tk.W + tk.E + tk.N + tk.S)

        # スクロールバー
        scrollbar = ttk.Scrollbar(
            text_frame, orient=tk.VERTICAL, command=self.result_text.yview
        )
        scrollbar.grid(row=0, column=1, sticky=tk.N + tk.S)
        self.result_text.config(yscrollcommand=scrollbar.set)

        # ログハンドラーにメインウィンドウのテキストエリアも登録
        log_handler.register_widget(self.result_text, self.root)

        # ログクリアボタン
        clear_button_frame = ttk.Frame(result_frame)
        clear_button_frame.grid(row=1, column=0, sticky=tk.E, pady=(5, 0))

        ttk.Button(
            clear_button_frame, text="ログクリア", command=self._clear_log
        ).pack()

        # パイプライン2ボタン（ログ・結果表示の外、右下に配置）
        pipeline2_button_frame = ttk.Frame(main_frame)
        pipeline2_button_frame.grid(row=1, column=1, sticky=tk.E, pady=(10, 0))

        ttk.Button(
            pipeline2_button_frame,
            text="パイプライン2を起動",
            command=self._open_pipeline2_window,
            style="Accent.TButton",
        ).pack()

    def _select_excel(self):
        """Excelファイル選択"""
        file_path = Window1.select_excel_file()
        if file_path:
            self.selected_files = [file_path]

    def _select_folder(self):
        """フォルダ選択"""
        folder_path = Window1.select_folder()
        if folder_path:
            # 従来の表示も残す
            self.result_text.insert(tk.END, f"選択されたフォルダ: {folder_path}\n\n")
            self.result_text.see(tk.END)

    def _run_pipeline1(self):
        """パイプライン1を実行"""
        logger.info("パイプライン1の実行を開始します...")

        try:
            # 別スレッドでパイプラインを実行（GUIがブロックされないように）
            def run_pipeline():
                try:
                    process_data()  # 実際のパイプライン実行
                    logger.success("パイプライン1の実行が完了しました")

                    # メインスレッドで成功メッセージを表示
                    self.root.after(
                        0,
                        lambda: messagebox.showinfo(
                            "完了", "パイプライン1の実行が完了しました"
                        ),
                    )
                except Exception as e:
                    logger.error(
                        f"パイプライン1の実行中にエラーが発生しました: {str(e)}"
                    )
                    # メインスレッドでエラーメッセージを表示
                    self.root.after(
                        0,
                        lambda e=e: messagebox.showerror(
                            "エラー", f"パイプライン1の実行に失敗しました:\n{str(e)}"
                        ),
                    )

            # 別スレッドで実行
            threading.Thread(target=run_pipeline, daemon=True).start()

        except Exception as e:
            logger.error(f"パイプライン1の起動中にエラーが発生しました: {str(e)}")
            messagebox.showerror(
                "エラー", f"パイプライン1の起動に失敗しました:\n{str(e)}"
            )

    def _open_pipeline2_window(self):
        """パイプライン2のウィンドウを開く"""
        # 既にウィンドウが開いている場合はフォーカスを当てる
        if self.pipeline2_window and hasattr(self.pipeline2_window, "window"):
            try:
                self.pipeline2_window.window.lift()
                self.pipeline2_window.window.focus_force()
                logger.info("既存のパイプライン2ウィンドウにフォーカスしました")
                return
            except tk.TclError:
                # ウィンドウが既に閉じられている場合
                self.pipeline2_window = None

        # 新しいウィンドウを作成
        self.pipeline2_window = Window2(parent=self.root)

    def _clear_log(self):
        """ログ表示エリアをクリア"""
        self.result_text.delete(1.0, tk.END)
        logger.info("メインウィンドウのログ表示がクリアされました")


def gui_run():
    """GUIアプリケーションを起動"""
    # ログハンドラーを初期化
    log_handler.setup_logger()

    root = tk.Tk()
    FileManagerApp(root)

    # アプリケーション終了時の処理
    def on_closing():
        logger.info("アプリケーションを終了します")
        root.quit()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    gui_run()
