import tkinter as tk
from tkinter import filedialog, messagebox
import os
import schedule
import time
import threading
import subprocess


class PythonScriptScheduler:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Script Manager")
        self.root.geometry("500x400")

        self.scripts = []

        # Widgets
        self.script_listbox = tk.Listbox(self.root, width=60, height=15)
        self.script_listbox.pack(pady=10)

        self.add_script_button = tk.Button(self.root, text="Add Script", command=self.add_script)
        self.add_script_button.pack(pady=5)

        self.remove_script_button = tk.Button(self.root, text="Remove Selected", command=self.remove_script)
        self.remove_script_button.pack(pady=5)

        self.schedule_script_button = tk.Button(self.root, text="Schedule Selected", command=self.schedule_script)
        self.schedule_script_button.pack(pady=5)

        self.run_now_button = tk.Button(self.root, text="Run Selected Now", command=self.run_now)
        self.run_now_button.pack(pady=5)

        self.start_scheduler_button = tk.Button(self.root, text="Start Scheduler", command=self.start_scheduler)
        self.start_scheduler_button.pack(pady=10)

    def add_script(self):
        file_path = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
        if file_path:
            self.scripts.append(file_path)
            self.script_listbox.insert(tk.END, os.path.basename(file_path))

    def remove_script(self):
        selected = self.script_listbox.curselection()
        if selected:
            index = selected[0]
            self.script_listbox.delete(index)
            self.scripts.pop(index)
        else:
            messagebox.showwarning("Warning", "No script selected")

    def schedule_script(self):
        selected = self.script_listbox.curselection()
        if selected:
            index = selected[0]
            file_path = self.scripts[index]
            time_input = tk.simpledialog.askstring("Schedule Time", "Enter time (HH:MM 24hr format):")
            if time_input:
                try:
                    hour, minute = map(int, time_input.split(":"))
                    schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(self.run_script, file_path)
                    messagebox.showinfo("Success", f"Scheduled {os.path.basename(file_path)} at {time_input}")
                except ValueError:
                    messagebox.showerror("Error", "Invalid time format")
        else:
            messagebox.showwarning("Warning", "No script selected")

    def run_now(self):
        selected = self.script_listbox.curselection()
        if selected:
            index = selected[0]
            file_path = self.scripts[index]
            self.run_script(file_path)
        else:
            messagebox.showwarning("Warning", "No script selected")

    def run_script(self, file_path):
        try:
            subprocess.Popen(["python", file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            messagebox.showinfo("Success", f"Running {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to run script: {e}")

    def start_scheduler(self):
        def scheduler_thread():
            while True:
                schedule.run_pending()
                time.sleep(1)

        thread = threading.Thread(target=scheduler_thread, daemon=True)
        thread.start()
        messagebox.showinfo("Scheduler", "Scheduler started in the background")


# Main application
if __name__ == "__main__":
    root = tk.Tk()
    app = PythonScriptScheduler(root)
    root.mainloop()