# ファイル： src/mac_to_iphone_ocr_bot.py

import pyautogui
import time
import sys
from pathlib import Path

# パス修正: 2階層上（.parent.parent）がプロジェクトルート
BASE_DIR = Path(__file__).resolve().parent.parent
IMG_DIR = BASE_DIR / "images"

# --- 【追加項目】スクリーンショットを保存するフォルダ ---
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
            # 画像を探す
            pos = pyautogui.locateCenterOnScreen(img_path, confidence=CONFIDENCE)
            if pos:
                # =============================================================
                # 【Retinaディスプレイ対策】
                # もし画像は認識するのにクリック位置が画面の左上にずれる場合は、
                # 下の2行のコメントアウト(#)を外して、座標を半分にする必要があります。
                # print(f"  -> 画像発見 (Retina調整前座標): ({pos.x}, {pos.y})")
                # click_x, click_y = pos.x / 2, pos.y / 2
                # =============================================================
                
                # 通常（またはRetina調整済）の座標
                click_x, click_y = pos.x, pos.y
                
                # print(f"  -> クリック座標: ({click_x}, {click_y})")
                pyautogui.click(click_x, click_y)
                return True
                
        except pyautogui.ImageNotFoundException:
            pass # 見つからなかった場合は待機へ
        
        time.sleep(delay)
        
    return False

def check_mac_permissions():
    """画面収録の権限があるかどうかの簡易チェック"""
    print("システムの画面収録権限をチェックしています...")
    screenshot = pyautogui.screenshot()
    colors = screenshot.getcolors(maxcolors=1000)
    if colors and len(colors) == 1:
        print("【警告】画面が単色（真っ黒など）で取得されています。Macの「画面収録」権限が許可されていない可能性が高いです！")
    else:
        print(" -> 画面の取得は正常に行われているようです。\n")

def main_loop():
    print("=== 画像認識BOT 起動 ===")
    print(f"画像フォルダ: {IMG_DIR}")
    
    # --- 【追加項目】スクショフォルダの準備 ---
    print(f"スクショ保存フォルダ: {SCREENSHOT_DIR}")
    # フォルダが存在しない場合は作成する
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    
    check_mac_permissions()
    print("停止するにはターミナルで Ctrl+C を押してください。\n")
    
    try:
        while True:
            print("1. 「掘り出し物を見る」(horidashi.png) を探しています...")
            if click_image("horidashi.png", retries=3):
                # ★修正ポイント：タップ直後の処理
                print(" -> タップしました。画面遷移を待ちます。(1秒)")
                
                # 元の遷移待ち時間（2秒）を分割し、その間でスクショを撮る
                time.sleep(1) # まず1秒待つ（タップ後の反応時間）

                # --- 【追加項目】スクリーンショット撮影と保存 ---
                print(" -> [追加機能] 画面遷移後のスクリーンショットを撮影します...")
                # タイムスタンプを含む一意のファイル名を生成 (例: sc_20231027_153045.png)
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"sc_{timestamp}.png"
                save_path = SCREENSHOT_DIR / filename
                
                # 画面全体を撮影して指定パスに保存
                screenshot = pyautogui.screenshot()
                screenshot.save(save_path)
                print(f" -> 画面を保存しました: {filename}")
                # ---------------------------------------------

                time.sleep(1) # さらに1秒待つ（合計2秒の遷移待ちを維持）
                
                print("2. 商品（karusaito / sufe-n）を探しています...")
                if click_image("karusaito.png", retries=2) or click_image("sufe-n.png", retries=2):
                    print(" -> 対象商品を発見し、タップしました！")
                    time.sleep(1)
                    
                    print("3. 「はい」(yes.png) を探しています...")
                    if click_image("yes.png", retries=3):
                        print(" -> 購入処理を実行しました。")
                        time.sleep(3)
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