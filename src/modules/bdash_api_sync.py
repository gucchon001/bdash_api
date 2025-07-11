"""
b→dash APIからデータを取得してスプレッドシートに転記するモジュール
"""

import requests
import pandas as pd
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from src.utils.environment import EnvironmentUtils as env
from src.modules.csv_to_sheet import upload_csv_to_sheet
from src.modules.spreadsheet import SpreadSheet

class BDashAPISync:
    """b→dash APIとの連携を管理するクラス"""
    
    def __init__(self):
        """初期化"""
        self.base_url = "https://api.smart-bdash.com/api/v1"
        self.api_key = None
        self.datafile_id = None
        
    def setup_api_credentials(self) -> bool:
        """
        環境変数からAPIキーとデータファイルIDを設定
        
        Returns:
            bool: 設定成功時はTrue、失敗時はFalse
        """
        try:
            # 環境変数をロード
            env.load_env()
            
            # APIキーを取得
            self.api_key = env.get_env_var("BDASH_API_KEY")
            if not self.api_key:
                print("❌ b→dash APIキーが設定されていません")
                return False
                
            # データファイルIDを取得
            self.datafile_id = env.get_config_value("BDASH", "datafile_id", "503")
            
            print(f"✅ API設定完了: データファイルID={self.datafile_id}")
            return True
            
        except Exception as e:
            print(f"❌ API設定エラー: {e}")
            return False
    
    def fetch_data(self, limit: int = 5000) -> Optional[Dict[str, Any]]:
        """
        b→dash APIからデータを取得
        
        Args:
            limit (int): 取得するレコード数の上限
            
        Returns:
            Optional[Dict[str, Any]]: 取得したデータ、エラー時はNone
        """
        try:
            # エンドポイントURL
            endpoint = f"{self.base_url}/datafiles/{self.datafile_id}/records"
            
            # ヘッダー設定
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json; charset=UTF-8'
            }
            
            # パラメータ設定
            params = {'limit': limit}
            
            print(f"🚀 b→dash APIからデータを取得中...")
            print(f"📡 リクエストURL: {endpoint}")
            print(f"📊 取得予定件数: {limit}件")
            
            # APIリクエスト
            response = requests.get(endpoint, headers=headers, params=params)
            
            if response.status_code == 206:  # Partial Content
                data = response.json()
                print(f"✅ データ取得成功: {len(data.get('result', {}).get('records', []))}件")
                return data
            else:
                print(f"❌ データ取得失敗: {response.status_code}")
                print(f"エラーレスポンス: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ データ取得エラー: {e}")
            return None
    
    def convert_to_dataframe(self, data: Dict[str, Any]) -> Optional[pd.DataFrame]:
        """
        APIレスポンスをPandasのDataFrameに変換
        
        Args:
            data (Dict[str, Any]): APIレスポンスデータ
            
        Returns:
            Optional[pd.DataFrame]: 変換後のDataFrame、エラー時はNone
        """
        try:
            if 'result' not in data:
                print("❌ データの構造が不正です")
                return None
            
            result = data['result']
            header_info = result.get('header_info', [])
            records = result.get('records', [])
            
            if not header_info or not records:
                print("❌ ヘッダー情報またはレコードが見つかりません")
                return None
            
            # DataFrameを作成
            df = pd.DataFrame(records)
            
            # カラム名のマッピングを作成（内部ID → 日本語名）
            column_mapping = {}
            for col in header_info:
                # 内部的なカラムIDを小文字に変換
                internal_id = col.get('column_id', '').lower()
                # 実際のレコードで使用されている形式に合わせる
                for record in records:
                    for key in record.keys():
                        if key.lower() == internal_id:
                            column_mapping[key] = col.get('column_name', key)
                            break
            
            # カラム名を日本語名に変換
            original_columns = df.columns.tolist()
            new_columns = []
            for col in original_columns:
                japanese_name = column_mapping.get(col, col)
                new_columns.append(japanese_name)
            
            df.columns = new_columns
            
            # 配信年月で並べ替え（昇順）
            date_column = None
            for col in df.columns:
                if '配信年月' in col or '年月' in col:
                    date_column = col
                    break
            
            if date_column:
                print(f"📅 配信年月カラム '{date_column}' で昇順に並べ替えます")
                try:
                    # YYYY/MM形式をYYYY-MM-01形式に変換してソート
                    df['_sort_date'] = pd.to_datetime(df[date_column] + '/01', format='%Y/%m/%d', errors='coerce')
                    df_sorted = df.sort_values('_sort_date', ascending=True)
                    df_sorted = df_sorted.drop('_sort_date', axis=1)  # ソート用カラムを削除
                    df = df_sorted
                    print(f"✅ 配信年月で昇順に並べ替えました")
                except Exception as e:
                    print(f"⚠️ 配信年月の並べ替えに失敗: {e}")
                    print("📋 元の順序でデータを処理します")
            
            print(f"📊 DataFrame作成完了: {len(df)}行 × {len(df.columns)}列")
            return df
            
        except Exception as e:
            print(f"❌ DataFrame変換エラー: {e}")
            return None
    
    def save_to_csv(self, df: pd.DataFrame, filename: Optional[str] = None) -> Optional[str]:
        """
        DataFrameをCSVファイルとして保存
        
        Args:
            df (pd.DataFrame): 保存するDataFrame
            filename (Optional[str]): ファイル名（Noneの場合は自動生成）
            
        Returns:
            Optional[str]: 保存したファイルのパス、エラー時はNone
        """
        try:
            # dataフォルダを作成
            os.makedirs('data', exist_ok=True)
            
            # ファイル名を生成
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"bdash_datafile_{self.datafile_id}_{timestamp}.csv"
            
            filepath = f'data/{filename}'
            
            # CSVファイルとして保存（UTF-8 BOM付きで保存してExcelでも正しく表示）
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
            
            print(f"✅ CSVファイルを保存しました: {filepath}")
            print(f"📊 保存データ: {len(df)}行 × {len(df.columns)}列")
            
            return filepath
            
        except Exception as e:
            print(f"❌ CSV保存エラー: {e}")
            return None
    
    def upload_to_spreadsheet(self, csv_path: str) -> bool:
        """
        CSVファイルをGoogleスプレッドシートにアップロード
        
        Args:
            csv_path (str): アップロードするCSVファイルのパス
            
        Returns:
            bool: アップロード成功時はTrue、失敗時はFalse
        """
        try:
            # サービスアカウントファイルのパスを取得
            credentials_path = env.get_service_account_file()
            
            # スプレッドシートIDを取得
            spreadsheet_id = env.get_config_value('SPREADSHEET', 'ssid', '')
            if not spreadsheet_id:
                print("❌ スプレッドシートIDが設定されていません")
                return False
            
            print(f"📋 スプレッドシートID: {spreadsheet_id}")
            print(f"🔐 認証ファイル: {credentials_path}")
            
            # CSVファイルをスプレッドシートにアップロード
            result = upload_csv_to_sheet(csv_path, credentials_path, spreadsheet_id)
            
            if result:
                print("✅ スプレッドシートへの転記が完了しました")
                return True
            else:
                print("❌ スプレッドシートへの転記に失敗しました")
                return False
                
        except Exception as e:
            print(f"❌ スプレッドシート転記エラー: {e}")
            return False
    
    def sync_data_to_spreadsheet(self, limit: int = 5000) -> bool:
        """
        b→dash APIからデータを取得してスプレッドシートに同期
        
        Args:
            limit (int): 取得するレコード数の上限
            
        Returns:
            bool: 同期成功時はTrue、失敗時はFalse
        """
        try:
            print("🚀 b→dash APIデータ同期開始")
            print("=" * 60)
            
            # 1. API認証情報の設定
            if not self.setup_api_credentials():
                return False
            
            # 2. データ取得
            data = self.fetch_data(limit)
            if not data:
                return False
            
            # 3. DataFrameに変換
            df = self.convert_to_dataframe(data)
            if df is None:
                return False
            
            # 4. CSVファイルとして保存
            csv_path = self.save_to_csv(df)
            if not csv_path:
                return False
            
            # 5. スプレッドシートにアップロード
            if not self.upload_to_spreadsheet(csv_path):
                return False
            
            print("=" * 60)
            print("🎉 b→dash APIデータ同期完了")
            print(f"📊 処理データ: {len(df)}行 × {len(df.columns)}列")
            
            # 配信年月の範囲を表示
            date_column = None
            for col in df.columns:
                if '配信年月' in col or '年月' in col:
                    date_column = col
                    break
            
            if date_column and date_column in df.columns:
                date_values = df[date_column].dropna().unique()
                if len(date_values) > 0:
                    print(f"📅 配信年月の範囲: {min(date_values)} ～ {max(date_values)}")
                    print(f"📊 配信年月の種類: {len(date_values)}種類")
            
            return True
            
        except Exception as e:
            print(f"❌ データ同期エラー: {e}")
            import traceback
            traceback.print_exc()
            return False 