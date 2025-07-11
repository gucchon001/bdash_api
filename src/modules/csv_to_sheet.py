import pandas as pd
from pathlib import Path
from src.modules.spreadsheet import SpreadSheet

def upload_csv_to_sheet(csv_path: str, credentials_path: Path, spreadsheet_id: str) -> bool:
    """
    CSVファイルのデータをスプレッドシートに転記する
    毎回既存データを完全にクリアして最新データに更新する
    
    Args:
        csv_path (str): CSVファイルのパス
        credentials_path (Path): サービスアカウントの認証情報JSONファイルのパス
        spreadsheet_id (str): スプレッドシートID
        
    Returns:
        bool: 転記成功時はTrue、失敗時はFalse
    """
    try:
        # 1. CSVファイルの読み込み
        print("📄 CSVファイル読み込み開始")
        data = pd.read_csv(csv_path)
        print(f"✅ CSVファイル読込完了: {len(data)} 行")
        
        # 2. スプレッドシートに接続
        print("🔗 スプレッドシート接続開始")
        sheet = SpreadSheet(credentials_path, spreadsheet_id)
        if not sheet.connect():
            print("❌ スプレッドシートへの接続に失敗しました")
            return False
        print("✅ スプレッドシート接続完了")
        
        # 3. シートのデータを完全にクリア
        print("🗑️ 既存データの完全クリア開始")
        print("   → 全てのデータを削除して最新データに更新します")
        
        # シート全体をクリア
        sheet.sheet.clear()
        
        # 念のため、明示的に大きな範囲をクリア（A1:Z10000）
        try:
            sheet.sheet.batch_clear(['A1:Z10000'])
        except Exception as e:
            print(f"   ⚠️ 拡張クリアでエラー（通常は問題なし）: {e}")
        
        print("✅ 既存データの完全クリア完了")
        
        # 4. データの前処理
        print("🔄 データ変換開始")
        # NaN、Inf、-Infなどの特殊な浮動小数点値をNoneに置き換え
        data = data.replace([float('inf'), float('-inf')], None)
        data = data.fillna("")  # NaNを空文字列に変換
        
        # 5. データフレームをリストに変換
        headers = data.columns.tolist()
        values = data.values.tolist()
        all_values = [headers] + values
        print(f"✅ データ変換完了: ヘッダー {len(headers)} 列, データ {len(values)} 行")
        
        # 6. 列のインデックスをExcel風の列文字に変換する関数
        def num_to_col_letter(n):
            string = ""
            while n > 0:
                n, remainder = divmod(n - 1, 26)
                string = chr(65 + remainder) + string
            return string
        
        # 7. 最後の列のインデックスから列名を取得
        last_col = num_to_col_letter(len(headers))
        cell_range = f'A1:{last_col}{len(values) + 1}'
        print(f"📋 更新範囲: {cell_range}")
        
        # 8. スプレッドシートに最新データを書き込み
        print("📝 最新データの書き込み開始")
        sheet.sheet.update(values=all_values, range_name=cell_range)
        print(f"✅ 最新データの書き込み完了: {len(values)}行 x {len(headers)}列")
        
        # 9. 処理完了の確認
        print("🎉 データ更新処理完了")
        print(f"   → 既存データを全削除して最新の{len(values)}行のデータに更新しました")
        
        return True
    except Exception as e:
        print(f"❌ スプレッドシートへの転記処理でエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return False 