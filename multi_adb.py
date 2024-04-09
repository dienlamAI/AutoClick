import subprocess
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import time
import keyboard
import pygetwindow as gw
import threading

class ADBAutomator:
    def __init__(self, tab, device_id):
        self.root = root
        self.device_id = device_id  
        self.action_thread = None
        self.positions = []
        self.running = False
        self.wait_input_ok_clicked = False
        self.setup_ui(tab)
    def adb_command(self, command):
        full_cmd = f"adb -s {self.device_id} {command}"
        subprocess.run(full_cmd, shell=True)

    def adb_click(self, x, y):
        self.adb_command(f"shell input tap {x} {y}")

    def adb_drag(self, x1, y1, x2, y2, duration):
        self.adb_command(f"shell input swipe {x1} {y1} {x2} {y2} {duration}")

    def get_active_window_title(self):
        try:
            return gw.getActiveWindow().title
        except Exception:
            return None

    def add_click_position(self):
        try:
            x = float(self.x_entry.get())
            y = float(self.y_entry.get())
            self.positions.append(('click', (x, y)))
            self.update_position_listbox()
            self.x_entry.delete(0, tk.END)
            self.y_entry.delete(0, tk.END)
        except ValueError:
            messagebox.showinfo("Lỗi", "Vui lòng nhập số hợp lệ cho tọa độ.")

    def add_drag_position(self):
        x1 = float(self.x1_entry.get())
        y1 = float(self.y1_entry.get())
        x2 = float(self.x2_entry.get())
        y2 = float(self.y2_entry.get())
        if x1 == '' or y1 == '' or x2 == '' or y2 == '':
            messagebox.showinfo("Lỗi", "Vui lòng nhập số hợp lệ cho tọa độ.")
        else:
            self.positions.append(('drag', ((x1,y1), (x2, y2))))
            self.update_position_listbox()
            self.x1_entry.delete(0, tk.END)
            self.y1_entry.delete(0, tk.END)
            self.x2_entry.delete(0, tk.END)
            self.y2_entry.delete(0, tk.END)
            

    def add_wait_for_input(self):
        self.positions.append(('wait_input', None))
        self.update_position_listbox()

    def add_wait_time_directly(self):
        try:
            wait_time = float(self.wait_time_entry.get())
            if wait_time > 0:
                self.positions.append(('wait', wait_time))
                self.update_position_listbox()
                self.wait_time_entry.delete(0, tk.END)  
        except ValueError:
            print("Vui lòng nhập một số hợp lệ.")

    def update_position_listbox(self):
        self.position_listbox.delete(0, tk.END)
        for action, value in self.positions:
            if action == 'click':
                self.position_listbox.insert(tk.END, f"click: {value}")
            elif action == 'wait':
                self.position_listbox.insert(tk.END, f"wait: {value}")
            elif action == 'drag':
                start_pos, end_pos = value
                self.position_listbox.insert(tk.END, f"drag: ({start_pos}, {end_pos})")
            elif action == 'wait_input':
                self.position_listbox.insert(tk.END, f"wait_input")
        self.position_listbox.yview(tk.END)
    def delete_selected_position(self):
        selected = self.position_listbox.curselection()
        if selected:
            self.positions.pop(selected[0])
            self.update_position_listbox()
    def delete_all_start(self):
        self.start_listbox.delete(0, tk.END)
    def delete_all(self):
        self.positions.clear()  
        self.update_position_listbox()  
    def auto_close_messagebox(self,title,message,  timeout=5000):
        threading.Thread(target=lambda: messagebox.showinfo(title, message)).start()

    def save_positions_to_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, 'w') as file:
                for action, value in self.positions:
                    file.write(f"{action}: {value}\n")
            print(f"Lưu thành công vào {file_path}")
    def wait_input_button_clicked(self):
        global wait_input_ok_clicked
        self.wait_input_ok_clicked = True

    def perform_actions(self):
        global running, wait_input_ok_clicked
        running = True
        keyboard.add_hotkey('z', lambda: self.stop_actions())
        self.delete_all_start()
        if self.wait_run_entry.get() == '':
            messagebox.showerror('Lỗi','Thời gian chờ giữa các hành động không được rỗng')
        else:
            action_count = 0
            for action, value in self.positions:
                action_count +=1
                if not running:
                    break
                time.sleep(float(self.wait_run_entry.get())) 
                if action == 'click':
                    x,y = value

                    self.adb_click(x,y)
                    time.sleep(1)
                    self.start_listbox.insert(tk.END, f"{action_count} Đã click {value}")
                    self.start_listbox.yview(tk.END)
                    # self.root.update()
                elif action == 'wait':
                    for i in range(int(value)):
                        self.start_listbox.insert(tk.END, f"{action_count} Bắt đầu chờ {i+1}/{value} giây")
                        self.start_listbox.yview(tk.END)
                        # self.root.update()
                        time.sleep(1)
                        self.start_listbox.delete(self.start_listbox.size() - 1)
                        # self.root.update()
                    self.start_listbox.insert(tk.END, f"{action_count} Chờ xong {value}/{value} giây")
                    self.start_listbox.yview(tk.END)
                    # self.root.update()
                elif action == 'wait_input':
                    self.wait_input_button_ok.config(state=tk.NORMAL)
                    self.start_listbox.insert(tk.END, f"{action_count} Đợi nhập...")
                    # auto_close_messagebox('Nhập đê','Xác nhận dùm cái',5000)
                    self.start_listbox.yview(tk.END)
                    # self.root.update()
                    while not self.wait_input_ok_clicked:
                        # self.root.update()
                        time.sleep(0.1)  
                    self.wait_input_button_ok.config(state=tk.DISABLED)
                    self.wait_input_ok_clicked = False
                elif action == 'drag':
                    x,y = value
                    x1,y1 = x
                    x2,y2 = y
                    self.adb_drag(x1,y1,x2,y2,500)
                    time.sleep(0.2)
                    self.start_listbox.insert(tk.END, f"{action_count} Đã kéo từ {x} đến {y}")
                    self.start_listbox.yview(tk.END)
                    # self.root.update()
            self.start_listbox.insert(tk.END, "Hoàn thành tất cả các hành động.")
            self.start_listbox.yview(tk.END)
            # self.root.update()
            keyboard.remove_hotkey('z')


    def import_positions_from_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, 'r') as file:
                for line in file:
                    action, value = line.strip().split(': ')
                    if action == 'click':
                        x, y = map(float, value.strip("()").split(', '))
                        self.positions.append((action, (x, y)))
                    elif action == 'wait':
                        self.positions.append((action, float(value)))
                    elif action == 'wait_input':
                        self.positions.append((action, None))
                    elif action == 'drag':
                        start_value, end_value = value.split('), (')
                        start_x, start_y = map(float, start_value.strip("()").split(', '))
                        end_x, end_y = map(float, end_value.strip("()").split(', '))
                        self.positions.append((action, ((start_x, start_y), (end_x, end_y))))
            self.update_position_listbox()
    def start_actions(self):
        if self.action_thread is None or not self.action_thread.is_alive():
            self.action_thread = threading.Thread(target=self.perform_actions)
            self.action_thread.start()
    def stop_actions(self):
        self.running = False
        if self.action_thread is not None:
            self.action_thread.join()
        keyboard.remove_hotkey('z')
    def setup_ui(self, tab):
        self.root = tab 

        coordinate_frame = tk.Frame(self.root)
        coordinate_frame.pack()
        coordinate_label = tk.Label(coordinate_frame, text='Nhập Click: ')
        coordinate_label.pack(side=tk.LEFT)
        self.x_entry = tk.Entry(coordinate_frame, width=5)
        self.x_entry.pack(side=tk.LEFT)
        self.y_entry = tk.Entry(coordinate_frame, width=5)
        self.y_entry.pack(side=tk.LEFT)
        add_coordinate_button = tk.Button(coordinate_frame, text="Thêm", command=self.add_click_position)
        add_coordinate_button.pack(side=tk.LEFT)

        drag_frame = tk.Frame(self.root)
        drag_frame.pack()
        drag_label = tk.Label(drag_frame, text='Nhập drag: ')
        drag_label.pack(side=tk.LEFT)
        self.x1_entry = tk.Entry(drag_frame, width=5)
        self.x1_entry.pack(side=tk.LEFT)
        self.y1_entry = tk.Entry(drag_frame, width=5)
        self.y1_entry.pack(side=tk.LEFT)
        self.x2_entry = tk.Entry(drag_frame, width=5)
        self.x2_entry.pack(side=tk.LEFT)
        self.y2_entry = tk.Entry(drag_frame, width=5)
        self.y2_entry.pack(side=tk.LEFT)
        add_drag_button = tk.Button(drag_frame, text="Thêm", command=self.add_drag_position)
        add_drag_button.pack(side=tk.LEFT)

        wait_run_frame = tk.Frame(self.root)
        wait_run_frame.pack()
        self.wait_run_label = tk.Label(wait_run_frame, text='Thời gian chờ giữa các hành động: ')
        self.wait_run_label.pack(side=tk.LEFT)
        self.wait_run_entry = tk.Entry(wait_run_frame, width=5)
        self.wait_run_entry.pack(side=tk.LEFT)
        self.wait_run_entry.insert(0, '2')


        wait_time_frame = tk.Frame(self.root)
        wait_time_frame.pack()
        self.wait_time_label = tk.Label(wait_time_frame, text='Thời gian chờ: ')
        self.wait_time_label.pack(side=tk.LEFT)
        self.wait_time_entry = tk.Entry(wait_time_frame, width=5)
        self.wait_time_entry.pack(side=tk.LEFT)
        self.add_wait_button = tk.Button(wait_time_frame, text="Thêm", command=self.add_wait_time_directly)
        self.add_wait_button.pack(side=tk.LEFT)

        wait_input_frame = tk.Frame(self.root)
        wait_input_frame.pack()
        self.wait_input_button = tk.Button(wait_input_frame, text="Muốn chờ nhập", command=self.add_wait_for_input)
        self.wait_input_button.pack(side=tk.LEFT)
        self.wait_input_button_ok = tk.Button(wait_input_frame, text="Nhập xong",command=self.wait_input_button_clicked, state=tk.DISABLED)
        self.wait_input_button_ok.pack(side=tk.LEFT)

        delete_frame = tk.Frame(self.root)
        delete_frame.pack()
        self.delete_button = tk.Button(delete_frame, text="Xóa hành động", command=self.delete_selected_position)
        self.delete_button.pack(side=tk.LEFT)

        self.delete_button_all = tk.Button(delete_frame, text="Xóa tất cả", command=self.delete_all)
        self.delete_button_all.pack(side=tk.LEFT)

        position_listbox_frame = tk.Frame(self.root)
        position_listbox_frame.pack()
        self.position_listbox = tk.Listbox(position_listbox_frame,width=40)
        self.position_listbox.pack()

        start_end_frame = tk.Frame(self.root)
        start_end_frame.pack()
        self.start = tk.Button(start_end_frame, text='Bắt đầu', command=self.start_actions)
        self.start.pack(side=tk.LEFT)
        self.stop_label = tk.Label(start_end_frame,text='Bấm "z" để dừng chạy')
        self.stop_label.pack(side=tk.LEFT)
        self.del_all_btn = tk.Button(start_end_frame,text='Xóa tất cả',command=self.delete_all_start)
        self.del_all_btn.pack(side=tk.LEFT)
        self.start_listbox = tk.Listbox(self.root,width=40)
        self.start_listbox.pack()

        save_button = tk.Button(self.root, text="Lưu Click", command=self.save_positions_to_file)
        save_button.pack()
        import_button = tk.Button(self.root, text="Nhập Click", command=self.import_positions_from_file)
        import_button.pack()

def get_connected_devices():
    result = subprocess.run(["adb", "devices"], stdout=subprocess.PIPE)
    devices_output = result.stdout.decode()
 
    lines = devices_output.split('\n')
    device_ids = []
    for line in lines[1:]:  
        if line.strip():  
            device_id = line.split('\t')[0]
            device_ids.append(device_id)

    return device_ids

root = tk.Tk()
root.title('multiadb')
root.attributes('-topmost', True)
device_ids = get_connected_devices() 
tab_control = ttk.Notebook(root)
automators = []

for device_id in device_ids:
    tab = ttk.Frame(tab_control)
    tab_control.add(tab, text=device_id)
    automator = ADBAutomator(tab, device_id)
    automators.append(automator)

tab_control.pack(expand=1, fill="both")

root.mainloop()