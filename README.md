# B→dash API データ同期システム

B→dash APIからデータを取得してGoogleスプレッドシートに転記するPythonアプリケーションです。

## 📋 機能

- B→dash APIからのデータ取得
- CSVファイルへの保存
- Googleスプレッドシートへの転記
- 自動環境設定と依存関係管理
- タスクスケジューラー対応

## 🚀 実行方法

### 1. 対話式実行（開発・テスト用）

```bash
# バッチファイル実行
.\run_dev.bat

# PowerShell実行
.\run_dev.ps1 -Environment dev -Test
```

### 2. 本番実行

```bash
# バッチファイル実行
.\run.bat

# PowerShell実行
.\run.ps1
```

### 3. タスクスケジューラー実行（自動化）

対話的な要素を排除したサイレント実行：

```bash
# 専用サイレントスクリプト
.\run_silent.bat          # バッチファイル版
.\run_silent.ps1          # PowerShell版

# 既存スクリプトのサイレントモード
.\run.bat --silent
```

## ⚙️ タスクスケジューラー設定

### Windows タスクスケジューラーでの設定例

1. **タスクスケジューラーを開く**
   - `taskschd.msc` を実行

2. **基本タスクの作成**
   - 名前: `B-dash API Sync`
   - 説明: `B→dash APIデータ同期処理`

3. **トリガー設定**
   - 毎日 / 毎週 / 毎月など必要に応じて設定

4. **操作設定**
   - プログラム/スクリプト: `powershell.exe`
   - 引数: `-ExecutionPolicy Bypass -File "C:\path\to\bdash_api\run_silent.ps1"`
   - 開始場所: `C:\path\to\bdash_api`

### バッチファイル使用の場合
   - プログラム/スクリプト: `C:\path\to\bdash_api\run_silent.bat`
   - 開始場所: `C:\path\to\bdash_api`

## 📁 プロジェクト構造

```
bdash_api/
├── config/                    # 設定ファイル
│   └── settings.ini
├── src/                       # ソースコード
│   ├── main.py               # メインエントリーポイント
│   ├── modules/              # 機能別モジュール
│   └── utils/                # ユーティリティ
├── logs/                     # ログファイル出力先
├── data/                     # データファイル保存先
├── tests/                    # テストコード
├── requirements.txt          # Python依存関係
├── run.bat                   # 対話式実行（バッチ）
├── run.ps1                   # 対話式実行（PowerShell）
├── run_dev.bat              # 開発用実行（バッチ）
├── run_dev.ps1              # 開発用実行（PowerShell）
├── run_silent.bat           # サイレント実行（バッチ）
└── run_silent.ps1           # サイレント実行（PowerShell）
```

## 🔧 実行スクリプトの選び方

| スクリプト | 用途 | 特徴 |
|-----------|------|------|
| `run_dev.*` | 開発・テスト | 詳細ログ、対話式選択 |
| `run.*` | 手動実行 | 本番環境、対話式確認 |
| `run_silent.*` | 自動実行 | タスクスケジューラー対応、ログファイル出力 |

## 📊 PowerShellスクリプトのオプション

```powershell
# 基本実行
.\run.ps1

# 開発環境でテストモード
.\run.ps1 -Environment dev -Test

# 特定モジュールの実行
.\run.ps1 -Module spreadsheet

# パッケージインストールをスキップ
.\run.ps1 -NoInstall

# 仮想環境を強制再作成
.\run.ps1 -Force
```

## 🔍 ログ確認

- **対話式実行**: コンソール出力
- **サイレント実行**: `logs/scheduler_YYYYMMDD_HHMMSS.log`

## 📝 設定

1. `config/settings.ini` でAPIキーとスプレッドシートIDを設定
2. `config/secrets.env` で認証情報を設定
3. 必要に応じて `requirements.txt` で依存関係を管理

## 🛠️ トラブルシューティング

### タスクスケジューラーでの問題

1. **PowerShell実行ポリシー**
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

2. **パスの設定**
   - 絶対パスを使用してください
   - 開始場所を正しく設定してください

3. **権限の確認**
   - 実行ユーザーに適切な権限があることを確認

### ログの確認方法
```bash
# 最新のログファイルを確認
Get-ChildItem logs\scheduler_*.log | Sort-Object LastWriteTime -Descending | Select-Object -First 1 | Get-Content
```

## 📞 サポート

問題が発生した場合は、以下を確認してください：
- ログファイルの内容
- 設定ファイルの内容
- 実行環境（Python、仮想環境、依存関係）

## 📈 バージョン履歴

- v1.0: 初期リリース
- v1.1: PowerShellスクリプト追加
- v1.2: タスクスケジューラー対応、サイレント実行機能追加 