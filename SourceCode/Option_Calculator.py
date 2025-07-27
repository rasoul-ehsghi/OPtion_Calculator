import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np

# Function to convert English numbers to Persian
def to_persian_number(number):
    persian_numbers = {'0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴', 
                       '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹'}
    return ''.join(persian_numbers.get(char, char) for char in str(number))

# Function to calculate strategy metrics
def calculate_strategy_metrics(strategy, strategy_data):
    if strategy == "Straddle":
        call_data = next(item for item in strategy_data if item['type'] == 'call')
        put_data = next(item for item in strategy_data if item['type'] == 'put')
        total_premium = call_data['premium'] + put_data['premium']
        max_profit = np.inf  # Unlimited profit
        max_loss = total_premium
        breakevens = [call_data['strike'] + total_premium, put_data['strike'] - total_premium]
    elif strategy == "Strangle":
        call_data = next(item for item in strategy_data if item['type'] == 'call')
        put_data = next(item for item in strategy_data if item['type'] == 'put')
        total_premium = call_data['premium'] + put_data['premium']
        max_profit = np.inf  # Unlimited profit
        max_loss = total_premium
        breakevens = [call_data['strike'] + total_premium, put_data['strike'] - total_premium]
    elif strategy == "Bull Call Spread":
        long_call = next(item for item in strategy_data if item['direction'] == 1)
        short_call = next(item for item in strategy_data if item['direction'] == -1)
        net_cost = long_call['premium'] - short_call['premium']
        max_profit = (short_call['strike'] - long_call['strike']) - net_cost
        max_loss = net_cost
        breakevens = [long_call['strike'] + net_cost]
    elif strategy == "Bear Call Spread":
        short_call = next(item for item in strategy_data if item['direction'] == -1)
        long_call = next(item for item in strategy_data if item['direction'] == 1)
        
        # محاسبه اعتبار خالص
        net_credit = short_call['premium'] - long_call['premium']
        
        # محاسبه حداکثر سود
        max_profit = net_credit
        
        # محاسبه حداکثر ضرر
        max_loss = (long_call['strike'] - short_call['strike']) - net_credit
        
        # محاسبه نقطه سر به سر
        breakevens = [short_call['strike'] + net_credit]
    elif strategy == "Bear Put Spread":
        long_put = next(item for item in strategy_data if item['direction'] == 1 and item['type'] == 'put')
        short_put = next(item for item in strategy_data if item['direction'] == -1 and item['type'] == 'put')
        net_cost = long_put['premium'] - short_put['premium']
        max_profit = (long_put['strike'] - short_put['strike']) - net_cost
        max_loss = net_cost
        breakevens = [long_put['strike'] - net_cost]
    elif strategy == "Bull Put Spread":
        # پیدا کردن آپشن‌های خرید و فروش
        long_put = next(item for item in strategy_data if item['direction'] == 1 and item['type'] == 'put')
        short_put = next(item for item in strategy_data if item['direction'] == -1 and item['type'] == 'put')

        # محاسبه اعتبار خالص
        net_credit = short_put['premium'] - long_put['premium']

        # محاسبه حداکثر سود
        max_profit = net_credit

        # محاسبه حداکثر زیان
        max_loss = (short_put['strike'] - long_put['strike']) - net_credit

        # محاسبه نقطه سر به سر
        breakevens = [short_put['strike'] - net_credit]

        # محاسبه درصد سود (با استفاده از مقدار مطلق حداکثر ضرر)
        if max_loss == 0:
            profit_percentage = "بینهایت"
        else:
            profit_percentage = (max_profit / abs(max_loss)) * 100
    elif strategy == "Butterfly":
        long_call_low = next(item for item in strategy_data if item['direction'] == 1 and item['strike'] == min(item['strike'] for item in strategy_data))
        short_call_mid = next(item for item in strategy_data if item['direction'] == -1)
        long_call_high = next(item for item in strategy_data if item['direction'] == 1 and item['strike'] == max(item['strike'] for item in strategy_data))
        net_cost = long_call_low['premium'] + long_call_high['premium'] - 2 * short_call_mid['premium']
        max_profit = (short_call_mid['strike'] - long_call_low['strike']) - net_cost
        max_loss = net_cost
        breakevens = [long_call_low['strike'] + net_cost, long_call_high['strike'] - net_cost]
    elif strategy == "Covered Call":
        call_data = strategy_data[0]
        stock_price = float(entry_market_price.get())
        max_profit = (call_data['strike'] - stock_price) + call_data['premium']
        max_loss = stock_price - call_data['premium']
        breakevens = [stock_price - call_data['premium']]
    elif strategy == "Long Call":
        call_data = strategy_data[0]
        max_profit = np.inf  # Unlimited profit
        max_loss = call_data['premium']
        breakevens = [call_data['strike'] + call_data['premium']]
    elif strategy == "Short Call":
        call_data = strategy_data[0]
        max_profit = call_data['premium']
        max_loss = np.inf  # Unlimited loss
        breakevens = [call_data['strike'] + call_data['premium']]
    elif strategy == "Long Put":
        put_data = strategy_data[0]
        max_profit = put_data['strike'] - put_data['premium']
        max_loss = put_data['premium']
        breakevens = [put_data['strike'] - put_data['premium']]
    elif strategy == "Short Put":
        put_data = strategy_data[0]
        max_profit = put_data['premium']
        max_loss = put_data['strike'] - put_data['premium']
        breakevens = [put_data['strike'] - put_data['premium']]
    else:
        max_profit, max_loss, breakevens = 0, 0, []

    # Calculate profit percentage
    if max_loss == 0:
        profit_percentage = "بینهایت"
    else:
        profit_percentage = (max_profit / max_loss) * 100

    return max_profit, max_loss, breakevens, profit_percentage

