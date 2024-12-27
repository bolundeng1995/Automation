import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, Toplevel, scrolledtext
from tkinter import ttk
from datetime import datetime
import os
import schedule
import time
import threading
import subprocess


class PythonScriptScheduler:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Script Scheduler")
        self.root.geometry("900x600")

        self.scripts = []  # List of scripts
        self.logs = []  # List of logs for executed scripts
        self.jobs = []  # List of jobs with details

        # GUI Components
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

        self.clear_jobs_button = tk.Button(self.root, text="Clear Scheduled Jobs", command=self.clear_scheduled_jobs)
        self.clear_jobs_button.pack(pady=5)

        # Scheduled Jobs Label
        self.scheduled_jobs_label = tk.Label(self.root, text="Scheduled Jobs:")
        self.scheduled_jobs_label.pack(pady=5)

        # Scheduled Jobs Treeview
        self.scheduled_jobs_tree = ttk.Treeview(self.root, columns=("File Name", "Time", "Location"), show="headings",
                                                height=10)
        self.scheduled_jobs_tree.heading("File Name", text="File Name")
        self.scheduled_jobs_tree.heading("Time", text="Scheduled Time")
        self.scheduled_jobs_tree.heading("Location", text="File Location")
        self.scheduled_jobs_tree.column("File Name", width=200)
        self.scheduled_jobs_tree.column("Time", width=100)
        self.scheduled_jobs_tree.column("Location", width=500)
        self.scheduled_jobs_tree.pack(pady=10)

        # Define Treeview tags for highlighting
        self.scheduled_jobs_tree.tag_configure("running", background="lightgreen")

        self.show_logs_button = tk.Button(self.root, text="Show Logs", command=self.show_logs)
        self.show_logs_button.pack(pady=5)

        self.about_button = tk.Button(self.root, text="About", command=self.show_about)
        self.about_button.pack(pady=5)

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
            time_input = simpledialog.askstring("Schedule Time", "Enter time (HH:MM 24-hour format):")
            if time_input:
                try:
                    hour, minute = map(int, time_input.split(":"))

                    # Schedule the script and add the job to Treeview
                    schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(self.run_script_with_highlight, file_path)
                    file_name = os.path.basename(file_path)
                    tree_id = self.scheduled_jobs_tree.insert("", tk.END,
                                                              values=(file_name, f"{hour:02d}:{minute:02d}", file_path))

                    # Store job details
                    self.jobs.append({"tree_id": tree_id, "file_name": file_name, "time": f"{hour:02d}:{minute:02d}",
                                      "location": file_path})

                    messagebox.showinfo("Success", f"Scheduled {file_name} at {time_input}")
                except ValueError:
                    messagebox.showerror("Error", "Invalid time format")
        else:
            messagebox.showwarning("Warning", "No script selected")

    def run_script_with_highlight(self, file_path):
        # Find the Treeview item for this file and highlight it
        for job in self.jobs:
            if job["location"] == file_path:
                self.scheduled_jobs_tree.item(job["tree_id"], tags=("running",))
                break

        # Run the script
        self.run_script(file_path)

    def run_now(self):
        selected = self.script_listbox.curselection()
        if selected:
            index = selected[0]
            file_path = self.scripts[index]
            self.run_script_with_highlight(file_path)
        else:
            messagebox.showwarning("Warning", "No script selected")

    def run_script(self, file_path):
        try:
            # Execute the script
            subprocess.Popen(["python", file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Add a timestamped log entry
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.logs.append(f"{timestamp} - Executed {os.path.basename(file_path)}")

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

    def clear_scheduled_jobs(self):
        self.scheduled_jobs_tree.delete(*self.scheduled_jobs_tree.get_children())
        self.jobs.clear()
        schedule.clear()
        messagebox.showinfo("Clear Jobs", "All scheduled jobs have been cleared")

    def show_logs(self):
        logs_window = Toplevel(self.root)
        logs_window.title("Execution Logs")
        logs_window.geometry("600x400")
        log_text = scrolledtext.ScrolledText(logs_window, wrap=tk.WORD, width=70, height=20)
        log_text.pack(pady=10)
        log_text.insert(tk.END, "\n".join(self.logs))
        log_text.config(state=tk.DISABLED)

    def show_about(self):
        messagebox.showinfo("About", "Python Script Scheduler\nVersion 1.0\nCreated by [Your Name]")


# Main application
if __name__ == "__main__":
    root = tk.Tk()
    app = PythonScriptScheduler(root)
    root.mainloop()