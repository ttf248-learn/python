import keyboard
import pyautogui
import time
import random

def simulate_process():
    # 模拟按鼠标右键
    keyboard.press_and_release('x')
    time.sleep(0.001)
    keyboard.press_and_release('x')
    time.sleep(0.001)
    keyboard.press_and_release('x')
    time.sleep(0.005)
    keyboard.press_and_release('x')
    time.sleep(0.005)
    keyboard.press_and_release('x')
    time.sleep(0.005)
    keyboard.press_and_release('x')
    time.sleep(0.005)
    pyautogui.click(button='right')
    time.sleep(0.005)
    keyboard.press_and_release('x')
    time.sleep(0.005)
    keyboard.press_and_release('x')
    time.sleep(0.005)
    keyboard.press_and_release('x')
    time.sleep(0.05)
    keyboard.press_and_release('x')
    time.sleep(0.05)
    keyboard.press_and_release('x')
    time.sleep(0.05)
    keyboard.press_and_release('x')
    time.sleep(0.05)

    # 模拟人工开蛋
    time.sleep(1)
    # 长按 'f' 键五秒钟
    keyboard.press('f')
    time.sleep(5)
    keyboard.release('f')
    time.sleep(0.5)

    # 模拟重新打开包裹界面
    keyboard.press_and_release('f')
    time.sleep(0.5)


def on_key_pressed(e):
    if e.name == 'n' and e.event_type == keyboard.KEY_DOWN:
        while True:
            # 获取并记住当前鼠标位置
            current_mouse_position = pyautogui.position()
            print(f"Current mouse position: {current_mouse_position}")
            
            # 执行模拟操作
            simulate_process()

            # 随机生成偏差
            # deviation_x = random.uniform(-1, 1)
            # deviation_y = random.uniform(-1, 1)

            deviation_x = 0
            deviation_y = 0

            # 鼠标移回原位置，加上随机偏差
            pyautogui.moveTo(current_mouse_position[0] + deviation_x, current_mouse_position[1] + deviation_y)
            time.sleep(0.5)

            # 随机休眠
            # sleep_time = random.uniform(1, 3)
            # print(f"Sleeping for {sleep_time} seconds...")
            # time.sleep(sleep_time)

            # return


# 注册 'n' 键的按下事件
keyboard.hook(on_key_pressed)

# 保持程序运行
keyboard.wait('esc')  # 等待按下 'esc' 键，可以替换为其他按键来结束程序
