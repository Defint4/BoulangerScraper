import os
import csv
class CSVWriter:
    def __init__(self, filename, headers):
        self.filename = filename
        self.headers = headers

    def writeCsv(self, data):
        directory = 'BoulangerCsv' 
        if not os.path.exists(directory):
            os.makedirs(directory)
        filepath = os.path.join(directory, self.filename)
        with open(filepath, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=self.headers)
            writer.writeheader()
            for row in data:
                writer.writerow(row)
                