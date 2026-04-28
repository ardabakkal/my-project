import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import requests

class ExchangeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("💰 Exchange Rate Tracker")
        self.root.geometry("900x650")
        self.root.resizable(True, True)
        
        # Modern renk paleti
        self.bg_color = "#f5f5f5"
        self.primary_color = "#4a6fa5"
        self.secondary_color = "#166088"
        self.accent_color = "#4fc3f7"
        self.text_color = "#333333"
        
        # Stil ayarları (font boyutları artırıldı)
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.root.configure(bg=self.bg_color)
        self.style.configure('TFrame', background=self.bg_color)
        self.style.configure('TLabelFrame', background=self.bg_color, foreground=self.text_color, font=('Arial', 14, 'bold'))  # Boyut 12'den 14'e çıkarıldı
        self.style.configure('TButton', font=('Arial', 12, 'bold'), background=self.primary_color, foreground='white')
        self.style.map('TButton', background=[('active', self.secondary_color), ('pressed', self.accent_color)])
        
        # API verileri
        self.rates = {}
        self.last_updated = ""
        self.favorites = []  # Favoriler başlangıçta BOŞ

        self.setup_ui()
        self.refresh_rates()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding=(20, 15))
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Başlık (font boyutu artırıldı)
        title_label = tk.Label(main_frame, text="💰 Exchange Rate Tracker", 
                             font=('Arial', 18, 'bold'), bg=self.bg_color, fg=self.primary_color)
        title_label.pack(pady=(0, 15))

        # 1. TÜM PARA BİRİMLERİ TABLOSU
        rates_frame = ttk.LabelFrame(main_frame, text="📊 Current Exchange Rates (USD Base)", padding=15)
        rates_frame.pack(fill=tk.BOTH, pady=10, padx=5, expand=True)
        
        self.tree = ttk.Treeview(rates_frame, columns=('Currency', 'Rate'), show='headings', height=12)
        self.tree.heading('Currency', text='Currency', anchor='center')
        self.tree.heading('Rate', text='Rate', anchor='center')
        self.tree.column('Currency', width=150, anchor='center')
        self.tree.column('Rate', width=150, anchor='center')
        
        # Treeview font ayarı
        self.style.configure("Treeview.Heading", font=('Arial', 12))
        self.style.configure("Treeview", font=('Arial', 11), rowheight=25)
        
        scrollbar = ttk.Scrollbar(rates_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        self.tree.pack(fill=tk.BOTH, expand=True)

        # 2. DÖNÜŞTÜRÜCÜ (font boyutları artırıldı)
        converter_frame = ttk.LabelFrame(main_frame, text="🔄 Currency Converter", padding=15)
        converter_frame.pack(fill=tk.X, pady=10, padx=5)
        
        # Grid yapılandırması
        converter_frame.columnconfigure(0, weight=1)
        converter_frame.columnconfigure(1, weight=1)

        # Input fields
        ttk.Label(converter_frame, text="Amount:", font=('Arial', 12)).grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.amount_entry = ttk.Entry(converter_frame, width=15, font=('Arial', 12))
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5, sticky='w')

        ttk.Label(converter_frame, text="From:", font=('Arial', 12)).grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.from_combobox = ttk.Combobox(converter_frame, values=sorted(self.rates.keys()), width=12, font=('Arial', 12))
        self.from_combobox.grid(row=1, column=1, padx=5, pady=5, sticky='w')

        ttk.Label(converter_frame, text="To:", font=('Arial', 12)).grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.to_combobox = ttk.Combobox(converter_frame, values=sorted(self.rates.keys()), width=12, font=('Arial', 12))
        self.to_combobox.grid(row=2, column=1, padx=5, pady=5, sticky='w')

        convert_btn = ttk.Button(converter_frame, text="Convert", command=self.convert_currency)
        convert_btn.grid(row=3, column=0, columnspan=2, pady=10, ipadx=10, ipady=5)

        self.result_var = tk.StringVar()
        result_label = ttk.Label(converter_frame, textvariable=self.result_var, 
                               font=('Arial', 13, 'bold'), foreground=self.secondary_color)
        result_label.grid(row=4, column=0, columnspan=2, pady=(5, 0))

        # 3. FAVORİLER (font boyutları artırıldı)
        favorites_frame = ttk.LabelFrame(main_frame, text="⭐ Favorite Currencies", padding=15)
        favorites_frame.pack(fill=tk.X, pady=10, padx=5)

        self.fav_text = tk.Text(favorites_frame, height=4, font=('Arial', 12), 
                               bg='white', fg=self.text_color, padx=10, pady=10)
        self.fav_text.pack(fill=tk.X)

        # Favori ekleme/çıkarma paneli
        fav_controls = ttk.Frame(favorites_frame)
        fav_controls.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(fav_controls, text="Currency Code:", font=('Arial', 12)).pack(side=tk.LEFT, padx=5)
        self.fav_entry = ttk.Entry(fav_controls, width=5, font=('Arial', 12))
        self.fav_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(fav_controls, text="Add", command=self.add_favorite).pack(side=tk.LEFT, padx=5)
        ttk.Button(fav_controls, text="Remove", command=self.remove_favorite).pack(side=tk.LEFT, padx=5)

        # Refresh butonu
        ttk.Button(main_frame, text="🔄 Refresh Data", command=self.refresh_rates).pack(pady=(15, 5))
        
        # Footer (font boyutu artırıldı)
        tk.Label(main_frame, text="© 2023 Exchange Rate Tracker", 
                font=('Arial', 10), bg=self.bg_color, fg='gray').pack(side=tk.BOTTOM)

    def refresh_rates(self):
        try:
            response = requests.get("https://api.exchangerate-api.com/v4/latest/USD")
            data = response.json()
            self.rates = data['rates']
            self.last_updated = datetime.fromtimestamp(data['time_last_updated']).strftime("%d/%m/%Y %H:%M")
            
            # Combobox'ları güncelle
            self.from_combobox['values'] = sorted(self.rates.keys())
            self.to_combobox['values'] = sorted(self.rates.keys())
            
            self.update_ui()
            messagebox.showinfo("Success", f"Rates updated!\nLast update: {self.last_updated}")
        except Exception as e:
            messagebox.showerror("Error", f"API error: {str(e)}")

    def update_ui(self):
        # TÜM para birimlerini göster
        self.tree.delete(*self.tree.get_children())
        for currency, rate in sorted(self.rates.items()):
            self.tree.insert('', 'end', values=(currency, f"{rate:.4f}"))

        # Sadece favorileri göster
        self.fav_text.delete(1.0, tk.END)
        for fav in self.favorites:
            if fav in self.rates:
                self.fav_text.insert(tk.END, f"{fav}: {self.rates[fav]:.4f}\n")

    def add_favorite(self):
        curr = self.fav_entry.get().upper().strip()
        if len(curr) != 3:
            messagebox.showerror("Error", "Currency code must be 3 letters (e.g. USD)")
            return
            
        if curr not in self.rates:
            messagebox.showerror("Error", f"Invalid currency: {curr}")
            return
            
        if curr not in self.favorites:
            self.favorites.append(curr)
            self.update_ui()
            messagebox.showinfo("Added", f"{curr} added to favorites!")
        else:
            messagebox.showinfo("Info", f"{curr} already in favorites")

    def remove_favorite(self):
        curr = self.fav_entry.get().upper().strip()
        if curr in self.favorites:
            self.favorites.remove(curr)
            self.update_ui()
            messagebox.showinfo("Removed", f"{curr} removed from favorites")
        else:
            messagebox.showerror("Error", f"{curr} not in favorites")

    def convert_currency(self):
        """Para birimi dönüşümü yapar (Performs currency conversion)"""
        try:
            amount = float(self.amount_entry.get())
            from_curr = self.from_combobox.get()
            to_curr = self.to_combobox.get()

            if from_curr not in self.rates or to_curr not in self.rates:
                messagebox.showerror("Error", "Invalid currency selection!")
                return

            converted = amount * (self.rates[to_curr] / self.rates[from_curr])
            self.result_var.set(f"🔹 {amount:.2f} {from_curr} = {converted:.2f} {to_curr}")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid numeric amount!")

if __name__ == "__main__":
    root = tk.Tk()
    app = ExchangeApp(root)
    root.mainloop()