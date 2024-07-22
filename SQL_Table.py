import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from datetime import datetime
import os


class CSVProcessor:
    def __init__(self, file):
        self.file = file

    def SQL_operation(self):
        with open(self.file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if len(line.split(",")) == 10:
                    date = os.path.basename(self.file).strip(".csv")
                    # Assuming the original format is YYYY-MM-DD
                    date_obj = datetime.strptime(date, '%d-%m-%Y')
                    date = date_obj.strftime('%Y-%m-%d')
                    continue
                else:
                    operation = line.strip().split(",")[8]
                    operation = operation.lstrip(" ")
                    operation = operation.rstrip(" ")
                    with open(f'SQL_{date}_{operation}.csv', 'a') as fl:
                        line = [item.strip() for item in line.strip().split(",")]
                        line.append(date)
                        fl.write(",".join(line) + "\n")

    def SQL_operation2(self):
        abspath = os.path.abspath(self.file)
        abspath = abspath.split("\\")
        operation = abspath[-2]
        operation = operation.lstrip(" ")
        operation = operation.rstrip(" ")
        date = os.path.basename(self.file).strip(".csv")
        # Assuming the original format is YYYY-MM-DD
        date_obj = datetime.strptime(date, '%d-%m-%Y')
        date = date_obj.strftime('%Y-%m-%d')
        with open(self.file, 'r') as f:
            lines = f.readlines()
        with open(f"SQL_{date}_{operation}.csv", 'a') as f:
            for line in lines[1:]:
                line = [item.strip() for item in line.strip().split(",")]
                line.append(operation)
                line.append(date)
                f.write(",".join(line) + "\n")

    def operation_select(self):
        with open(self.file, 'r') as f:
            line = f.readlines()[0]
            if line.startswith("Ref,Item No.,NC#,Field 1,Field 2,Description,Area(m^2)(Metal),Area(m^2)(Ins),Opreation,Sum:"):
                self.SQL_operation()
            elif line.startswith("Ref,Item No.,NC#,Field 1,Field 2,Description,Area(m^2)(Metal),Area(m^2)(Ins)"):
                self.SQL_operation2()
            else:
                raise ValueError("Can't recognize this file")


def process_csv_files():
    file_paths = filedialog.askopenfilenames()
    if file_paths:
        for file_path in file_paths:
            # Check if the selected file is a CSV file
            if not file_path.endswith('.csv'):
                messagebox.showerror("Error", "Please select a CSV file.")
                continue

            processor = CSVProcessor(file_path)
            try:
                # Update the selected file path label
                selected_file_label.config(text=f"Selected File: {
                                           os.path.basename(file_path)}")

                # Process the CSV file
                processor.operation_select()

                messagebox.showinfo("Success", f"CSV file '{
                                    os.path.basename(file_path)}' processed successfully.")
            except ValueError as e:
                messagebox.showerror("Error", str(e))


# Create the main window
root = tk.Tk()
root.title("CSV Processor")

# Set the size of the main window
root.geometry("400x300")

# Create a label and file dialog button
label = tk.Label(root, text="Select CSV files to process")
label.pack(pady=10)

selected_file_label = tk.Label(root, text="Selected Files: None")
selected_file_label.pack(pady=5)

button = tk.Button(root, text="Open Files", command=process_csv_files)
button.pack(pady=10)

# Run the main loop
root.mainloop()
