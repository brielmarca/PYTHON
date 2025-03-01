import tkinter as tk
from tkinter import messagebox

class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Task List")
        
        self.tasks = []

        # Configure grid weights for proper resizing
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # Create widgets
        self.task_listbox = tk.Listbox(root, height=10, width=50, selectmode=tk.SINGLE)
        self.scrollbar = tk.Scrollbar(root, orient=tk.VERTICAL, command=self.task_listbox.yview)
        self.task_listbox.config(yscrollcommand=self.scrollbar.set)
        
        self.entry_task = tk.Entry(root, width=40)
        self.btn_add = tk.Button(root, text="Add Task", width=20, command=self.add_task)
        self.btn_remove = tk.Button(root, text="Remove Task", width=20, command=self.remove_task)
        self.btn_complete = tk.Button(root, text="Complete Task", width=20, command=self.complete_task)

        # Grid layout with sticky attributes
        self.task_listbox.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.entry_task.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self.btn_add.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        self.btn_remove.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        self.btn_complete.grid(row=4, column=0, padx=10, pady=5, sticky="ew")

    def add_task(self):
        task = self.entry_task.get().strip()
        if task:
            self.tasks.append(task)
            self.update_task_listbox()
            self.entry_task.delete(0, tk.END)
        else:
            messagebox.showwarning("Empty Input", "Please enter a task.")

    def remove_task(self):
        selected_task_index = self.task_listbox.curselection()
        if selected_task_index:
            self.tasks.pop(selected_task_index[0])
            self.update_task_listbox()
        else:
            messagebox.showwarning("No Task Selected", "Please select a task to remove.")

    def complete_task(self):
        selected_task_index = self.task_listbox.curselection()
        if selected_task_index:
            index = selected_task_index[0]
            if not self.tasks[index].endswith("(Completed)"):
                self.tasks[index] += " (Completed)"
                self.update_task_listbox()
        else:
            messagebox.showwarning("No Task Selected", "Please select a task to mark as completed.")

    def update_task_listbox(self):
        self.task_listbox.delete(0, tk.END)
        for task in self.tasks:
            self.task_listbox.insert(tk.END, task)

# Main window setup
root = tk.Tk()
app = TodoApp(root)
root.mainloop()