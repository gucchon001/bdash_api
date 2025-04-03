from src.utils.environment import EnvironmentUtils as env
import os

def main():
    # 設定ファイルからファイルパスを取得
    file_path = env.get_config_value('FILE', 'file_path', 'default_path.mer')

    # ファイルパスの拡張子を変更
    csv_file_path = os.path.splitext(file_path)[0] + '.csv'

    # 新しいファイルパスを出力
    print(f"CSVファイルパス: {csv_file_path}")

if __name__ == "__main__":
    main() 