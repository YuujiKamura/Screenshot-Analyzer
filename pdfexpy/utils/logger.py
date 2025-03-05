"""
ログ出力機能を提供するモジュール
"""

import os
import sys
import logging
import datetime
from logging.handlers import RotatingFileHandler

# ロガーインスタンスの辞書
_loggers = {}

def setup_logger(name, log_dir=None, console_level=logging.INFO, file_level=logging.DEBUG):
    """
    ロガーのセットアップを行います。

    Args:
        name (str): ロガー名
        log_dir (str, optional): ログファイル出力ディレクトリ。Noneの場合は一時ディレクトリを使用
        console_level (int, optional): コンソール出力のログレベル
        file_level (int, optional): ファイル出力のログレベル

    Returns:
        logging.Logger: 設定済みのロガー
    """
    if name in _loggers:
        return _loggers[name]
    
    # ロガー作成
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # 全レベルのログを受け付ける
    
    # フォーマッターの作成
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # コンソールハンドラーの設定
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # ファイルハンドラーの設定（指定があれば）
    if log_dir:
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
            
        timestamp = datetime.datetime.now().strftime('%Y%m%d')
        log_file = os.path.join(log_dir, f"{name}_{timestamp}.log")
        
        file_handler = RotatingFileHandler(
            log_file, 
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(file_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # ロガーをキャッシュ
    _loggers[name] = logger
    
    return logger


def get_logger(name):
    """
    既存のロガーインスタンスを取得、または新規作成します。

    Args:
        name (str): ロガー名

    Returns:
        logging.Logger: ロガーインスタンス
    """
    if name in _loggers:
        return _loggers[name]
    
    # 初期未設定の場合は基本設定でセットアップ
    return setup_logger(name) 