# Function to calculate strategy
def calculate_strategy():
    try:
        strategy = strategy_var.get()
        if strategy == "انتخاب استراتژی":
            messagebox.showwarning("هشدار", "لطفاً یک استراتژی انتخاب کنید.")
            return

        market_price = float(entry_market_price.get())

        # Gather input values dynamically
        strategy_data = []
        for var_name, entry in input_elements.items():
            input_value = float(entry.get())
            parts = var_name.split('_')
            direction = 1 if 'long' in parts else -1
            option_type = 'call' if 'call' in parts else 'put'
            if 'strike' in parts:
                strike = input_value
            elif 'premium' in parts:
                premium = input_value
                strategy_data.append({
                    'strike': strike,
                    'premium': premium,
                    'type': option_type,
                    'direction': direction
                })

        # Calculate metrics
        max_profit, max_loss, breakevens, profit_percentage = calculate_strategy_metrics(strategy, strategy_data)

        # Clear previous results
        for row in result_table.get_children():
            result_table.delete(row)

        # Display results in the table (مقدار سمت چپ، معیار سمت راست)
        result_table.insert("", "end", values=(to_persian_number(f"{int(max_profit)}" if max_profit != np.inf else "بینهایت"), "حداکثر سود"))
        result_table.insert("", "end", values=(to_persian_number(f"{int(max_loss)}"), "حداکثر ضرر"))
        result_table.insert("", "end", values=(to_persian_number(f"{profit_percentage:.2f}%" if profit_percentage != "بینهایت" else profit_percentage), "درصد سود"))

        # Display breakeven points
        if breakevens:
            for i, breakeven in enumerate(breakevens, start=1):
                result_table.insert("", "end", values=(to_persian_number(f"{int(breakeven)}"), f"نقطه سر به سر {i}"))

    except Exception as e:
        messagebox.showerror("خطا", f"خطایی رخ داده است: {str(e)}")

# Function to clear entries
def clear_entries():
    entry_market_price.delete(0, tk.END)
    for entry in input_elements.values():
        entry.delete(0, tk.END)
    for row in result_table.get_children():
        result_table.delete(row)

# Initialize main window
root = tk.Tk()
root.title("ماشین حساب استراتژی اختیار معامله")
root.geometry("400x500")  # کوچک‌تر کردن پنجره

# Apply Dark Mode
style = ttk.Style()
style.theme_use("clam")
style.configure(".", font=("B Nazanin", 12), background="#2d2d2d", foreground="#ffffff")
style.configure("TLabel", background="#2d2d2d", foreground="#ffffff")
style.configure("TButton", background="#444444", foreground="#ffffff")
style.configure("TEntry", fieldbackground="#444444", foreground="#ffffff")
style.configure("Treeview", background="#444444", foreground="#ffffff", fieldbackground="#444444")
style.map("Treeview", background=[("selected", "#666666")])

# Strategy selection
strategy_var = tk.StringVar(value="انتخاب استراتژی")  # تنظیم گزینه پیش‌فرض
strategy_label = tk.Label(root, text="استراتژی را انتخاب کنید:", font=("B Nazanin", 14))
strategy_label.pack(pady=10)
strategy_options = [
    "انتخاب استراتژی",  # اضافه کردن گزینه جدید
    "Covered Call",
    "Bull Call Spread",
    "Bear Call Spread",
    "Bull Put Spread",
    "Bear Put Spread",
    "Strangle",
    "Straddle",
    "Long Call",
    "Short Call",
    "Long Put",
    "Short Put",
]
strategy_menu = ttk.OptionMenu(root, strategy_var, *strategy_options)
strategy_menu.pack(pady=10)

# Input fields frame (زیر دراپ‌لیست استراتژی‌ها)
frame_inputs = tk.Frame(root, bg="#2d2d2d")
frame_inputs.pack(pady=10)

# Common inputs
label_market_price = tk.Label(frame_inputs, text="قیمت بازار:", font=("B Nazanin", 12), bg="#2d2d2d", fg="#ffffff")
label_market_price.grid(row=0, column=0, padx=10, pady=5)
entry_market_price = ttk.Entry(frame_inputs, font=("B Nazanin", 12))
entry_market_price.grid(row=0, column=1, padx=10, pady=5)

