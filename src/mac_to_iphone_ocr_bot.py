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

def click_image(image_filename, retries=3, delay=1.0):
    img_path = str(IMG_DIR / image_filename)
    
    if not Path(img_path).exists():
        print(f"【エラー】画像ファイルが見つかりません: {img_path}")
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

                # 「掘り出し物を見る」タップ後のスクショ（前回追加分）
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

                        # --- 【今回追加】購入後のスクリーンショット撮影 ---
                        print(" -> [追加機能] 購入後のスクリーンショットを撮影します...")
                        timestamp_buy = time.strftime("%Y%m%d_%H%M%S")
                        filename_buy = f"purchased_item_{timestamp_buy}.png"
                        pyautogui.screenshot().save(SCREENSHOT_DIR / filename_buy)
                        print(f" -> 購入結果を保存しました: {filename_buy}")
                        
                        # --- 【今回追加】「OK」ボタンをタップして次へ進む ---
                        print("4. 「OK」(ok.png) を探しています...")
                        # 演出でOKボタンが出るまで少し時間がかかることを想定し、リトライ回数を多め（5回=約5秒）に設定
                        if click_image("ok.png", retries=5):
                            print(" -> 「OK」をタップしました。次の探索へ戻ります。")
                            time.sleep(2) # 画面が戻るまでの待機
                        else:
                            print(" -> 「OK」が見つかりませんでした。手動で確認するか、画像を取り直してください。")

                else:
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