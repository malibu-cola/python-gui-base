#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
拡張版パイプライン処理
"""

import time
from loguru import logger


def process_data(window_id="main"):
    """パイプライン1の処理"""
    # window_idを指定したロガーを作成
    bound_logger = logger.bind(window_id=window_id)
    bound_logger.info("パイプライン1: 処理を開始します")
    
    try:
        # ステップ1: データ読み込み
        bound_logger.info("ステップ1: データ読み込みを開始")
        time.sleep(1)  # 実際の処理をシミュレート
        bound_logger.success("ステップ1: データ読み込み完了")
        
        # ステップ2: データ検証
        bound_logger.info("ステップ2: データ検証を開始")
        time.sleep(1)
        bound_logger.success("ステップ2: データ検証完了")
        
        # ステップ3: データ変換
        bound_logger.info("ステップ3: データ変換を開始")
        time.sleep(1.5)
        bound_logger.success("ステップ3: データ変換完了")
        
        # ステップ4: 結果保存
        bound_logger.info("ステップ4: 結果保存を開始")
        time.sleep(0.5)
        bound_logger.success("ステップ4: 結果保存完了")
        
        bound_logger.success("パイプライン1: すべての処理が正常に完了しました")
        
    except Exception as e:
        bound_logger.error(f"パイプライン1でエラーが発生しました: {str(e)}")
        raise


def process_data2(window_id="window2"):
    """パイプライン2の処理"""
    # window_idを指定したロガーを作成
    bound_logger = logger.bind(window_id=window_id)
    bound_logger.info("パイプライン2: 処理を開始します")
    
    try:
        # ステップ1: 設定ファイル読み込み
        bound_logger.info("ステップ1: 設定ファイル読み込みを開始")
        time.sleep(0.8)
        bound_logger.success("ステップ1: 設定ファイル読み込み完了")
        
        # ステップ2: 前処理
        bound_logger.info("ステップ2: 前処理を開始")
        time.sleep(1.2)
        bound_logger.debug("前処理: データクリーニング実行中...")
        bound_logger.debug("前処理: 異常値検出実行中...")
        bound_logger.success("ステップ2: 前処理完了")
        
        # ステップ3: メイン処理
        bound_logger.info("ステップ3: メイン処理を開始")
        for i in range(1, 6):
            bound_logger.debug(f"メイン処理: バッチ{i}/5 を処理中...")
            time.sleep(0.4)
        bound_logger.success("ステップ3: メイン処理完了")
        
        # ステップ4: 後処理
        bound_logger.info("ステップ4: 後処理を開始")
        time.sleep(0.6)
        bound_logger.debug("後処理: レポート生成中...")
        bound_logger.success("ステップ4: 後処理完了")
        
        # ステップ5: 最終確認
        bound_logger.info("ステップ5: 最終確認を開始")
        time.sleep(0.3)
        bound_logger.success("ステップ5: 最終確認完了")
        
        bound_logger.success("パイプライン2: すべての処理が正常に完了しました")
        
    except Exception as e:
        bound_logger.error(f"パイプライン2でエラーが発生しました: {str(e)}")
        raise


def process_data_with_error():
    """エラーテスト用の処理"""
    logger.info("エラーテスト: 処理を開始します")
    
    try:
        logger.info("意図的にエラーを発生させます...")
        time.sleep(1)
        
        # 意図的にエラーを発生
        result = 1 / 0
        
    except ZeroDivisionError as e:
        logger.error(f"ゼロ除算エラーが発生しました: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"予期しないエラーが発生しました: {str(e)}")
        raise


if __name__ == "__main__":
    # loguruの設定（スタンドアローン実行時用）
    logger.remove()
    logger.add(
        "logs/pipeline_{time:YYYY-MM-DD}.log",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="1 day",
        retention="7 days",
        encoding="utf-8"
    )
    logger.add(
        lambda msg: print(msg, end=""),
        level="INFO",
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        colorize=True
    )
    
    logger.info("パイプライン処理テストを開始します")
    
    try:
        process_data()
        logger.info("=" * 50)
        process_data2()
    except Exception as e:
        logger.critical(f"パイプライン処理で致命的なエラーが発生しました: {str(e)}")
    
    logger.info("パイプライン処理テストを終了します")