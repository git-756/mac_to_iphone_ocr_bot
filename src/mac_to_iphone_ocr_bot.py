import pyautogui
import time
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# パス設定
BASE_DIR = Path(__file__).resolve().parent.parent
IMG_DIR = BASE_DIR / "images"
SCREENSHOT_DIR = BASE_DIR / "screenshots"

# 認識のしきい値
CONFIDENCE = 0.85 

MISSING_IMAGES = set()

def click_image(image_filename, retries=3, delay=0.5):
    """単一の画像を探してタップする（クリック動作を少しマイルドに改良）"""
    img_path = str(IMG_DIR / image_filename)
    
    if not Path(img_path).exists():
        if image_filename not in MISSING_IMAGES:
            print(f"【エラー】画像ファイルが見つかりません: {image_filename}")
            MISSING_IMAGES.add(image_filename)
        return False

    for i in range(retries):
        try:
            pos = pyautogui.locateCenterOnScreen(img_path, confidence=CONFIDENCE)
            if pos:
                click_x, click_y = pos.x, pos.y
                # --- 改良: 0.1秒かけてカーソルを移動させ、0.1秒間押し下げるようにクリック ---
                pyautogui.moveTo(click_x, click_y, duration=0.1)
                pyautogui.click(clicks=1, interval=0.1)
                return True
        except pyautogui.ImageNotFoundException:
            pass
        
        if i < retries - 1:
            time.sleep(delay)
        
    return False

# --- 複数アイテムを並列で検索する関数 ---
def find_items_concurrently(image_filenames, confidence=CONFIDENCE):
    """
    1回のスクリーンショットに対して、複数の画像をマルチスレッドで同時に探します。
    """
    screenshot = pyautogui.screenshot()
    
    def search_single_item(filename):
        img_path = str(IMG_DIR / filename)
        if not Path(img_path).exists():
            return None
        try:
            box = pyautogui.locate(img_path, screenshot, confidence=confidence)
            if box:
                center_x, center_y = pyautogui.center(box)
                return (filename, center_x, center_y)
        except pyautogui.ImageNotFoundException:
            pass
        return None

    with ThreadPoolExecutor(max_workers=len(image_filenames)) as executor:
        results = executor.map(search_single_item, image_filenames)
        
    for res in results:
        if res is not None:
            return res
            
    return None, None, None
# --------------------------------------------------------

def check_mac_permissions():
    print("システムの画面収録権限をチェックしています...")
    screenshot = pyautogui.screenshot()
    colors = screenshot.getcolors(maxcolors=1000)
    if colors and len(colors) == 1:
        print("【警告】画面が単色で取得されています。Macの「画面収録」権限を確認してください。")
    else:
        print(" -> 画面の取得は正常に行われているようです。\n")

def main_loop():
    print("=== 画像認識BOT 起動 (並列処理・高速＆安定化版) ===")
    print(f"画像フォルダ: {IMG_DIR}")
    
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    check_mac_permissions()
    print("停止するにはターミナルで Ctrl+C を押してください。\n")
    
    try:
        while True:
            print("1. 「掘り出し物を見る」(horidashi.png) を探しています...")
            # delayを0.2から0.4にして少しだけリトライ間隔を空ける
            if click_image("horidashi.png", retries=2, delay=0.4):
                print(" -> タップしました。画面遷移を待ちます。")
                # 画面切り替わりアニメーションを確実に待つために0.4秒から0.7秒に増加
                time.sleep(0.7) 

                print("2. 商品（複数）および「終了条件」を並列で探しています...")
                target_items = ["karusaito.png", "sufe-n.png", "torife-n.png", "owari.png"]
                found_item, x, y = find_items_concurrently(target_items)
                
                if found_item == "owari.png":
                    print("\n【終了完了】「owari.png」を検出しました。自動化スクリプトを安全に終了します。")
                    sys.exit()
                
                elif found_item:
                    print(f" -> 対象商品（{found_item}）を発見し、タップしました！")
                    pyautogui.click(x, y)
                    
                    # タップ後のロード時間待ちを0.4秒から0.6秒に増加
                    time.sleep(0.6) 
                    
                    print("3. 「はい」(yes.png) を探しています...")
                    if click_image("yes.png", retries=2, delay=0.4):
                        print(" -> 購入処理を実行しました。演出完了を待ちます。")
                        # 購入演出（エフェクト等）をしっかり待つため1.0秒から1.5秒に増加
                        time.sleep(1.5) 

                        print(" -> 購入後のスクリーンショットを撮影します...")
                        timestamp_buy = time.strftime("%Y%m%d_%H%M%S")
                        filename_buy = f"purchased_item_{timestamp_buy}.png"
                        pyautogui.screenshot().save(SCREENSHOT_DIR / filename_buy)
                        print(f" -> 購入結果を保存しました: {filename_buy}")
                        
                        print("4. 「OK」(ok.png) の出現を待機しています...")
                        while True:
                            if click_image("ok.png", retries=1, delay=0):
                                print(" -> 「OK」をタップしました。")
                                # OKを押した後のポップアップ消滅を待つため0.5秒から0.7秒に増加
                                time.sleep(0.7) 
                                break 
                            # 監視ループが早すぎてCPUに負荷をかけないよう、待機を0.2秒から0.3秒へ
                            time.sleep(0.3)
                            
                        print("5. 購入完了後の「戻る」(return.png) を待機しています...")
                        while True:
                            if click_image("return.png", retries=1, delay=0):
                                print(" -> 「戻る」をタップしました。次の探索へ移行します。")
                                # 戻った後の画面描画待ちを0.5秒から0.7秒に増加
                                time.sleep(0.7) 
                                break 
                            time.sleep(0.3)

                else:
                    print(" -> 対象商品はありませんでした。「戻る」(return.png)を探します。")
                    if click_image("return.png", retries=2, delay=0.4):
                        print(" -> 「戻る」をタップしました。")
                        # 戻り遷移の待ち時間を0.4秒から0.6秒に増加
                        time.sleep(0.6)
            else:
                print(" -> 「掘り出し物を見る」が見つかりません。1秒後に再試行します。")
                time.sleep(1.2) 
                
    except KeyboardInterrupt:
        print("\nスクリプトを安全に終了しました。")
        sys.exit()

if __name__ == "__main__":
    main_loop()