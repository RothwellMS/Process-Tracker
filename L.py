with open("Storage/Location.csv","a") as csv_file:
    for color in ["R","B","G"]:
        for x in range(0, 10):
            for y in ["A","B","C"]:
                if color == "G" and y == "C": 
                    continue
                else:
                    csv_file.write(f"{x+1}-{y}-{color},0\n")