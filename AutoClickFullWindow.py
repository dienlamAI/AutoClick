import tkinter as tk
from pynput import mouse
import time
from pynput.mouse import Controller, Button
import keyboard
from tkinter import filedialog
from tkinter import messagebox
import pygetwindow as gw

mouse_controller = Controller()
drag_start_pos = None
drag_in_progress = False
mouse_listener = None
wait_input_ok_clicked = False
positions = []
adding_mode = False

def is_click_inside_tkinter_window(x, y):
    window_x1 = root.winfo_rootx()
    window_y1 = root.winfo_rooty()
    window_x2 = window_x1 + root.winfo_width()
    window_y2 = window_y1 + root.winfo_height()
    return window_x1 <= x <= window_x2 and window_y1 <= y <= window_y2

def on_move(x, y):
    global drag_start_pos, drag_in_progress
    if drag_start_pos and not drag_in_progress:
        dx, dy = abs(x - drag_start_pos[0]), abs(y - drag_start_pos[1])
        if dx + dy > 10:
            print(f"Kéo di chuyển: ({x}, {y})")
            drag_in_progress = True
def get_active_window_title():
    try:
        return gw.getActiveWindow().title
    except Exception:
        return None
def on_click(x, y, button, pressed):
    global drag_start_pos, drag_in_progress
    if adding_mode and not is_click_inside_tkinter_window(x, y):
        if pressed:
            drag_start_pos = (x, y)
            drag_in_progress = False
        else:
            if drag_start_pos and drag_in_progress:
                positions.append(('drag', (drag_start_pos, (x, y))))
                update_position_listbox()
            elif drag_start_pos:
                positions.append(('click', drag_start_pos))
                update_position_listbox()
            drag_start_pos = None
            drag_in_progress = False

def toggle_adding_mode():
    global adding_mode, mouse_listener
    adding_mode = not adding_mode
    if adding_mode:
        add_click_button.config(text="Dừng Thêm", bg='red')
        if mouse_listener is None or not mouse_listener.running:
            mouse_listener = mouse.Listener(on_click=on_click, on_move=on_move)
            mouse_listener.start()
        # Vô hiệu hóa các nút khác
        add_wait_button.config(state=tk.DISABLED)
        delete_button.config(state=tk.DISABLED)
        delete_button_all.config(state=tk.DISABLED)
        wait_time_entry.config(state=tk.DISABLED)
        start.config(state=tk.DISABLED)
    else:
        add_click_button.config(text="Thêm Click",bg='#EEEEEE')
        # Kích hoạt lại các nút
        add_wait_button.config(state=tk.NORMAL)
        delete_button.config(state=tk.NORMAL)
        delete_button_all.config(state=tk.NORMAL)
        wait_time_entry.config(state=tk.NORMAL)
        start.config(state=tk.NORMAL)

def add_wait_for_input():
    positions.append(('wait_input', None))
    update_position_listbox()

def add_wait_time_directly():
    try:
        wait_time = float(wait_time_entry.get())
        if wait_time > 0:
            positions.append(('wait', wait_time))
            update_position_listbox()
            wait_time_entry.delete(0, tk.END)  
    except ValueError:
        print("Vui lòng nhập một số hợp lệ.")

def update_position_listbox():
    position_listbox.delete(0, tk.END)
    for action, value in positions:
        if action == 'click':
            position_listbox.insert(tk.END, f"click: {value}")
        elif action == 'wait':
            position_listbox.insert(tk.END, f"wait: {value}")
        elif action == 'drag':
            start_pos, end_pos = value
            position_listbox.insert(tk.END, f"drag: ({start_pos}, {end_pos})")
        elif action == 'wait_input':
            position_listbox.insert(tk.END, f"wait_input")
    position_listbox.yview(tk.END)
def delete_selected_position():
    selected = position_listbox.curselection()
    if selected:
        positions.pop(selected[0])
        update_position_listbox()
def delete_all_start():
    start_listbox.delete(0, tk.END)
def delete_all():
    positions.clear()  
    update_position_listbox()  
def save_positions_to_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                             filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    if file_path:
        with open(file_path, 'w') as file:
            for action, value in positions:
                file.write(f"{action}: {value}\n")
        print(f"Lưu thành công vào {file_path}")
def wait_input_button_clicked():
    global wait_input_ok_clicked
    wait_input_ok_clicked = True

def perform_actions():
    global running, wait_input_ok_clicked
    if wait_run_entry.get() == '':
        messagebox.showerror('Lỗi','Thời gian chờ giữa các hành động không được rỗng')
    elif vong_lap_entry.get() == '':
        messagebox.showerror('Lỗi','Vòng lặp không được rỗng')
    else:
        for i in range(int(vong_lap_entry.get())):
            running = True
            keyboard.add_hotkey('z', lambda: stop_actions())
            for action, value in positions:
                if not running:
                    break
                time.sleep(float(wait_run_entry.get())) 
                if action == 'click':
                    mouse_controller.position = value 
                    mouse_controller.click(Button.left, 1)  
                    time.sleep(1)
                    start_listbox.insert(tk.END, f"Đã click {value}")
                    start_listbox.yview(tk.END)
                    root.update()
                elif action == 'wait':
                    for i in range(int(value)):
                        start_listbox.insert(tk.END, f"Bắt đầu chờ {i+1}/{value} giây")
                        start_listbox.yview(tk.END)
                        root.update()
                        time.sleep(1)
                        start_listbox.delete(start_listbox.size() - 1)
                        root.update()
                    start_listbox.insert(tk.END, f"Chờ xong {value}/{value} giây")
                    start_listbox.yview(tk.END)
                    root.update()
                elif action == 'wait_input':
                    wait_input_button_ok.config(state=tk.NORMAL)
                    start_listbox.insert(tk.END, "Đợi nhập...")
                    start_listbox.yview(tk.END)
                    root.update()
                    while not wait_input_ok_clicked:
                        root.update()
                        time.sleep(0.1)  
                    wait_input_button_ok.config(state=tk.DISABLED)
                    wait_input_ok_clicked = False
                elif action == 'drag':
                    start_pos, end_pos = value
                    mouse_controller.position = start_pos  
                    mouse_controller.press(Button.left)
                    time.sleep(0.2) 

                    steps = 20  
                    dx = (end_pos[0] - start_pos[0]) / steps
                    dy = (end_pos[1] - start_pos[1]) / steps

                    for _ in range(steps):
                        new_x, new_y = mouse_controller.position[0] + dx, mouse_controller.position[1] + dy
                        mouse_controller.position = (new_x, new_y)
                        time.sleep(0.01) 

                    mouse_controller.release(Button.left) 
                    time.sleep(0.2)
                    start_listbox.insert(tk.END, f"Đã kéo từ {start_pos} đến {end_pos}")
                    start_listbox.yview(tk.END)
                    root.update()
            start_listbox.insert(tk.END, "Hoàn thành tất cả các hành động.")
            start_listbox.yview(tk.END)
            root.update()
            keyboard.remove_hotkey('z')


