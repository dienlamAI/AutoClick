import subprocess
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import time
import keyboard
import pygetwindow as gw
import threading

drag_start_pos = None
drag_in_progress = False
wait_input_ok_clicked = False
positions = []
adding_mode = False


def adb_click(x, y):
    cmd = f"adb shell input tap {x} {y}"
    subprocess.run(cmd, shell=True)

def adb_drag(x1, y1, x2, y2, duration):
    cmd = f"adb shell input swipe {x1} {y1} {x2} {y2} {duration}"
    subprocess.run(cmd, shell=True)

def get_active_window_title():
    try:
        return gw.getActiveWindow().title
    except Exception:
        return None

def add_click_position():
    try:
        x = float(x_entry.get())
        y = float(y_entry.get())
        positions.append(('click', (x, y)))
        update_position_listbox()
        x_entry.delete(0, tk.END)
        y_entry.delete(0, tk.END)
    except ValueError:
        messagebox.showinfo("Lỗi", "Vui lòng nhập số hợp lệ cho tọa độ.")

def add_drag_position():
    x1 = float(x1_entry.get())
    y1 = float(y1_entry.get())
    x2 = float(x2_entry.get())
    y2 = float(y2_entry.get())
    if x1 == '' or y1 == '' or x2 == '' or y2 == '':
        messagebox.showinfo("Lỗi", "Vui lòng nhập số hợp lệ cho tọa độ.")
    else:
        positions.append(('drag', ((x1,y1), (x2, y2))))
        update_position_listbox()
        x1_entry.delete(0, tk.END)
        y1_entry.delete(0, tk.END)
        x2_entry.delete(0, tk.END)
        y2_entry.delete(0, tk.END)
        

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
def auto_close_messagebox(title,message,  timeout=5000):
    threading.Thread(target=lambda: messagebox.showinfo(title, message)).start()

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
    running = True
    keyboard.add_hotkey('z', lambda: stop_actions())
    delete_all_start()
    if wait_run_entry.get() == '':
        messagebox.showerror('Lỗi','Thời gian chờ giữa các hành động không được rỗng')
    else:
        action_count = 0
        for action, value in positions:
            action_count +=1
            if not running:
                break
            time.sleep(float(wait_run_entry.get())) 
            if action == 'click':
                x,y = value

                adb_click(x,y)
                time.sleep(1)
                start_listbox.insert(tk.END, f"{action_count} Đã click {value}")
                start_listbox.yview(tk.END)
                root.update()
            elif action == 'wait':
                for i in range(int(value)):
                    start_listbox.insert(tk.END, f"{action_count} Bắt đầu chờ {i+1}/{value} giây")
                    start_listbox.yview(tk.END)
                    root.update()
                    time.sleep(1)
                    start_listbox.delete(start_listbox.size() - 1)
                    root.update()
                start_listbox.insert(tk.END, f"{action_count} Chờ xong {value}/{value} giây")
                start_listbox.yview(tk.END)
                root.update()
            elif action == 'wait_input':
                wait_input_button_ok.config(state=tk.NORMAL)
                start_listbox.insert(tk.END, f"{action_count} Đợi nhập...")
                # auto_close_messagebox('Nhập đê','Xác nhận dùm cái',5000)
                start_listbox.yview(tk.END)
                root.update()
                while not wait_input_ok_clicked:
                    root.update()
                    time.sleep(0.1)  
                wait_input_button_ok.config(state=tk.DISABLED)
                wait_input_ok_clicked = False
            elif action == 'drag':
                x,y = value
                x1,y1 = x
                x2,y2 = y
                adb_drag(x1,y1,x2,y2,500)
                time.sleep(0.2)
                start_listbox.insert(tk.END, f"{action_count} Đã kéo từ {x} đến {y}")
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
                    x, y = map(float, value.strip("()").split(', '))
                    positions.append((action, (x, y)))
                elif action == 'wait':
                    positions.append((action, float(value)))
                elif action == 'wait_input':
                    positions.append((action, None))
                elif action == 'drag':
                    start_value, end_value = value.split('), (')
                    start_x, start_y = map(float, start_value.strip("()").split(', '))
                    end_x, end_y = map(float, end_value.strip("()").split(', '))
                    positions.append((action, ((start_x, start_y), (end_x, end_y))))
        update_position_listbox()

def stop_actions():
    global running
    running = False


root = tk.Tk()
root.title("adb")

root.attributes('-topmost', True)


coordinate_frame = tk.Frame(root)
coordinate_frame.pack()
coordinate_label = tk.Label(coordinate_frame, text='Nhập Click: ')
coordinate_label.pack(side=tk.LEFT)
x_entry = tk.Entry(coordinate_frame, width=5)
x_entry.pack(side=tk.LEFT)
y_entry = tk.Entry(coordinate_frame, width=5)
y_entry.pack(side=tk.LEFT)
add_coordinate_button = tk.Button(coordinate_frame, text="Thêm", command=add_click_position)
add_coordinate_button.pack(side=tk.LEFT)

drag_frame = tk.Frame(root)
drag_frame.pack()
drag_label = tk.Label(drag_frame, text='Nhập drag: ')
drag_label.pack(side=tk.LEFT)
x1_entry = tk.Entry(drag_frame, width=5)
x1_entry.pack(side=tk.LEFT)
y1_entry = tk.Entry(drag_frame, width=5)
y1_entry.pack(side=tk.LEFT)
x2_entry = tk.Entry(drag_frame, width=5)
x2_entry.pack(side=tk.LEFT)
y2_entry = tk.Entry(drag_frame, width=5)
y2_entry.pack(side=tk.LEFT)
add_drag_button = tk.Button(drag_frame, text="Thêm", command=add_drag_position)
add_drag_button.pack(side=tk.LEFT)

wait_run_frame = tk.Frame(root)
wait_run_frame.pack()
wait_run_label = tk.Label(wait_run_frame, text='Thời gian chờ giữa các hành động: ')
wait_run_label.pack(side=tk.LEFT)
wait_run_entry = tk.Entry(wait_run_frame, width=5)
wait_run_entry.pack(side=tk.LEFT)
wait_run_entry.insert(0, '2')


wait_time_frame = tk.Frame(root)
wait_time_frame.pack()
wait_time_label = tk.Label(wait_time_frame, text='Thời gian chờ: ')
wait_time_label.pack(side=tk.LEFT)
wait_time_entry = tk.Entry(wait_time_frame, width=5)
wait_time_entry.pack(side=tk.LEFT)
add_wait_button = tk.Button(wait_time_frame, text="Thêm", command=add_wait_time_directly)
add_wait_button.pack(side=tk.LEFT)

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
start = tk.Button(start_end_frame, text='Bắt đầu', command=lambda: threading.Thread(target=perform_actions).start())
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



root.mainloop()
