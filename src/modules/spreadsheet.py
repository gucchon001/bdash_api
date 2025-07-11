from pathlib import Path
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from typing import List, Dict, Optional

class SpreadSheet:
    def __init__(self, credentials_path: Path, spreadsheet_key: str):
        """
        Args:
            credentials_path (Path): サービスアカウントの認証情報JSONファイルのパス
            spreadsheet_key (str): スプレッドシートのキー
        """
        self.credentials_path = credentials_path
        self.spreadsheet_key = spreadsheet_key
        self.client = None
        self.sheet = None

    def connect(self) -> bool:
        """
        スプレッドシートに接続します。シートが存在しない場合は作成します。

        Returns:
            bool: 接続成功したかどうか
        """
        try:
            # APIスコープの設定
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # 認証情報の設定
            credentials = ServiceAccountCredentials.from_json_keyfile_name(
                str(self.credentials_path), scope
            )
            
            # クライアントの初期化
            self.client = gspread.authorize(credentials)
            
            # スプレッドシートを開く
            workbook = self.client.open_by_key(self.spreadsheet_key)
            
            # シートを取得
            try:
                # 既存のシートを開く
                self.sheet = workbook.sheet1  # デフォルトのシートを開く
            except Exception as e:
                print(f"シートの取得に失敗: {str(e)}")
                return False
            
            return True
            
        except Exception as e:
            print(f"スプレッドシートへの接続に失敗: {str(e)}")
            return False

    def get_last_row(self) -> Optional[int]:
        """
        スプレッドシートの最終行を取得します。

        Returns:
            Optional[int]: 最終行の番号。エラー時はNone
        """
        try:
            return len(self.sheet.col_values(1))
        except Exception as e:
            print(f"最終行の取得に失敗: {str(e)}")
            return None 