# Define input fields for each strategy dynamically
strategy_inputs = {
    "Straddle": [
        ("قیمت اعمال اختیار خرید:", "long_call_strike"),
        ("پرمیوم اختیار خرید:", "long_call_premium"),
        ("قیمت اعمال اختیار فروش:", "long_put_strike"),
        ("پرمیوم اختیار فروش:", "long_put_premium")
    ],
    "Bull Call Spread": [
        ("قیمت اعمال اختیار خریداری شده:", "long_call_strike"),
        ("پرمیوم اختیار خریداری شده:", "long_call_premium"),
        ("قیمت اعمال اختیار فروش رفته:", "short_call_strike"),
        ("پرمیوم اختیار فروش رفته:", "short_call_premium")
    ],
    "Bear Call Spread": [
        ("قیمت اعمال اختیار فروش رفته:", "short_call_strike"),
        ("پرمیوم اختیار فروش رفته:", "short_call_premium"),
        ("قیمت اعمال اختیار خریداری شده:", "long_call_strike"),
        ("پرمیوم اختیار خریداری شده:", "long_call_premium")
    ],
    "Bull Put Spread": [
        ("قیمت اعمال اختیار فروش رفته:", "short_put_strike"),
        ("پرمیوم اختیار فروش رفته:", "short_put_premium"),
        ("قیمت اعمال اختیار خریداری شده:", "long_put_strike"),
        ("پرمیوم اختیار خریداری شده:", "long_put_premium")
    ],
    "Bear Put Spread": [
        ("قیمت اعمال اختیار خریداری شده:", "long_put_strike"),
        ("پرمیوم اختیار خریداری شده:", "long_put_premium"),
        ("قیمت اعمال اختیار فروش رفته:", "short_put_strike"),
        ("پرمیوم اختیار فروش رفته:", "short_put_premium")
    ],
    "Strangle": [
        ("قیمت اعمال اختیار خرید خریداری شده:", "long_call_strike"),
        ("پرمیوم اختیار خرید خریداری شده:", "long_call_premium"),
        ("قیمت اعمال اختیار فروش خریداری شده:", "long_put_strike"),
        ("پرمیوم اختیار فروش خریداری شده:", "long_put_premium")
    ],
    "Long Call": [
        ("قیمت اعمال اختیار خریداری شده:", "long_call_strike"),
        ("پرمیوم اختیار خریداری شده:", "long_call_premium")
    ],
    "Short Call": [
        ("قیمت اعمال اختیار فروش رفته:", "short_call_strike"),
        ("پرمیوم اختیار فروش رفته:", "short_call_premium")
    ],
    "Long Put": [
        ("قیمت اعمال اختیار خریداری شده:", "long_put_strike"),
        ("پرمیوم اختیار خریداری شده:", "long_put_premium")
    ],
    "Short Put": [
        ("قیمت اعمال اختیار فروش رفته:", "short_put_strike"),
        ("پرمیوم اختیار فروش رفته:", "short_put_premium")
    ],
    "Covered Call": [
        ("قیمت اعمال اختیار فروش رفته:", "short_call_strike"),
        ("پرمیوم اختیار فروش رفته:", "short_call_premium")
    ]
}

# Input elements storage for dynamic removal and addition
input_elements = {}

def show_strategy_inputs(*args):
    for widget in frame_inputs.winfo_children():
        widget.grid_forget()

    # اگر گزینه "انتخاب استراتژی" انتخاب شده باشد، هیچ فیلدی نمایش داده نشود
    if strategy_var.get() == "انتخاب استراتژی":
        return

    label_market_price.grid(row=0, column=0, padx=10, pady=5)
    entry_market_price.grid(row=0, column=1, padx=10, pady=5)

    strategy = strategy_var.get()
    row = 1
    input_elements.clear()
    for label_text, var_name in strategy_inputs.get(strategy, []):
        label = tk.Label(frame_inputs, text=label_text, font=("B Nazanin", 12), bg="#2d2d2d", fg="#ffffff")
        label.grid(row=row, column=0, padx=10, pady=5)
        entry = ttk.Entry(frame_inputs, font=("B Nazanin", 12))
        entry.grid(row=row, column=1, padx=10, pady=5)
        input_elements[var_name] = entry
        row += 1

# Trace strategy selection changes
strategy_var.trace("w", show_strategy_inputs)

# Initialize inputs
show_strategy_inputs()

# Result table
result_table = ttk.Treeview(root, columns=("Value", "Metric"), show="headings", style="Treeview")
result_table.heading("Value", text="مقدار")
result_table.heading("Metric", text="معیار")
result_table.pack(pady=10)

# Buttons frame
buttons_frame = tk.Frame(root, bg="#2d2d2d")
buttons_frame.pack(pady=10)

# Calculate button
calculate_button = ttk.Button(buttons_frame, text="محاسبه", command=calculate_strategy)
calculate_button.grid(row=0, column=0, padx=5)

# Clear button
clear_button = ttk.Button(buttons_frame, text="حذف نوشته‌ها", command=clear_entries)
clear_button.grid(row=0, column=1, padx=5)

root.mainloop()