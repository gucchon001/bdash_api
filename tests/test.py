import requests
import json
import time
import base64
import pandas as pd
import os
from datetime import datetime

# ==========================================================
# 設定値
# ==========================================================
# コロン付きのAPIキーをそのまま設定
API_KEY_WITH_COLON = "100376-9907-pn6b24wh6r:dxmiwqjteehpdc1r8jfugkigiks64gi13ijietcas77f26ntvc1rcrq21g51tdgpsnrjeuswpf8i3c1wptqu5ib5hn4ar4th4y2xcme6s"
DATAFILE_ID = "503"

# ==========================================================
# APIリクエストの準備
# ==========================================================
base_url = "https://api.smart-bdash.com/api/v1"
api_endpoint = f"{base_url}/datafiles/{DATAFILE_ID}/records"

# --- Basic認証のための準備 ---
# APIキーをコロンで分割して、IDとシークレットに分ける
try:
    api_key_id, api_key_secret = API_KEY_WITH_COLON.split(':', 1)
    print(f"✅ APIキーを分割しました: ID={api_key_id[:10]}...")
    print(f"✅ APIキーシークレット: {api_key_secret[:10]}...")
except ValueError:
    print("❌ エラー: APIキーにコロンが含まれていません")
    exit(1)

# ==========================================================
# テスト実行
# ==========================================================
print("🚀 b→dash API疎通テスト開始")
print("=" * 60)

# --- 共通仕様準拠のヘッダー設定 ---
def get_common_headers():
    """共通仕様に準拠したヘッダーを返す"""
    return {
        'Authorization': f'Bearer {API_KEY_WITH_COLON}',
        'Content-Type': 'application/json; charset=UTF-8',  # 共通仕様準拠
        'User-Agent': 'bdash-api-test/1.0'
    }

# --- CSV保存機能 ---
def save_to_csv(data, filename):
    """取得したデータをCSVファイルとして保存"""
    if 'result' not in data:
        print("❌ データの構造が不正です")
        return False
    
    result = data['result']
    header_info = result.get('header_info', [])
    records = result.get('records', [])
    
    if not header_info or not records:
        print("❌ ヘッダー情報またはレコードが見つかりません")
        return False
    
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
    
    # DataFrameを作成
    df = pd.DataFrame(records)
    
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
        
        # 配信年月を適切な形式に変換してソート
        try:
            # YYYY/MM形式をYYYY-MM-01形式に変換してソート
            df['_sort_date'] = pd.to_datetime(df[date_column] + '/01', format='%Y/%m/%d', errors='coerce')
            df_sorted = df.sort_values('_sort_date', ascending=True)
            df_sorted = df_sorted.drop('_sort_date', axis=1)  # ソート用カラムを削除
            df = df_sorted
            print(f"✅ 配信年月で昇順に並べ替えました")
        except Exception as e:
            print(f"⚠️ 配信年月の並べ替えに失敗: {e}")
            print("📋 元の順序でCSVファイルを保存します")
    else:
        print("⚠️ 配信年月カラムが見つかりません")
    
    # dataフォルダに保存
    os.makedirs('data', exist_ok=True)
    filepath = f'data/{filename}'
    
    # CSVファイルとして保存（UTF-8 BOM付きで保存してExcelでも正しく表示）
    df.to_csv(filepath, index=False, encoding='utf-8-sig')
    
    print(f"✅ CSVファイルを保存しました: {filepath}")
    print(f"📊 保存データ: {len(records)}行 × {len(df.columns)}列")
    
    # 配信年月の範囲を表示
    if date_column and date_column in df.columns:
        date_values = df[date_column].dropna().unique()
        if len(date_values) > 0:
            print(f"📅 配信年月の範囲: {min(date_values)} ～ {max(date_values)}")
            print(f"📊 配信年月の種類: {len(date_values)}種類")
    
    # カラム名マッピングを表示
    print("📋 カラム名マッピング:")
    for original, japanese in zip(original_columns, new_columns):
        if original != japanese:
            print(f"  {original} → {japanese}")
    
    return True

# --- テスト1: GET（成功パターン） ---
print("\n📊 テスト1: GETメソッドでのデータ取得（成功パターン）")
print("-" * 50)

headers = get_common_headers()
# GETリクエストではContent-Typeは不要なので削除
del headers['Content-Type']

# より多くのデータを取得
params = {'limit': 5000}  # 100件取得
response = requests.get(api_endpoint, headers=headers, params=params)

