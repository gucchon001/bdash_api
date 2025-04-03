# 開発手順書

## 目的
この手順書は、`config/settings.ini` からファイルを読み取り、そのデータをGoogleスプレッドシートにアップロードするプロセスを説明します。

## 手順

### 1. `config/settings.ini` からファイルを読み取る

- `EnvironmentUtils.get_config_value(section, key, default)` を使用して、設定ファイルから必要な情報を取得します。

```python
from src.utils.environment import EnvironmentUtils

# 設定ファイルからファイルパスを取得
file_path = EnvironmentUtils.get_config_value('DATA_PATHS', 'MER_FILE_PATH', 'default_path.mer')
```

### 2. 読み取ったファイルのパスの拡張子を `.mer` から `.csv` に変換

- Pythonの`os`モジュールを使用してファイルパスの拡張子を変更します。

```python
import os

# ファイルパスの拡張子を変更
csv_file_path = os.path.splitext(file_path)[0] + '.csv'
```

### 3. ファイル全体を読み取る

- `pandas`ライブラリを使用して、CSVファイルをデータフレームとして読み込みます。

```python
import pandas as pd

# CSVファイルを読み込む
data = pd.read_csv(csv_file_path)
```

### 4. `secrets.env` からスプレッドシートの認証

- `EnvironmentUtils.load_env()` を使用して環境変数をロードし、認証情報を取得します。

```python
# 環境変数をロード
EnvironmentUtils.load_env()

# 認証情報を取得
credentials = EnvironmentUtils.get_service_account_file()
```

### 5. `settings.ini` にあるSSID・シート名からスプレッドシートにアクセス

- `modules.spreadsheet.py` を使用してスプレッドシートにアクセスします。

```python
from src.modules.spreadsheet import Spreadsheet

# SSIDとシート名を取得
spreadsheet_id = EnvironmentUtils.get_config_value('SPREADSHEET', 'SSID', 'default_ssid')
sheet_name = EnvironmentUtils.get_config_value('SPREADSHEET', 'SHEET_NAME', 'default_sheet')

# スプレッドシートにアクセス
spreadsheet = Spreadsheet(credentials, spreadsheet_id, sheet_name)
```

### 6. シートのデータを全てクリア

- スプレッドシートのデータをクリアします。

```python
# シートのデータをクリア
spreadsheet.clear_sheet()
```

### 7. 3で取得したデータを貼り付け

- データフレームの内容をスプレッドシートにアップロードします。

```python
# データをスプレッドシートにアップロード
spreadsheet.update_sheet(data)
```

## 注意事項
- 環境変数や設定ファイルの情報は、`EnvironmentUtils` クラスを通じて一元管理します。
- スプレッドシートの操作には、適切な認証情報が必要です。
- データのアップロード前に、必ずデータの整合性を確認してください。
