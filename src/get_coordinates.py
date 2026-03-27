
from pynput import mouse

print("1. iPhoneミラーリング画面の【左上】をクリックしてください。")
click_count = 0
coords = []

def on_click(x, y, button, pressed):
    global click_count
    if pressed:
        coords.append((int(x), int(y)))
        click_count += 1
        if click_count == 1:
            print(f"左上座標を取得しました: ({int(x)}, {int(y)})")
            print("2. 続いて、画面の【右下】をクリックしてください。")
        elif click_count == 2:
            print(f"右下座標を取得しました: ({int(x)}, {int(y)})")
            
            x1, y1 = coords[0]
            x2, y2 = coords[1]
            width = x2 - x1
            height = y2 - y1
            
            print("\n=== メインスクリプトに設定する値 ===")
            print(f"REGION = ({x1}, {y1}, {width}, {height})")
            print("====================================")
            return False # リスナーを終了

# マウスクリックを監視
with mouse.Listener(on_click=on_click) as listener:
    listener.join()