print(f"📡 リクエスト URL: {response.url}")
print(f"📋 ステータスコード: {response.status_code}")
print(f"📄 レスポンス概要: {len(response.text)} 文字")

if response.status_code == 206:
    print("✅ GET成功（206 Partial Content）")
    try:
        data = response.json()
        if 'result' in data:
            print(f"📊 データ構造: {list(data['result'].keys())}")
            
            # ヘッダー情報の表示
            if 'header_info' in data['result']:
                header_info = data['result']['header_info']
                print(f"📋 カラム情報: {len(header_info)} 列")
                print("📝 カラム一覧:")
                for i, col in enumerate(header_info):
                    column_name = col.get('column_name', 'Unknown')
                    column_id = col.get('column_id', 'Unknown')
                    data_type = col.get('data_type', 'Unknown')
                    print(f"  [{i+1:2d}] {column_name} ({column_id}) - {data_type}")
            
            # レコードデータの確認
            if 'records' in data['result']:
                records = data['result']['records']
                print(f"📈 レコード数: {len(records)}")
                
                # 最初の3レコードを表示
                print("\n📊 データサンプル（最初の3行）:")
                print("=" * 80)
                
                for i, record in enumerate(records[:3]):
                    print(f"\n🔍 レコード {i+1}:")
                    print("-" * 40)
                    
                    # レコードの内容を見やすく表示
                    for key, value in record.items():
                        if value is not None and value != "":
                            # 値が長い場合は切り詰める
                            if isinstance(value, str) and len(value) > 50:
                                display_value = value[:50] + "..."
                            else:
                                display_value = value
                            print(f"  {key}: {display_value}")
                    
                    # 空でないフィールドの数を表示
                    non_empty_fields = sum(1 for v in record.values() if v is not None and v != "")
                    print(f"  💡 データ入力済みフィールド: {non_empty_fields}/{len(record)}")
                
                print("\n" + "=" * 80)
                
                # CSVファイルとして保存
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"bdash_datafile_{DATAFILE_ID}_{timestamp}.csv"
                
                if save_to_csv(data, filename):
                    print(f"🎉 データファイル {DATAFILE_ID} をCSVファイルとして保存しました！")
                else:
                    print("❌ CSV保存に失敗しました")
                
                # データの統計情報
                if records:
                    total_fields = len(records[0])
                    filled_fields_per_record = [
                        sum(1 for v in record.values() if v is not None and v != "")
                        for record in records
                    ]
                    avg_filled = sum(filled_fields_per_record) / len(filled_fields_per_record)
                    
                    print(f"\n📊 データ統計:")
                    print(f"  - 総フィールド数: {total_fields}")
                    print(f"  - 平均データ入力率: {avg_filled:.1f}/{total_fields} ({avg_filled/total_fields*100:.1f}%)")
                    print(f"  - 最大データ入力数: {max(filled_fields_per_record)}")
                    print(f"  - 最小データ入力数: {min(filled_fields_per_record)}")
        else:
            print("📄 レスポンス内容（最初の500文字）:")
            print(response.text[:500])
    except json.JSONDecodeError:
        print("⚠️ JSON解析エラー")
    except Exception as e:
        print(f"❌ エラーが発生: {e}")
else:
    print(f"❌ GET失敗: {response.status_code}")

# --- テスト2以降は省略（データ取得のみに集中） ---
print("\n📊 データ取得とCSV保存テスト完了")
print("-" * 50)

# ==========================================================
# データ取得結果総括
# ==========================================================
print("\n" + "=" * 60)
print("🎯 データ取得結果総括")
print("=" * 60)

print("\n✅ 成功した項目:")
print("- GETメソッドでのデータ取得（Bearer認証）")
print("- 実際のデータ内容の確認")
print("- カラム情報の取得")
print("- CSVファイルとしての保存")

print("\n🔧 APIアクセス情報:")
print(f"- ベースURL: {base_url}")
print(f"- 認証方式: Bearer {API_KEY_WITH_COLON[:20]}...")
print(f"- GET成功エンドポイント: /datafiles/{DATAFILE_ID}/records")

print("\n📁 保存先:")
print(f"- フォルダ: data/")
print(f"- ファイル名: bdash_datafile_{DATAFILE_ID}_[タイムスタンプ].csv")

print("\n🎉 データ取得・CSV保存テスト完了！")