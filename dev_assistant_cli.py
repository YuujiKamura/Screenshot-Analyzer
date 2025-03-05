"""
開発支援ツールのコマンドラインインターフェース
"""
import argparse
from dev_assistant import DevAssistant

def parse_args():
    """コマンドライン引数をパース"""
    parser = argparse.ArgumentParser(
        description="開発支援ツール - スクリーンショットと開発コンテキストの記録"
    )
    
    # サブコマンドの設定
    subparsers = parser.add_subparsers(dest="command", help="実行するコマンド")
    
    # キャプチャコマンド
    capture_parser = subparsers.add_parser("capture", help="現在の状態を記録")
    capture_parser.add_argument(
        "--name",
        "-n",
        required=True,
        help="記録の名前（例：feature_implementation）"
    )
    capture_parser.add_argument(
        "--description",
        "-d",
        default="",
        help="状況の説明"
    )
    
    # 履歴表示コマンド
    history_parser = subparsers.add_parser("history", help="記録の履歴を表示")
    history_parser.add_argument(
        "--limit",
        "-l",
        type=int,
        default=5,
        help="表示する記録の数"
    )
    
    return parser.parse_args()

def main():
    """メイン実行関数"""
    args = parse_args()
    assistant = DevAssistant()
    
    if args.command == "capture":
        # 状態を記録
        result = assistant.capture_moment(args.name, args.description)
        if "error" not in result:
            print("記録に成功しました！")
            print(f"スクリーンショット: {result['screenshot_path']}")
        else:
            print(f"エラーが発生しました: {result['error']}")
            
    elif args.command == "history":
        # 履歴を表示
        history = assistant.get_recent_captures(args.limit)
        if history:
            print(f"最近の記録（{len(history)}件）:")
            for i, record in enumerate(history, 1):
                print(f"\n{i}. {record['context_name']}")
                print(f"   時刻: {record['timestamp']}")
                if record['description']:
                    print(f"   説明: {record['description']}")
                print(f"   スクリーンショット: {record['screenshot_path']}")
        else:
            print("記録が見つかりませんでした。")
    
    else:
        print("コマンドを指定してください。")
        print("使用例:")
        print("  python dev_assistant_cli.py capture -n feature_test -d 'テスト機能の実装'")
        print("  python dev_assistant_cli.py history -l 3")

if __name__ == "__main__":
    main() 