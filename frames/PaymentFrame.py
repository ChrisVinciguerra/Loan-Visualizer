from decimal import Decimal
from matplotlib import pyplot as plt
import ttkbootstrap as ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from loan import LoanManager


class PaymentFrame(ttk.Frame):
    def __init__(self, parent, loan_manager: LoanManager, refresh_callback, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.loan_manager = loan_manager
        self.refresh_callback = refresh_callback

        # Matplotlib Figure and Axis
        self.fig, self.ax = plt.subplots(figsize=(6, 2))
        self.fig.set_tight_layout(True)

        # Entry subframe for manual entry
        self.entry_frame = ttk.Frame(self)
        self.entry_frame.grid(row=0, column=0, sticky='')

        # Canvas for Matplotlib Figure
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().grid(row=1, column=0, sticky='')
        self.canvas.mpl_connect("button_press_event", self.on_click)

        # Current selected month for update or delete
        self.selected_month = None

        # Draw the initial plot and UI
        self.draw()

    def clear(self):
        for widget in self.entry_frame.winfo_children():
            widget.destroy()
        self.ax.clear()

    def refresh(self):
        self.clear()
        self.draw()

    def draw(self):
        ttk.Label(self.entry_frame, text="Month:",).grid(
            row=0, column=0, sticky='nsew', padx=10, pady=10)
        self.month_entry = ttk.Entry(
            self.entry_frame, width=8, font=("Arial", 14))
        self.month_entry.insert(0, str(self.selected_month))
        self.month_entry.grid(row=0, column=1, sticky='nsew', padx=10, pady=10)

        ttk.Label(self.entry_frame, text="Income:").grid(
            row=0, column=2, sticky='nsew', padx=10, pady=10)
        self.payment_entry = ttk.Entry(
            self.entry_frame, width=12, font=("Arial", 14))
        self.payment_entry.insert(
            0, self.loan_manager.find_payment_amount(self.selected_month) if self.selected_month is not None else "")
        self.payment_entry.grid(
            row=0, column=3, sticky='nsew', padx=10, pady=10)

        self.set_button = ttk.Button(
            self.entry_frame, text="Set Income", command=self.set_income)
        self.set_button.grid(row=0, column=5, sticky='nsew', padx=10, pady=10)

        self.delete_button = ttk.Button(
            self.entry_frame, text="Delete Step", command=self.delete_step)
        self.delete_button.grid(
            row=0, column=6, sticky='nsew', padx=10, pady=10)
        # Draw the plot
        months, incomes = zip(*
                              sorted(self.loan_manager.payment_bands.items(), key=lambda x: x[0]))
        self.ax.step(months, incomes, where='post', color='red')
        # Indicate steps with dots
        self.ax.scatter(months, incomes, color='red')
        if self.selected_month is not None:
            self.ax.scatter([self.selected_month], [float(self.loan_manager.find_payment_amount(
                self.selected_month))], color='blue', s=100, zorder=10)
        self.ax.set_xlabel('Month')
        max_x = max(self.loan_manager.loan_df["Month"].max(), max(
            self.loan_manager.payment_bands))
        self.ax.set_xbound(0, max_x)
        self.ax.set_xticks(range(0, max_x+1), minor=True)
        self.ax.set_ybound(Decimal(".5") * min(self.loan_manager.payment_bands.values()),
                           max(self.loan_manager.payment_bands.values())*Decimal("1.2"))
        self.ax.set_ylabel('Income ($)')
        self.canvas.draw()

    def on_click(self, event):
        if event.inaxes is None:
            return
        self.selected_month = int(event.xdata)
        self.refresh()

    def set_income(self):
        month = int(self.month_entry.get())
        income = Decimal(self.payment_entry.get())
        self.loan_manager.add_payment_band(month, income)
        self.selected_month = None
        if self.refresh_callback:
            self.refresh_callback()

    def delete_step(self):
        self.loan_manager.delete_payment_band(self.selected_month)
        self.selected_month = None
        if self.refresh_callback:
            self.refresh_callback()
