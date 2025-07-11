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
    print("🚀 b→dash APIデータ同期システム開始")
    print("🌐 b→dash APIからデータを取得してスプレッドシートに転記します...")
    
    success = process_bdash_api()
    
    if success:
        print("✅ b→dash APIデータ同期完了")
    else:
        print("❌ b→dash APIデータ同期失敗")
    
    print("\n" + "=" * 60)
    input("処理が完了しました。Enter キーを押してください...")

if __name__ == "__main__":
    main() 