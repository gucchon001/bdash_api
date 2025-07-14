import sys
import os
from pathlib import Path

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.environment import EnvironmentUtils as env
from src.modules.bdash_api_sync import BDashAPISync

def process_bdash_api():
    """b→dash APIからデータを取得してスプレッドシートに転記"""
    print("=" * 60)
    print("🚀 b→dash APIデータ同期開始")
    print("=" * 60)
    
    try:
        # BDashAPISyncクラスのインスタンスを作成
        bdash_sync = BDashAPISync()
        
        # データ同期を実行
        result = bdash_sync.sync_data_to_spreadsheet(limit=5000)
        
        if result:
            print("=" * 60)
            print("🎉 b→dash APIデータ同期完了")
            return True
        else:
            print("=" * 60)
            print("❌ b→dash APIデータ同期失敗")
            return False
            
    except Exception as e:
        print(f"❌ b→dash APIデータ同期エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """メイン処理"""
    # サイレントモード判定
    is_silent = len(sys.argv) > 1 and any(arg in ['--silent', '--no-wait', '--batch'] for arg in sys.argv)
    
    if not is_silent:
        print("🚀 b→dash APIデータ同期システム開始")
        print("🌐 b→dash APIからデータを取得してスプレッドシートに転記します...")
    
    success = process_bdash_api()
    
    if success:
        if not is_silent:
            print("✅ b→dash APIデータ同期完了")
    else:
        if not is_silent:
            print("❌ b→dash APIデータ同期失敗")
    
    if not is_silent:
        print("\n" + "=" * 60)
        input("処理が完了しました。Enter キーを押してください...")
    else:
        # サイレントモードでは何も出力しない
        pass

if __name__ == "__main__":
    main() 