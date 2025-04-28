import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import threading
import time

# Global variables
timer_running = False
timer_thread = None
remaining_time = 0
current_task = None
task_timers = {}

# Theme
current_theme = "light"
button_normal_color = "#E0E0E0"
button_hover_color = "#D6D6D6"
dark_bg = "#2E2E2E"
dark_fg = "#FFFFFF"
light_bg = "#FFFFFF"
light_fg = "#000000"

def on_enter(e):
    e.widget.config(bg=button_hover_color)

def on_leave(e):
    e.widget.config(bg=button_normal_color)

def add_task():
    task = task_entry.get()
    if task != "" and task != "Type a new task...":
        if task_listbox.get(0) == "No tasks yet 🌸":
            task_listbox.delete(0)  # remove the placeholder
        task_number = task_listbox.size() + 1
        task_listbox.insert(tk.END, f"{task_number}. {task}")
        task_entry.delete(0, tk.END)
        task_entry.insert(0, 'Type a new task...')
        task_entry.config(foreground='grey')
        task_timers[f"{task_number}. {task}"] = {"timer": 0, "running": False}
    else:
        messagebox.showwarning("Input Error", "Please enter a task!")

def delete_task():
    try:
        task_index = task_listbox.curselection()[0]
        task = task_listbox.get(task_index)
        task_listbox.delete(task_index)
        del task_timers[task]
        
        # If no tasks left, show placeholder
        if task_listbox.size() == 0:
            task_listbox.insert(tk.END, "No tasks yet 🌸")
    except IndexError:
        messagebox.showwarning("Selection Error", "Please select a task to delete!")

def edit_task():
    try:
        task_index = task_listbox.curselection()[0]
        current_task = task_listbox.get(task_index)
        
        # Extract the number part (before the first ". ")
        number, old_task_text = current_task.split(". ", 1)
        
        # Ask user for new task description
        new_task_text = simpledialog.askstring("Edit Task", "Edit your task:", initialvalue=old_task_text)
        
        if new_task_text:  # If user didn't cancel
            new_full_task = f"{number}. {new_task_text}"
            task_listbox.delete(task_index)
            task_listbox.insert(task_index, new_full_task)
            
            # Update task_timers dictionary
            del task_timers[current_task]
            task_timers[new_full_task] = {"timer": 0, "running": False}
    except IndexError:
        messagebox.showwarning("Selection Error", "Please select a task to edit!")

def start_timer():
    global current_task
    try:
        task_index = task_listbox.curselection()[0]
        task = task_listbox.get(task_index)
        current_task = task
        hours = int(hours_entry.get())
        minutes = int(minutes_entry.get())
        seconds = int(seconds_entry.get())
        
        total_time = hours * 3600 + minutes * 60 + seconds
        task_timers[task] = {"timer": total_time, "running": True}
        
        global timer_thread, timer_running
        if not timer_running:
            timer_running = True
            timer_thread = threading.Thread(target=run_timer, args=(task,))
            timer_thread.start()
    except ValueError:
        messagebox.showwarning("Input Error", "Please enter valid hours, minutes, and seconds!")

def run_timer(task):
    global timer_running
    while task_timers[task]["timer"] > 0 and task_timers[task]["running"]:
        time.sleep(1)
        task_timers[task]["timer"] -= 1
        update_timer_label(task)
    task_timers[task]["running"] = False
    timer_running = False
    if task_timers[task]["timer"] == 0:
        update_timer_label(task)
        messagebox.showinfo("Timer Finished", f"Time for task '{task}' is up!")

def update_timer_label(task):
    remaining = task_timers[task]["timer"]
    hours = remaining // 3600
    minutes = (remaining % 3600) // 60
    seconds = remaining % 60
    time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    timer_label.config(text=f"Time left for '{task}': {time_str}")

def pause_timer():
    try:
        task_index = task_listbox.curselection()[0]
        task = task_listbox.get(task_index)
        task_timers[task]["running"] = False
    except IndexError:
        messagebox.showwarning("Selection Error", "Please select a task to pause!")

def stop_timer():
    try:
        task_index = task_listbox.curselection()[0]
        task = task_listbox.get(task_index)
        task_timers[task]["running"] = False
        task_timers[task]["timer"] = 0
        update_timer_label(task)
    except IndexError:
        messagebox.showwarning("Selection Error", "Please select a task to stop!")

def resume_timer():
    global timer_thread, timer_running
    try:
        task_index = task_listbox.curselection()[0]
        task = task_listbox.get(task_index)
        if not task_timers[task]["running"]:
            task_timers[task]["running"] = True
            if not timer_running:
                timer_thread = threading.Thread(target=run_timer, args=(task,))
                timer_thread.start()
    except IndexError:
        messagebox.showwarning("Selection Error", "Please select a task to resume!")

def save_tasks():
    file_name = simpledialog.askstring("Save File", "Enter file name (without extension):")
    if file_name:
        if not file_name.endswith(".txt"):
            file_name += ".txt"
        try:
            with open(file_name, "w") as file:
                for task in task_listbox.get(0, tk.END):
                    file.write(task + "\n")
            messagebox.showinfo("Saved", f"Tasks saved to {file_name}")
        except Exception as e:
            messagebox.showerror("Error", f"Error saving file: {str(e)}")

def load_tasks():
    file_name = filedialog.askopenfilename(title="Open File", filetypes=[("Text Files", "*.txt")])
    if file_name:
        try:
            task_listbox.delete(0, tk.END)
            task_timers.clear()
            with open(file_name, "r") as file:
                tasks = file.readlines()
                for task in tasks:
                    task = task.strip()
                    task_listbox.insert(tk.END, task)
                    task_timers[task] = {"timer": 0, "running": False}
            messagebox.showinfo("Loaded", f"Tasks loaded from {file_name}")
        except Exception as e:
            messagebox.showerror("Error", f"Error loading file: {str(e)}")

