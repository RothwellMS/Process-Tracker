
import csv
from datetime import datetime
import os
import tkinter as tk
from tkinter import messagebox
from ctypes import windll


class DataProcessor:
    def __init__(self):
        """
        Initialize the DataProcessor class.
        Set DPI awareness to avoid blurriness.
        Initialize paths for different categories.
        Initialize received_data variable.
        Create the main window with input fields, labels, and buttons.
        """
        try:
            windll.shcore.SetProcessDpiAwareness(1)
        except Exception as e:
            print(f"Failed to set DPI awareness: {e}")

        self.Laser_Cutter_path = "Laser Cutter/"
        self.Knock_Out_Path = "Knock Out/"
        self.Plastic_Path = "Plastic/"
        self.Insulation_Path = "Insulation/"
        self.Straight_Line_Path = "Straight Line/"
        self.Storage_Path = "Storage/"

        self.received_data = ""
        self.awaiting_cage_code = False  # Track if awaiting a Cage No

        # Create the main window
        self.root = tk.Tk()
        self.root.title("Data Processor")
        self.root.geometry("400x200")

        # Create input field for received data
        self.input_field = tk.Entry(self.root, font=("Arial", 14))
        self.input_field.pack(pady=20)

        # Create status label
        self.status_label = tk.Label(self.root, text="Please scan a label", font=("Arial", 12))
        self.status_label.pack()

        # Bind Enter key to process input
        self.input_field.bind("<Return>", self.process_input)

        self.root.mainloop()

    def process_input(self, event):
        """
        Process the received input from the scanner.
        """
        data = self.input_field.get().strip()
        self.input_field.delete(0, tk.END)

        if data.endswith(" T"):
            self.awaiting_cage_code = True
            self.received_data = data
            self.status_label.config(text="Please scan a Cage Code")

        elif self.awaiting_cage_code:
            if data.lower() == "exit":
                self.reset_cage_code_process()
            elif data[:-2].isdigit():
                self.write_to_storage(data)
            else:
                self.status_label.config(text="Invalid Cage No, please scan a valid label")
        elif data.endswith(" D"):
            self.process_deletion(data)
        else:
            self.status_label.config(text="Invalid input, please scan a valid label")

    def reset_cage_code_process(self):
        """
        Resets the Cage Code process.
        """
        self.awaiting_cage_code = False
        self.received_data = ""
        self.status_label.config(text="Cage Code process exited. Please scan a label.")

    def write_to_storage(self, cage_code):
        """
        Writes the combined data to the storage and log files.
        """
        current_date = datetime.now().strftime("%Y-%m-%d")
        full_data = f"{self.received_data} {cage_code} {current_date}"

        with open(os.path.join(self.Storage_Path, "Storage.csv"), "a", newline="") as storage_file:
            writer = csv.writer(storage_file)
            writer.writerow([full_data])

        with open(os.path.join(self.Storage_Path, "Log.csv"), "a", newline="") as log_file:
            writer = csv.writer(log_file)
            writer.writerow([full_data])

        self.awaiting_cage_code = False
        self.received_data = ""
        self.status_label.config(text="Data saved successfully. Please scan a label.")

    def process_deletion(self, data):
        """
        Deletes data from Storage.csv and adds it to Log.csv if it ends with ' D'.
        """
        storage_path = os.path.join(self.Storage_Path, "Storage.csv")
        log_path = os.path.join(self.Storage_Path, "Log.csv")

        # Read all lines from Storage.csv
        with open(storage_path, "r", newline="") as storage_file:
            rows = list(csv.reader(storage_file))

        # Filter out the rows that match the scanned data
        new_rows = [row for row in rows if row and row[0] != data]

        # Write the filtered rows back to Storage.csv
        with open(storage_path, "w", newline="") as storage_file:
            writer = csv.writer(storage_file)
            writer.writerows(new_rows)

        # Log the deleted data
        with open(log_path, "a", newline="") as log_file:
            writer = csv.writer(log_file)
            writer.writerow([data])

        self.status_label.config(text="Data deleted and logged successfully. Please scan a label.")

if __name__ == "__main__":
    DataProcessor()
