import pyautogui
import time
import sys
from pathlib import Path

# パス設定
BASE_DIR = Path(__file__).resolve().parent.parent
IMG_DIR = BASE_DIR / "images"
SCREENSHOT_DIR = BASE_DIR / "screenshots"

# 認識のしきい値
CONFIDENCE = 0.85 

# 欠損している画像ファイル名を記録するセット（エラーの連続表示を防ぐため）
MISSING_IMAGES = set()

def click_image(image_filename, retries=3, delay=1.0):
    img_path = str(IMG_DIR / image_filename)
    
    if not Path(img_path).exists():
        # まだ警告を出していない画像の場合のみエラーを表示
        if image_filename not in MISSING_IMAGES:
            print(f"【エラー】画像ファイルが見つかりません: {image_filename} (以降の警告は省略します)")
            MISSING_IMAGES.add(image_filename)
        return False

    for _ in range(retries):
        try:
            pos = pyautogui.locateCenterOnScreen(img_path, confidence=CONFIDENCE)
            if pos:
                # Retinaディスプレイ等でクリック位置がずれる場合は下のコメントアウトを外して調整
                # click_x, click_y = pos.x / 2, pos.y / 2
                click_x, click_y = pos.x, pos.y
                
                pyautogui.click(click_x, click_y)
                return True
                
        except pyautogui.ImageNotFoundException:
            pass
        
        time.sleep(delay)
        
    return False

def check_mac_permissions():
    """画面収録の権限チェック"""
    print("システムの画面収録権限をチェックしています...")
    screenshot = pyautogui.screenshot()
    colors = screenshot.getcolors(maxcolors=1000)
    if colors and len(colors) == 1:
        print("【警告】画面が単色で取得されています。Macの「画面収録」権限を確認してください。")
    else:
        print(" -> 画面の取得は正常に行われているようです。\n")

def main_loop():
    print("=== 画像認識BOT 起動 ===")
    print(f"画像フォルダ: {IMG_DIR}")
    print(f"スクショ保存フォルダ: {SCREENSHOT_DIR}")
    
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    check_mac_permissions()
    print("停止するにはターミナルで Ctrl+C を押してください。\n")
    
    try:
        while True:
            print("1. 「掘り出し物を見る」(horidashi.png) を探しています...")
            if click_image("horidashi.png", retries=3):
                print(" -> タップしました。画面遷移を待ちます。(1秒)")
                time.sleep(1)

                timestamp_view = time.strftime("%Y%m%d_%H%M%S")
                filename_view = f"sc_{timestamp_view}.png"
                pyautogui.screenshot().save(SCREENSHOT_DIR / filename_view)
                
                time.sleep(1) 
                
                print("2. 商品（karusaito / sufe-n）を探しています...")
                if click_image("karusaito.png", retries=2) or click_image("sufe-n.png", retries=2):
                    print(" -> 対象商品を発見し、タップしました！")
                    time.sleep(1)
                    
                    print("3. 「はい」(yes.png) を探しています...")
                    if click_image("yes.png", retries=3):
                        print(" -> 購入処理を実行しました。演出完了を待ちます。(3秒)")
                        time.sleep(3) 

                        print(" -> 購入後のスクリーンショットを撮影します...")
                        timestamp_buy = time.strftime("%Y%m%d_%H%M%S")
                        filename_buy = f"purchased_item_{timestamp_buy}.png"
                        pyautogui.screenshot().save(SCREENSHOT_DIR / filename_buy)
                        print(f" -> 購入結果を保存しました: {filename_buy}")
                        
                        # --- 【変更箇所】「OK」ボタンを2種類の画像で無限ループ待機 ---
                        print("4. 「OK」(ok.png または ok2.png) の出現を待機しています...")
                        while True:
                            # retries=1にして、このwhileループ自体でリトライを管理します
                            if click_image("ok.png", retries=1, delay=0.5) or click_image("ok2.png", retries=1, delay=0.5):
                                print(" -> 「OK」をタップしました。")
                                time.sleep(2) # 画面遷移の待機
                                break # OKが見つかったので無限ループを抜ける
                            # 見つからない場合は1秒待機して再チェック（CPU負荷の軽減）
                            time.sleep(1)
                            
                        # --- 【追加箇所】OKの後の「戻る」処理 ---
                        print("5. 購入完了後の「戻る」(return.png) を待機しています...")
                        while True:
                            if click_image("return.png", retries=1, delay=0.5):
                                print(" -> 「戻る」をタップしました。次の探索へ移行します。")
                                time.sleep(2) # メイン画面に戻るまでの待機
                                break # 戻るが見つかったので無限ループを抜ける
                            time.sleep(1)

                else:
                    # 商品がなかった場合の「戻る」処理はそのまま
                    print(" -> 対象商品はありませんでした。「戻る」(return.png)を探します。")
                    if click_image("return.png", retries=3):
                        print(" -> 「戻る」をタップしました。")
                        time.sleep(2)
            else:
                print(" -> 「掘り出し物を見る」が見つかりません。3秒後に再試行します。")
                time.sleep(3)
                
    except KeyboardInterrupt:
        print("\nスクリプトを安全に終了しました。")
        sys.exit()

if __name__ == "__main__":
    main_loop()