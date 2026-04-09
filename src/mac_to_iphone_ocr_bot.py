import pyautogui
import time
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor # 並列処理用に追加

# パス設定
BASE_DIR = Path(__file__).resolve().parent.parent
IMG_DIR = BASE_DIR / "images"
SCREENSHOT_DIR = BASE_DIR / "screenshots"

# 認識のしきい値
CONFIDENCE = 0.85 

MISSING_IMAGES = set()

def click_image(image_filename, retries=3, delay=0.5):
    """単一の画像を探してタップする（従来の関数）"""
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
                # Retinaディスプレイ等の調整用
                # click_x, click_y = pos.x / 2, pos.y / 2
                click_x, click_y = pos.x, pos.y
                pyautogui.click(click_x, click_y)
                return True
        except pyautogui.ImageNotFoundException:
            pass
        
        if i < retries - 1:
            time.sleep(delay)
        
    return False

# --- 【新規追加】複数アイテムを並列で爆速検索する関数 ---
def find_items_concurrently(image_filenames, confidence=CONFIDENCE):
    """
    1回のスクリーンショットに対して、複数の画像をマルチスレッドで同時に探します。
    """
    # 1. 画面全体のスクリーンショットを【1回だけ】撮影する（重い処理を1回に減らす）
    screenshot = pyautogui.screenshot()
    
    def search_single_item(filename):
        img_path = str(IMG_DIR / filename)
        if not Path(img_path).exists():
            return None
        try:
            # locateCenterOnScreenではなく、locateを使って『撮影済みのスクショ』から探す
            box = pyautogui.locate(img_path, screenshot, confidence=confidence)
            if box:
                # 見つかった領域から中心座標を計算
                center_x, center_y = pyautogui.center(box)
                return (filename, center_x, center_y)
        except pyautogui.ImageNotFoundException:
            pass
        return None

    # 2. マルチスレッドで同時に検索を実行
    with ThreadPoolExecutor(max_workers=len(image_filenames)) as executor:
        results = executor.map(search_single_item, image_filenames)
        
    # 3. 結果の確認（どれか1つでも見つかればそれを返す）
    for res in results:
        if res is not None:
            return res # (filename, x, y) を返す
            
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
    print("=== 画像認識BOT 起動 (並列処理・高速版) ===")
    print(f"画像フォルダ: {IMG_DIR}")
    
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    check_mac_permissions()
    print("停止するにはターミナルで Ctrl+C を押してください。\n")
    
    try:
        while True:
            print("1. 「掘り出し物を見る」(horidashi.png) を探しています...")
            if click_image("horidashi.png", retries=2, delay=0.2):
                print(" -> タップしました。画面遷移を待ちます。")
                time.sleep(0.4) 

                print("2. 商品（複数）を並列で探しています...")
                # --- 【変更】並列処理関数を使用するように書き換え ---
                target_items = ["karusaito.png", "sufe-n.png", "torife-n.png"]
                found_item, x, y = find_items_concurrently(target_items)
                
                if found_item:
                    print(f" -> 対象商品（{found_item}）を発見し、タップしました！")
                    
                    # Retina環境でクリックがずれる場合は、ここで / 2 を行います
                    # x, y = x / 2, y / 2
                    pyautogui.click(x, y)
                    
                    time.sleep(0.4) 
                    
                    print("3. 「はい」(yes.png) を探しています...")
                    if click_image("yes.png", retries=2, delay=0.2):
                        print(" -> 購入処理を実行しました。演出完了を待ちます。")
                        time.sleep(1.0) 

                        print(" -> 購入後のスクリーンショットを撮影します...")
                        timestamp_buy = time.strftime("%Y%m%d_%H%M%S")
                        filename_buy = f"purchased_item_{timestamp_buy}.png"
                        pyautogui.screenshot().save(SCREENSHOT_DIR / filename_buy)
                        print(f" -> 購入結果を保存しました: {filename_buy}")
                        
                        print("4. 「OK」(ok.png) の出現を待機しています...")
                        while True:
                            if click_image("ok.png", retries=1, delay=0):
                                print(" -> 「OK」をタップしました。")
                                time.sleep(0.5) 
                                break 
                            time.sleep(0.2)
                            
                        print("5. 購入完了後の「戻る」(return.png) を待機しています...")
                        while True:
                            if click_image("return.png", retries=1, delay=0):
                                print(" -> 「戻る」をタップしました。次の探索へ移行します。")
                                time.sleep(0.5) 
                                break 
                            time.sleep(0.2)

                else:
                    print(" -> 対象商品はありませんでした。「戻る」(return.png)を探します。")
                    if click_image("return.png", retries=2, delay=0.2):
                        print(" -> 「戻る」をタップしました。")
                        time.sleep(0.4)
            else:
                print(" -> 「掘り出し物を見る」が見つかりません。1秒後に再試行します。")
                time.sleep(1) 
                
    except KeyboardInterrupt:
        print("\nスクリプトを安全に終了しました。")
        sys.exit()

if __name__ == "__main__":
    main_loop()