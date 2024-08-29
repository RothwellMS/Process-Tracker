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

        self.Laser_Cutter_Path = "Laser Cutter/"
        self.Knock_Out_Path = "Knock Out/"
        self.Insulation_Path = "Insulation/"
        self.Straight_Line_Path = "Straight Line/"
        self.Storage_Path = "Storage/"

        self.received_data = ""
        self.awaiting_cage_code = False  # Track if awaiting a Cage No

        # Create the main window
        self.window = tk.Tk()
        self.window.title("Process Tracker")

        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        position_x = (screen_width // 2) - (600 // 2)
        position_y = (screen_height // 2) - (500 // 2)

        self.window.geometry(f"600x500+{position_x}+{position_y}")

        self.data_label = tk.Label(
            self.window, text="Enter data:", font=("Helvetica", 14))
        self.data_label.pack(pady=10)

        self.data_entry = tk.Entry(self.window, font=("Helvetica", 14))
        self.data_entry.pack(pady=10)
        self.data_entry.bind("<Return>", self.process_data_ui)

        self.sum_button = tk.Button(
            self.window, text="Calculate Sum", command=self.calculate_sum, font=("Helvetica", 14))
        self.sum_button.pack(pady=10)

        self.labels = []
        self.status_label = tk.Label(
            self.window, text="", font=("Helvetica", 12))
        self.status_label.pack(pady=10)

        self.window.protocol("WM_DELETE_WINDOW",
                             self.calculate_sum_before_close)

    def calculate_sum_before_close(self):
        self.calculate_sum()
        self.window.destroy()

    def process_data_ui(self, event=None):
        data = self.data_entry.get().strip()

        if self.awaiting_cage_code:
            self.process_cage_code(data)
        else:
            if data.endswith(" T"):
                if self.received_data == data:
                    self.handle_error(ValueError(
                        "The QR code has been scanned"))
                    return
                else:
                    self.received_data = data
                    try:
                        t_data = data[:-2]
                        t_data = t_data.strip().split(",")
                        if len(t_data) < 10:
                            self.handle_error(ValueError(
                                "Invalid QR code"))
                            return
                        del t_data[6], t_data[-2], t_data[-1]
                        t_data = ", ".join([x.strip() for x in t_data])
                        self.t_data = t_data
                    except IndexError as e:
                        self.handle_error(e)
                        return
                self.awaiting_cage_code = True
                self.data_entry.delete(0, tk.END)
                self.status_label.config(
                    text="Please scan a Cage Code or Input Exit to Interrupt", fg="green")
            elif data.endswith(" D"):
                self.process_deletion(data)
            else:
                self.process_regular_data(data)

    def process_deletion(self, data):
        """
        1. Find the data in the Storage.csv file
        2. Get the full data from the Storage.csv file
        3. Try deleting the data from the Storage.csv file, if failed then raise an exception and handle it
        4. Add the data to Log.csv file and set flag to true
        """
        data = [x.strip() for x in data.strip().split(",")[:3]]
        storage_path = os.path.join(self.Storage_Path, "Storage.csv")

        try:
            with open(storage_path, "r", newline="") as storage_file:
                rows = list(csv.reader(storage_file))
        except IOError as e:
            self.handle_error(e)
            return

        del_data = None

        for row in rows:
            if [x.strip() for x in row[:len(data)]] == data:
                del_data = row
                break
        if del_data is None:
            self.handle_error(ValueError("Data not found in Storage"))
            return

        try:
            rows.remove(del_data)
            del_data = del_data[:-1]
        except IndexError as e:
            self.handle_error(e)
            return
        except ValueError as e:
            self.handle_error(e)
            return

        with open(storage_path, "w", newline="") as storage_file:
            writer = csv.writer(storage_file)
            writer.writerows(rows)

        current_time = datetime.now().strftime("%d-%m-%Y")

        del_data.append(current_time)
        del_data = ",".join([x.strip() for x in del_data])

        self.data_write(self.Storage_Path, del_data, flag=True)
        self.data_entry.delete(0, tk.END)
        self.display_label(del_data)
        self.status_label.config(
            text="Data processed successfully.", fg="green")

    def process_regular_data(self, data):
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
            s_data = data[:-2]
            s_data = s_data.strip().split(",")
            del s_data[6:9]
            s_data = ", ".join(s_data) + "\n"
        except IndexError as e:
            self.handle_error(e)
            return

        try:
            self.data_write(file_path, s_data)
            self.display_label(self.data_entry.get())
            self.status_label.config(
                text="Data processed successfully.", fg="green")
            self.data_entry.delete(0, tk.END)
        except Exception as e:
            self.handle_error(e)

    def process_cage_code(self, data):
        if not data[:-2].isdigit():
            if data.lower() == "exit":
                self.received_data = ""
                self.status_label.config(
                    text="Storage Process has been interrupted. Please continue scan.", fg="green")
                self.awaiting_cage_code = False
                self.data_entry.delete(0, tk.END)
            else:
                self.status_label.config(
                    text="Invalid Cage No, please scan a valid label", fg="red")
                self.data_entry.delete(0, tk.END)
        else:
            cage_no = data[:-2]
            current_date = datetime.now().strftime("%d-%m-%Y")
            combined_data = f"{self.t_data}, {cage_no}, {current_date}\n"
            try:
                self.data_write(self.Storage_Path, combined_data)
                self.status_label.config(
                    text="Cage processed successfully.", fg="green")
                self.display_label(combined_data)
                self.data_entry.delete(0, tk.END)
                self.awaiting_cage_code = False
            except Exception as e:
                self.handle_error(e)

    def path_finder(self, data):
        if data.endswith(" L"):
            return self.Laser_Cutter_path
        elif data.endswith(" K"):
            return self.Knock_Out_Path
        elif data.endswith(" I"):
            return self.Insulation_Path
        elif data.endswith(" S"):
            return self.Straight_Line_Path
        elif data.endswith(" T") or data.endswith(" D"):
            return self.Storage_Path
        else:
            return "Error"

    def data_write(self, file_path, data, flag=False):
        if file_path == self.Storage_Path:
            storage_file_name = os.path.join(self.Storage_Path, "Storage.csv")
            log_file_name = os.path.join(self.Storage_Path, "Log.csv")

            if not os.path.exists(storage_file_name):
                with open(storage_file_name, "w") as new_file:
                    new_file.write(
                        "Ref,Item No.,NC#,Field 1,Field 2,Description,End1,End2,Cage No.,Date\n")

            if not os.path.exists(log_file_name):
                with open(log_file_name, "w") as new_file:
                    new_file.write(
                        "Ref,Item No.,NC#,Field 1,Field 2,Description,End1,End2,Cage No.,Date,Operation\n")

            if not flag:
                with open(storage_file_name, "a") as csv_file:
                    csv_file.write(data)

            with open(log_file_name, "a") as csv_file:
                if flag:
                    csv_file.write(f"{data.strip()}, Delivered\n")
                else:
                    csv_file.write(f"{data.strip()}, Storaged\n")

        else:
            current_date = datetime.now().strftime("%d-%m-%Y")
            file_name = f"{file_path}{current_date}.csv"

            if not os.path.exists(file_name):
                with open(file_name, "w") as new_file:
                    new_file.write(
                        "Ref,Item No.,NC#,Field 1,Field 2,Description,Area(m^2)(Metal),Area(m^2)(Ins)\n")

            with open(file_name, "r") as csv_file:
                existing_data = csv_file.read()
                if data in existing_data:
                    raise ValueError("Data already exists in the file")

            with open(file_name, "a") as csv_file:
                csv_file.write(data)

    def display_label(self, text):
        label = tk.Label(self.window, text=text, font=("Helvetica", 10))
        label.pack(padx=10, pady=10)
        self.labels.append(label)
        if len(self.labels) > 5:
            self.labels[0].destroy()
            del self.labels[0]

    def handle_error(self, e):
        self.data_entry.delete(0, tk.END)
        self.status_label.config(text=f"An error occurred: {str(e)}", fg="red")
        if str(e) != "The QR code has been scanned":
            self.received_data = ""

    def calculate_sum(self):
        """Calculates the sum for each folder and writes to the summary file."""
        folders = [self.Insulation_Path,
                   self.Laser_Cutter_Path,
                   self.Knock_Out_Path,
                   self.Straight_Line_Path]
        sums = {}
        current_date = datetime.now().strftime("%d-%m-%Y")
        if os.path.exists(f'{current_date}.csv'):
            os.remove(f'{current_date}.csv')

        for folder in folders:
            file_path = os.path.join(
                folder, f"{datetime.now().strftime('%d-%m-%Y')}.csv")
            if os.path.exists(file_path):
                total = 0
                with open(file_path, "r") as csv_file:
                    reader = csv.reader(csv_file)
                    next(reader)
                    total = sum(
                        float(row[7]) if folder == "Insulation/" else float(row[6]) for row in reader)
                    sums[folder] = round(total, 2)

                    with open(f'{current_date}.csv', 'a') as record:
                        record.write(
                            f"{folder.strip('/')} Sum: {sums[folder]} m^2\n")
                        record.write(
                            f"Ref,Item No.,NC#,Field 1,Field 2,Description,Area(m^2)(Metal),Area(m^2)(Ins)\n")
                        csv_file.seek(0)
                        next(reader)  # Skip header again
                        for row in reader:
                            record.write(",".join(row) +
                                         f",{folder.strip('/')}\n")
            else:
                sums[folder] = None

        result_message = "\n".join(
            [f"{folder.strip('/')}: {total} m^2" for folder, total in sums.items()])
        messagebox.showinfo("Sum Results", result_message)

        return sums


processor = DataProcessor()
processor.window.mainloop()
