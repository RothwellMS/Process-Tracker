import csv
from datetime import datetime
import os
import tkinter as tk
from tkinter import messagebox  # Import messagebox
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
        # Set DPI awareness to avoid blurriness
        try:
            windll.shcore.SetProcessDpiAwareness(1)
        except Exception as e:
            print(f"Failed to set DPI awareness: {e}")

        self.Laser_Cutter_path = "Laser Cutter/"
        self.Knock_Out_Path = "Knock Out/"
        self.Plastic_Path = "Plastic/"
        self.Insulation_Path = "Insulation/"
        self.Straight_Line_Path = "Straight Line/"

        self.received_data = ""

        # Create the main window
        self.window = tk.Tk()
        self.window.title("Process Tracker")

        # Get the screen width and height
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        # Calculate the position to center the window
        position_x = (screen_width // 2) - (600 // 2)
        position_y = (screen_height // 2) - (500 // 2)

        self.window.geometry(f"600x500+{position_x}+{position_y}")

        # Create input fields and labels with larger font size
        self.data_label = tk.Label(
            self.window, text="Enter data:", font=("Helvetica", 14))
        self.data_label.pack()

        self.data_entry = tk.Entry(self.window, font=("Helvetica", 14))
        self.data_entry.pack()

        # Bind the process_data_ui method to the Return key
        self.data_entry.bind("<Return>", self.process_data_ui)

        # Create a button to calculate sum (optional) with larger font size
        self.sum_button = tk.Button(
            self.window, text="Calculate Sum", command=self.calculate_sum, font=("Helvetica", 14))
        self.sum_button.pack(pady=10)

        # Initialize the list to store labels
        self.labels = []

        # Create a status label with larger font size
        self.status_label = tk.Label(
            self.window, text="", font=("Helvetica", 12))
        self.status_label.pack(pady=10)

    def process_data_ui(self, event=None):
        """
        Process the data entered in the input field.
        Check if the QR code has been scanned.
        Find the appropriate file path based on the data category.
        Process the data and write it to the corresponding file.
        Display the processed data and update the status label.
        """
        data = self.data_entry.get()
        if self.received_data == data:
            self.handle_error(ValueError("The QR code has been scanned"))
            return
        else:
            self.received_data = data
        file_path = self.path_finder(data)
        if file_path == "Error":
            self.handle_error(ValueError("Invalid data category"))
            return

        try:
            data = data[:-2]
            data = data.strip().split(",")
            del data[6]
            data = ", ".join(data) + "\n"
        except IndexError as e:
            self.handle_error(e)
            return

        try:
            self.data_write(file_path, data)
            self.display_label(self.data_entry.get())
            self.status_label.config(
                text="Data processed successfully.", fg="green")
            self.data_entry.delete(0, tk.END)
        except Exception as e:
            self.handle_error(e)

    def path_finder(self, data):
        """
        Find the appropriate file path based on the data category.

        Parameters:
        data (str): The data entered in the input field.

        Returns:
        str: The file path corresponding to the data category.
        """
        if data.strip().endswith(" L"):
            return self.Laser_Cutter_path
        elif data.strip().endswith(" K"):
            return self.Knock_Out_Path
        elif data.strip().endswith(" P"):
            return self.Plastic_Path
        elif data.strip().endswith(" I"):
            return self.Insulation_Path
        elif data.strip().endswith(" S"):
            return self.Straight_Line_Path
        else:
            return "Error"

    def data_write(self, file_path, data):
        """
        Write the processed data to the corresponding file.

        Parameters:
        file_path (str): The file path where the data will be written.
        data (str): The processed data to be written.
        """
        current_date = datetime.now().strftime("%d-%m-%Y")
        file_name = f"{file_path}{current_date}.csv"

        if not os.path.exists(file_name):
            with open(file_name, "w") as new_file:
                new_file.write(
                    "Ref,Item No.,NC#,Field 1,Field 2,Description,Area(m^2)(Metal),Area(m^2)(Ins)\n")

            with open(file_name, "a") as csv_file:
                csv_file.write(data)
        else:
            with open(file_name, "r") as csv_file:
                existing_data = csv_file.read()
                if data in existing_data:
                    raise ValueError("Data already exists in the file")

            with open(file_name, "a") as csv_file:
                csv_file.write(data)

    def display_label(self, text):
        """
        Display the processed data in a label.

        Parameters:
        text (str): The processed data to be displayed.
        """
        label = tk.Label(self.window, text=text, font=("Helvetica", 10))
        label.pack(padx=10, pady=10)
        self.labels.append(label)
        if len(self.labels) > 5:
            self.labels[0].destroy()
            del self.labels[0]

    def handle_error(self, e):
        """
        Handle any errors that occur during data processing.

        Parameters:
        e (Exception): The exception that occurred.
        """
        self.data_entry.delete(0, tk.END)
        self.status_label.config(text=f"An error occurred: {str(e)}", fg="red")

    def calculate_sum(self):
        """
        Calculate the total area processed for each category.

        Returns:
        dict: A dictionary containing the total area processed for each category.
        """
        current_date = datetime.now().strftime("%d-%m-%Y")
        folders = [
            self.Laser_Cutter_path,
            self.Knock_Out_Path,
            self.Plastic_Path,
            self.Insulation_Path,
            self.Straight_Line_Path
        ]

        sums = {}
        if os.path.exists(f'{current_date}.csv'):
            os.remove(f'{current_date}.csv')
        for folder in folders:
            file_path = os.path.join(folder, f"{current_date}.csv")
            if os.path.exists(file_path):
                with open(file_path, "r") as csv_file:
                    reader = csv.reader(csv_file)
                    next(reader)  # Skip header
                    total = 0
                    for row in reader:
                        if folder == self.Insulation_Path:
                            total += float(row[7])  # 8th column for Insulation
                        else:
                            # 7th column for other folders
                            total += float(row[6])
                    sums[folder] = round(total, 2)

                with open(f'{current_date}.csv', 'a') as record:
                    record.write(f"Ref,Item No.,NC#,Field 1,Field 2,Description,Area(m^2)(Metal),Area(m^2)(Ins),Opreation,Sum: {
                                 sums[folder]}\n")
                    with open(file_path, "r") as csv_file:
                        for line in csv_file.readlines()[1:]:
                            line = line.rstrip() + f",{folder.strip('/')}\n"
                            record.write(line)
            else:
                sums[folder] = None  # File does not exist

        # Display the sums in a message box
        result_message = "\n".join(
            [f"{folder.strip('/')}: {total} m^2" for folder, total in sums.items()])
        messagebox.showinfo("Sum Results", result_message)

        return sums


processor = DataProcessor()
processor.window.mainloop()
