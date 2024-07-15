import csv
from datetime import datetime
import tkinter as tk
from tkinter import messagebox

labels = []

def save_data(event=None):
    global labels
    user_input = entry.get()
    if user_input.lower() == 'exit':
        root.destroy()
    else:
        # Remove double quotes from the user input
        user_input = user_input.replace('"', '')

        # Create a label widget to display the user input
        label = tk.Label(root, text=user_input)
        label.pack(padx=10, pady=10)

        # Add the label to the list
        labels.append(label)

        # If there are more than 5 labels, destroy the first one
        if len(labels) > 5:
            labels[0].destroy()
            del labels[0]

        # Write the user input to the file
        with open(f"{current_date}.csv", "a", newline='') as csvfile:
            writer = csv.writer(csvfile)
            if csvfile.tell() == 0:  # Check if the file is empty
                writer.writerow(["Ref", "NC#", "Field 1", "Field 2", "Item No", "Description"])
            writer.writerow(user_input.split(','))

        entry.delete(0, tk.END)

        # If there are five labels, destroy the "Ready to Scan" label
        if len(labels) == 5:
            ready_label.destroy()

# Get current date in DD-MM-YYYY format
current_date = datetime.now().strftime("%d-%m-%Y")

# Create the main window
root = tk.Tk()
root.title("Laser Cutter")

# Set the geometry of the main window to be 400x300 and center it on the screen
root.geometry("400x300+400+300")

# Create an entry widget
entry = tk.Entry(root, width=30)
entry.pack(padx=10, pady=10)

# Bind the Enter key to the save_data function
entry.bind('<Return>', save_data)

# Create a button to save data
save_button = tk.Button(root, text="Save Data", command=save_data)
save_button.pack(padx=10, pady=10)

# Create a label to display a ready message
ready_label = tk.Label(root, text="Ready to Scan")
ready_label.pack(padx=10, pady=10)

# Run the application
root.mainloop()