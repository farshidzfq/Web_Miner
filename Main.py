import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox
from tkinter import filedialog
import threading
import csv

def scrape_website(url, data_type='text'):
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        if data_type == 'titles':
            data = [title.get_text() for title in soup.find_all('h1')]
        elif data_type == 'links':
            data = [a['href'] for a in soup.find_all('a', href=True)]
        elif data_type == 'images':
            data = [img['src'] for img in soup.find_all('img', src=True)]
        else:
            data = [para.get_text() for para in soup.find_all('p')]

        return data
    except requests.RequestException as e:
        return str(e)

class WebScraperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Web Scraper")
        self.create_widgets()

    def create_widgets(self):
        # ورودی برای URL
        self.url_label = tk.Label(self.root, text="Enter URL:")
        self.url_label.pack(pady=5)

        self.url_entry = tk.Entry(self.root, width=50)
        self.url_entry.pack(pady=5)

        # انتخاب نوع داده در یک فریم
        self.data_type_frame = tk.Frame(self.root)
        self.data_type_frame.pack(pady=5)

        self.data_type_var = tk.StringVar(value='text')
        self.data_type_label = tk.Label(self.data_type_frame, text="Select Data Type:")
        self.data_type_label.pack(side=tk.LEFT, padx=5)

        self.titles_radio = tk.Radiobutton(self.data_type_frame, text="Titles", variable=self.data_type_var, value='titles')
        self.titles_radio.pack(side=tk.LEFT, padx=5)
        
        self.links_radio = tk.Radiobutton(self.data_type_frame, text="Links", variable=self.data_type_var, value='links')
        self.links_radio.pack(side=tk.LEFT, padx=5)

        self.images_radio = tk.Radiobutton(self.data_type_frame, text="Images", variable=self.data_type_var, value='images')
        self.images_radio.pack(side=tk.LEFT, padx=5)

        self.text_radio = tk.Radiobutton(self.data_type_frame, text="Text", variable=self.data_type_var, value='text')
        self.text_radio.pack(side=tk.LEFT, padx=5)

        # دکمه برای شروع scraping
        self.scrape_button = tk.Button(self.root, text="Scrape", command=self.scrape_website_threaded)
        self.scrape_button.pack(pady=5)

        # دکمه برای ذخیره نتایج
        self.save_button = tk.Button(self.root, text="Save to CSV", command=self.save_to_csv)
        self.save_button.pack(pady=5)

        # دکمه برای بارگذاری نتایج
        self.load_button = tk.Button(self.root, text="Load from CSV", command=self.load_from_csv)
        self.load_button.pack(pady=5)

        # جعبه متن برای نمایش نتایج
        self.results_text = scrolledtext.ScrolledText(self.root, width=80, height=20)
        self.results_text.pack(pady=10)

    def scrape_website_threaded(self):
        url = self.url_entry.get()
        data_type = self.data_type_var.get()
        if not url:
            messagebox.showerror("Error", "Please enter a URL")
            return
        
        def task():
            data = scrape_website(url, data_type)
            self.results_text.delete(1.0, tk.END)
            if isinstance(data, str):
                self.results_text.insert(tk.END, f"Error: {data}\n")
            else:
                self.results_text.insert(tk.END, "\n".join(data))
        
        threading.Thread(target=task).start()

    def save_to_csv(self):
        data = self.results_text.get(1.0, tk.END).strip().split('\n')
        if not data:
            messagebox.showerror("Error", "No data to save")
            return
        
        filename = filedialog.asksaveasfilename(defaultextension=".csv",
                                               filetypes=[("CSV files", "*.csv")])
        if filename:
            with open(filename, 'w', newline='') as file:
                writer = csv.writer(file)
                for item in data:
                    writer.writerow([item])
            messagebox.showinfo("Info", "Data saved successfully")

    def load_from_csv(self):
        filename = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if filename:
            with open(filename, 'r') as file:
                data = file.readlines()
                self.results_text.delete(1.0, tk.END)
                self.results_text.insert(tk.END, ''.join(data))

if __name__ == "__main__":
    root = tk.Tk()
    app = WebScraperApp(root)
    root.mainloop()
