import requests

BASE_URL = "http://127.0.0.1:8000"
# APIのmain.pyで定義されているパスワード
ADMIN_PASSWORD = "cm2025"
TOKEN = None

def login():
    """APIにログインして認証トークンを取得する"""
    global TOKEN
    payload = {"password": ADMIN_PASSWORD}
    try:
        response = requests.post(f"{BASE_URL}/login", json=payload)
        response.raise_for_status()
        TOKEN = response.json().get("token")
        if TOKEN:
            print("ログインに成功しました。")
            return True
        else:
            print("エラー: トークンがレスポンスに含まれていません。")
            return False
    except requests.exceptions.RequestException as e:
        print(f"ログインに失敗しました: {e}")
        return False

def create_class(name):
    """新しいクラスを作成する"""
    if not TOKEN:
        print("ログインしていません。クラスを作成できません。")
        return

    headers = {"Authorization": f"Bearer {TOKEN}"}
    payload = {"name": name}
    try:
        response = requests.post(f"{BASE_URL}/classes/", headers=headers, json=payload)
        if response.status_code == 200:
            print(f"成功: クラス '{name}' を作成しました。")
        elif response.status_code == 400 and "already exists" in response.text:
            print(f"情報: クラス '{name}' は既に存在します。")
        else:
            response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"エラー: クラス '{name}' の作成中にエラーが発生しました: {e}")

def main():
    """ログインして、必要な全てのクラスを作成する"""
    print("--- ログイン処理を開始します ---")
    if not login():
        return

    print("--- クラスの作成を開始します ---")
    
    class_names = []
    for grade in range(1, 4):
        for group in range(1, 7):
            class_names.append(f"{grade}-{group}")

    for name in class_names:
        create_class(name)
        
    print("--- クラスの作成が完了しました ---")

if __name__ == "__main__":
    main()
