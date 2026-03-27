import pyautogui
import time
import sys
from pathlib import Path

# プロジェクトルートディレクトリと画像ディレクトリのパスを取得
BASE_DIR = Path(__file__).resolve().parent.parent
IMG_DIR = BASE_DIR / "images"

# --- 設定項目 ---
# 認識のしきい値（0.0〜1.0）。0.8〜0.9あたりが誤動作が少なくおすすめ
CONFIDENCE = 0.80 
# ---------------

def click_image(image_filename, retries=3, delay=1.0):
    """
    画面内から画像を探し、見つかれば中心をクリックしてTrueを返す。
    見つからなければFalseを返す。
    """
    img_path = str(IMG_DIR / image_filename)
    
    # ファイルが存在するかチェック
    if not Path(img_path).exists():
        print(f"【警告】画像ファイルが見つかりません: {image_filename}")
        return False

    for _ in range(retries):
        try:
            # confidenceを使用するには opencv-python が必要
            pos = pyautogui.locateCenterOnScreen(img_path, confidence=CONFIDENCE)
            if pos:
                # MacのRetinaディスプレイ環境で座標がずれる場合は、
                # pos.x / 2, pos.y / 2 のように調整が必要な場合があります。
                pyautogui.click(pos)
                return True
        except pyautogui.ImageNotFoundException:
            pass # 見つからなかった場合は例外を無視して待機へ
        
        time.sleep(delay)
        
    return False

def main_loop():
    print("画像認識による自動化を開始します。")
    print("停止するにはターミナルで Ctrl+C を押してください。\n")
    
    try:
        while True:
            print("1. 「掘り出し物を見る」を探しています...")
            if click_image("horidashi.png", retries=5):
                print(" -> タップしました。画面遷移を待ちます。")
                time.sleep(2) # 遷移待ち
                
                print("2. 商品（カルサイト or スフェーン）を探しています...")
                # どちらかが見つかるかチェック
                if click_image("karusaito.png", retries=2) or click_image("sufe-n.png", retries=2):
                    print(" -> 対象商品を発見し、タップしました！")
                    time.sleep(1) # ダイアログ表示待ち
                    
                    print("3. 「はい」を探しています...")
                    if click_image("yes.png"):
                        print(" -> 購入処理を実行しました。")
                        time.sleep(3) # 購入完了演出などの待機
                else:
                    print(" -> 対象商品はありませんでした。「戻る」を探します。")
                    if click_image("return.png"):
                        print(" -> 「戻る」をタップしました。")
                        time.sleep(2) # 遷移待ち
            else:
                print(" -> 「掘り出し物を見る」が見つかりません。3秒後に再試行します。")
                time.sleep(3)
                
    except KeyboardInterrupt:
        print("\nスクリプトを終了しました。")
        sys.exit()

if __name__ == "__main__":
    main_loop()