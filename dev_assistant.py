"""
開発支援ツール：スクリーンショットの記録と対話をサポート
"""
import os
import time
from datetime import datetime
from pathlib import Path
import json
import pyautogui
import logging

# ロガーの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DevAssistant:
    def __init__(self, base_dir: str = "dev_history"):
        """
        開発支援ツールの初期化
        
        Args:
            base_dir: 開発履歴を保存するベースディレクトリ
        """
        self.base_dir = Path(base_dir)
        self.screenshots_dir = self.base_dir / "screenshots"
        self.context_dir = self.base_dir / "context"
        self._ensure_directories()
        
    def _ensure_directories(self):
        """必要なディレクトリを作成"""
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        self.context_dir.mkdir(parents=True, exist_ok=True)
        
    def capture_moment(self, context_name: str, description: str = "") -> dict:
        """
        開発の瞬間を記録
        
        Args:
            context_name: コンテキストの名前（例：'feature_implementation', 'bug_fix'）
            description: 状況の説明
            
        Returns:
            dict: 記録された情報（パスなど）
        """
        # タイムスタンプ
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # スクリーンショットの保存
        screenshot_filename = f"{context_name}_{timestamp}.png"
        screenshot_path = self.screenshots_dir / screenshot_filename
        
        try:
            # スクリーンショットを撮影
            screenshot = pyautogui.screenshot()
            screenshot.save(screenshot_path)
            logger.info(f"スクリーンショットを保存しました: {screenshot_path}")
            
            # コンテキスト情報の保存
            context_info = {
                "timestamp": timestamp,
                "context_name": context_name,
                "description": description,
                "screenshot_path": str(screenshot_path)
            }
            
            context_filename = f"{context_name}_{timestamp}.json"
            context_path = self.context_dir / context_filename
            
            with open(context_path, 'w', encoding='utf-8') as f:
                json.dump(context_info, f, ensure_ascii=False, indent=2)
            
            logger.info(f"コンテキスト情報を保存しました: {context_path}")
            
            return context_info
            
        except Exception as e:
            logger.error(f"記録中にエラーが発生しました: {str(e)}")
            return {"error": str(e)}
    
    def get_recent_captures(self, limit: int = 5) -> list:
        """
        最近の記録を取得
        
        Args:
            limit: 取得する記録の数
            
        Returns:
            list: 最近の記録のリスト
        """
        try:
            # コンテキストファイルを時系列で取得
            context_files = sorted(
                self.context_dir.glob("*.json"),
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            
            recent_contexts = []
            for context_file in context_files[:limit]:
                with open(context_file, 'r', encoding='utf-8') as f:
                    context_info = json.load(f)
                    recent_contexts.append(context_info)
            
            return recent_contexts
            
        except Exception as e:
            logger.error(f"履歴の取得中にエラーが発生しました: {str(e)}")
            return []

def main():
    """メイン実行関数"""
    assistant = DevAssistant()
    
    # テスト用の記録
    context_info = assistant.capture_moment(
        "test_capture",
        "開発支援ツールのテスト記録"
    )
    
    if "error" not in context_info:
        print("記録に成功しました！")
        print(f"スクリーンショット: {context_info['screenshot_path']}")
    else:
        print(f"エラーが発生しました: {context_info['error']}")

if __name__ == "__main__":
    main() 