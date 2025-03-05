"""
設定ファイルの読み込みと保存を行うモジュール
"""

import os
import json
import yaml
from pathlib import Path
from .logger import get_logger

logger = get_logger(__name__)

# デフォルト設定
DEFAULT_CONFIG = {
    "app": {
        "name": "PDFExPy",
        "version": "0.1.0",
        "log_dir": "logs",
        "temp_dir": "temp",
        "output_dir": "output",
        "headless_mode": False,
    },
    "models": {
        "mobilenet": {
            "enabled": True,
            "threshold": 0.5,
            "version": "v2"
        },
        "cocossd": {
            "enabled": True,
            "threshold": 0.6,
            "version": "lite_mobilenet_v2"
        },
        "tesseract": {
            "enabled": True,
            "language": "jpn+eng",
            "config": "--psm 3"
        }
    },
    "screenshot": {
        "method": "mss",  # mss または pyautogui
        "delay": 1.0,
        "format": "png",
        "monitor": 0  # モニター番号、0は主モニター
    },
    "analysis": {
        "save_format": "json",
        "save_images": True,
        "mock_in_headless": True
    }
}


def get_config_dir():
    """
    設定ファイルディレクトリを取得します。
    
    Returns:
        Path: 設定ファイルディレクトリのパス
    """
    # ユーザーのホームディレクトリに .pdfexpy ディレクトリを作成
    config_dir = Path.home() / ".pdfexpy"
    if not config_dir.exists():
        config_dir.mkdir(exist_ok=True)
        logger.info(f"設定ディレクトリを作成しました: {config_dir}")
    
    return config_dir


def get_config_file(format="yaml"):
    """
    設定ファイルのパスを取得します。
    
    Args:
        format (str, optional): 設定ファイルの形式。'yaml'または'json'。

    Returns:
        Path: 設定ファイルのパス
    """
    config_dir = get_config_dir()
    if format.lower() == "yaml":
        return config_dir / "config.yaml"
    else:
        return config_dir / "config.json"


def load_config(config_file=None, format="yaml"):
    """
    設定ファイルを読み込みます。ファイルが存在しない場合はデフォルト設定を返します。
    
    Args:
        config_file (str, optional): 設定ファイルのパス。Noneの場合はデフォルトパスを使用
        format (str, optional): 設定ファイルの形式。'yaml'または'json'。

    Returns:
        dict: 設定情報
    """
    if config_file is None:
        config_file = get_config_file(format)
    else:
        config_file = Path(config_file)
    
    # 設定ファイルが存在しない場合はデフォルト設定を使用
    if not config_file.exists():
        logger.warning(f"設定ファイルが見つかりません: {config_file}。デフォルト設定を使用します。")
        return DEFAULT_CONFIG.copy()
    
    try:
        # ファイルフォーマットに応じて読み込み
        with open(config_file, 'r', encoding='utf-8') as f:
            if format.lower() == "yaml":
                config = yaml.safe_load(f)
            else:
                config = json.load(f)
        
        logger.info(f"設定ファイルを読み込みました: {config_file}")
        return config
    except Exception as e:
        logger.error(f"設定ファイルの読み込みに失敗しました: {e}")
        return DEFAULT_CONFIG.copy()


def save_config(config, config_file=None, format="yaml"):
    """
    設定を指定されたパスに保存します。
    
    Args:
        config (dict): 保存する設定情報
        config_file (str, optional): 設定ファイルのパス。Noneの場合はデフォルトパスを使用
        format (str, optional): 設定ファイルの形式。'yaml'または'json'。

    Returns:
        bool: 保存に成功した場合はTrue、失敗した場合はFalse
    """
    if config_file is None:
        config_file = get_config_file(format)
    else:
        config_file = Path(config_file)
    
    try:
        # ディレクトリが存在しない場合は作成
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # フォーマットに応じて保存
        with open(config_file, 'w', encoding='utf-8') as f:
            if format.lower() == "yaml":
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
            else:
                json.dump(config, f, ensure_ascii=False, indent=2)
        
        logger.info(f"設定を保存しました: {config_file}")
        return True
    except Exception as e:
        logger.error(f"設定の保存に失敗しました: {e}")
        return False 