def import_positions_from_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    if file_path:
        with open(file_path, 'r') as file:
            for line in file:
                action, value = line.strip().split(': ')
                if action == 'click':
                    x, y = map(int, value.strip("()").split(', '))
                    positions.append((action, (x, y)))
                elif action == 'wait':
                    positions.append((action, float(value)))
                elif action == 'wait_input':
                    positions.append((action, None))
                elif action == 'drag':
                    start_value, end_value = value.split('), (')
                    start_x, start_y = map(int, start_value.strip("()").split(', '))
                    end_x, end_y = map(int, end_value.strip("()").split(', '))
                    positions.append((action, ((start_x, start_y), (end_x, end_y))))
        update_position_listbox()

def stop_actions():
    global running
    running = False

def start_move1(event):
    root.x = event.x
    root.y = event.y

def on_move1(event):
    deltax = event.x - root.x
    deltay = event.y - root.y
    x = root.winfo_x() + deltax
    y = root.winfo_y() + deltay
    root.geometry(f"+{x}+{y}")

root = tk.Tk()
root.title("Quản lý Hành Động Chuột")

root.attributes('-topmost', True)


add_click_button = tk.Button(root, text="Thêm Click", command=toggle_adding_mode)
add_click_button.pack()

wait_run_frame = tk.Frame(root)
wait_run_frame.pack()
wait_run_label = tk.Label(wait_run_frame, text='Thời gian chờ  giữa các hành động: ')
wait_run_label.pack(side=tk.LEFT)
wait_run_entry = tk.Entry(wait_run_frame, width=5)
wait_run_entry.pack(side=tk.LEFT)


wait_time_frame = tk.Frame(root)
wait_time_frame.pack()
wait_time_label = tk.Label(wait_time_frame, text='Thời gian chờ: ')
wait_time_label.pack(side=tk.LEFT)
wait_time_entry = tk.Entry(wait_time_frame, width=5)
wait_time_entry.pack(side=tk.LEFT)
add_wait_button = tk.Button(wait_time_frame, text="Thêm", command=add_wait_time_directly)
add_wait_button.pack(side=tk.LEFT)

vong_lap_frame = tk.Frame(root)
vong_lap_frame.pack()
vong_lap_label = tk.Label(vong_lap_frame, text='Vòng lặp: ')
vong_lap_label.pack(side=tk.LEFT)
vong_lap_entry = tk.Entry(vong_lap_frame, width=5)
vong_lap_entry.pack(side=tk.LEFT)

wait_input_frame = tk.Frame(root)
wait_input_frame.pack()
wait_input_button = tk.Button(wait_input_frame, text="Muốn chờ nhập", command=add_wait_for_input)
wait_input_button.pack(side=tk.LEFT)
wait_input_button_ok = tk.Button(wait_input_frame, text="Nhập xong",command=wait_input_button_clicked, state=tk.DISABLED)
wait_input_button_ok.pack(side=tk.LEFT)

delete_frame = tk.Frame(root)
delete_frame.pack()
delete_button = tk.Button(delete_frame, text="Xóa hành động", command=delete_selected_position)
delete_button.pack(side=tk.LEFT)

delete_button_all = tk.Button(delete_frame, text="Xóa tất cả", command=delete_all)
delete_button_all.pack(side=tk.LEFT)

position_listbox_frame = tk.Frame(root)
position_listbox_frame.pack()
position_listbox = tk.Listbox(position_listbox_frame,width=40)
position_listbox.pack()

start_end_frame = tk.Frame(root)
start_end_frame.pack()
start = tk.Button(start_end_frame,text='Bắt đầu', command=perform_actions)
start.pack(side=tk.LEFT)
stop_label = tk.Label(start_end_frame,text='Bấm "z" để dừng chạy')
stop_label.pack(side=tk.LEFT)
del_all_btn = tk.Button(start_end_frame,text='Xóa tất cả',command=delete_all_start)
del_all_btn.pack(side=tk.LEFT)
start_listbox = tk.Listbox(root,width=40)
start_listbox.pack()

save_button = tk.Button(root, text="Lưu Click", command=save_positions_to_file)
save_button.pack()
import_button = tk.Button(root, text="Nhập Click", command=import_positions_from_file)
import_button.pack()

mouse_listener = mouse.Listener(on_click=on_click, on_move=on_move)

root.bind("<Button-1>", start_move1)
root.bind("<B1-Motion>", on_move1)

root.mainloop()