# === GUI DESIGN ===
root = tk.Tk()
root.title("📝 Python To-Do List App with Timer")
root.geometry("600x700")
title_label = tk.Label(root, text="⏳✨   t o o d l e s   🌸⏳", font=("Montserrat", 24, "bold"))
title_label.pack(pady=(20, 10))
root.configure(bg="#f0f0f0")

style = ttk.Style()
style.theme_use("clam")
style.configure("TButton", font=("Segoe UI", 10), padding=5)
style.configure("TLabel", font=("Segoe UI", 11))
style.configure("TEntry", font=("Segoe UI", 11))

# Save/Load Section
file_frame = ttk.LabelFrame(root, text="File Management", padding=(20, 10))
file_frame.pack(padx=20, pady=10, fill="both")

# Use grid for file_frame to center the buttons
file_frame.grid_columnconfigure(0, weight=1)  # To make sure both columns expand
file_frame.grid_columnconfigure(1, weight=1)  # To make both columns take equal space
file_frame.grid_rowconfigure(0, weight=1)     # To center the content vertically

save_button = ttk.Button(file_frame, text="Save Tasks 💾", command=save_tasks)
save_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

load_button = ttk.Button(file_frame, text="Load Tasks 📂", command=load_tasks)
load_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

# Task Section
task_frame = ttk.LabelFrame(root, text="Tasks", padding=(20, 10))
task_frame.pack(padx=20, pady=10, fill="both")

# Create a Frame to hold both the Listbox and Scrollbar
task_list_frame = ttk.Frame(task_frame)
task_list_frame.pack(padx=5, pady=10, fill="both", expand=True)

# Create Listbox
task_listbox = tk.Listbox(task_list_frame, height=4, font=("Segoe UI", 11), selectborderwidth=5)
task_listbox.pack(side="left", fill="both", expand=True)

# Create Scrollbar
scrollbar = ttk.Scrollbar(task_list_frame, orient="vertical", command=task_listbox.yview)
scrollbar.pack(side="right", fill="y")

# Connect Scrollbar to Listbox
task_listbox.config(yscrollcommand=scrollbar.set)

task_entry = ttk.Entry(task_frame, width=40)
task_entry.pack(padx=10, pady=(0,10))

# Placeholder for task_entry
def on_entry_click(event):
    if task_entry.get() == 'Type a new task...':
        task_entry.delete(0, "end")  # delete all the text
        task_entry.config(foreground='black')

def on_focusout(event):
    if task_entry.get() == '':
        task_entry.insert(0, 'Type a new task...')
        task_entry.config(foreground='grey')

task_entry.insert(0, 'Type a new task...')
task_entry.config(foreground='grey')
task_entry.bind('<FocusIn>', on_entry_click)
task_entry.bind('<FocusOut>', on_focusout)

btn_frame = ttk.Frame(task_frame)
btn_frame.pack(pady=5)

add_button = ttk.Button(btn_frame, text="Add +", command=add_task)
add_button.grid(row=0, column=0, padx=5)

edit_button = ttk.Button(btn_frame, text="Edit ✏️", command=edit_task)
edit_button.grid(row=0, column=1, padx=5)

delete_button = ttk.Button(btn_frame, text="Delete 🗑️", command=delete_task)
delete_button.grid(row=0, column=2, padx=5)

# Timer Section
timer_frame = ttk.LabelFrame(root, text="Timer Controls", padding=(20, 10))
timer_frame.pack(padx=20, pady=10, fill="both")

timer_set_frame = ttk.Frame(timer_frame)
timer_set_frame.pack(pady=10)

# Hour Entry and Label
hours_entry = ttk.Entry(timer_set_frame, width=5, justify="center")
hours_entry.insert(0, "00")
hours_entry.grid(row=0, column=0, padx=5)

hours_label = ttk.Label(timer_set_frame, text="hh", font=("Segoe UI", 10))
hours_label.grid(row=0, column=1, padx=(0, 5))

# Minute Entry and Label
minutes_entry = ttk.Entry(timer_set_frame, width=5, justify="center")
minutes_entry.insert(0, "00")
minutes_entry.grid(row=0, column=2, padx=5)

minutes_label = ttk.Label(timer_set_frame, text="mm", font=("Segoe UI", 10))
minutes_label.grid(row=0, column=3, padx=(0, 5))

# Second Entry and Label
seconds_entry = ttk.Entry(timer_set_frame, width=5, justify="center")
seconds_entry.insert(0, "00")
seconds_entry.grid(row=0, column=4, padx=5)

seconds_label = ttk.Label(timer_set_frame, text="ss", font=("Segoe UI", 10))
seconds_label.grid(row=0, column=5, padx=(0, 5))

timer_btn_frame = ttk.Frame(timer_frame)
timer_btn_frame.pack(pady=10)

start_button = ttk.Button(timer_btn_frame, text="Start ⏳", command=start_timer)
start_button.grid(row=0, column=0, padx=5)

pause_button = ttk.Button(timer_btn_frame, text="Pause ⏸️", command=pause_timer)
pause_button.grid(row=0, column=1, padx=5)

stop_button = ttk.Button(timer_btn_frame, text="Stop ⏹️", command=stop_timer)
stop_button.grid(row=0, column=2, padx=5)

resume_button = ttk.Button(timer_btn_frame, text="Resume ▶️", command=resume_timer)
resume_button.grid(row=0, column=3, padx=5)

timer_label = ttk.Label(timer_frame, text="Time left: 00:00:00", font=("Segoe UI", 32, "bold"))
timer_label.pack(pady=10)

root.mainloop()
