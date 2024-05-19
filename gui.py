import tkinter as tk
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from tkinter import ttk
from decimal import Decimal
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from app import LoanManager, Plotter

# TODO
# Data validation for EVERYTHING
# Add more typing hints


class InfoFrame(ttk.Frame):
    """
    Frame that displays the loan information in a table like view
    Has buttons to add, edit and delete loans that creates a popup window
    """

    def __init__(self, parent, loan_manager, refresh_callback=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.loan_manager = loan_manager
        self.refresh_callback = refresh_callback
        self.draw()

    def draw(self):
        ttk.Button(
            self, text="New Loan",
            command=lambda i: self.open_loan_popup(None),
            bootstyle="primary"
        ).grid(row=0, column=0, sticky='ew', pady=10, padx=20, columnspan=6)
        # Draw header
        ttk.Label(self, text="Loan").grid(
            row=1, column=0, padx=20, pady=10, sticky='n')
        ttk.Label(self, text="Principal").grid(
            row=1, column=1, padx=20, pady=10, sticky='n')
        ttk.Label(self, text="Rate").grid(
            row=1, column=2, padx=20, pady=10, sticky='n')
        ttk.Label(self, text="Minimum Payment").grid(
            row=1, column=3, padx=20, pady=10, sticky='n')
        # Draw each net loan info
        for i, loan in enumerate(self.loan_manager.loans):
            ttk.Label(self, text=f"{loan.name}").grid(
                row=i+2, column=0, padx=20, pady=10, sticky='n')
            ttk.Label(self, text=f"${loan.principal:.2f}").grid(
                row=i+2, column=1, padx=20, pady=10, sticky='n')
            ttk.Label(self, text=f"{loan.rate*100:.2f}%").grid(
                row=i+2, column=2, padx=20, pady=10, sticky='n')
            ttk.Label(self, text=f"${loan.min_pmt:.2f}").grid(
                row=i+2, column=3, padx=20, pady=10, sticky='n')
            ttk.Button(self, text="Edit", command=lambda i=i: self.open_loan_popup(
                i), bootstyle="warning").grid(row=i+2, column=4, padx=20, pady=10)
            ttk.Button(self, text="Delete", command=lambda i=i: self.delete_loan(
                i), bootstyle="danger").grid(row=i+2, column=5, padx=20, pady=10)

    def open_loan_popup(self, index):
        """Opens a popup window to edit the loan at the given index"""
        PopupWindow(self, self.loan_manager, index,
                    refresh_callback=self.refresh_callback)

    def delete_loan(self, index):
        """Deletes the loan at the given index then refreshes the frame"""
        self.loan_manager.delete_loan(index)
        # Calls the refresh callback, will eventually calls our own refresh too
        if self.refresh_callback:
            self.refresh_callback()

    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()

    def refresh(self):
        self.clear()
        self.draw()


class PopupWindow(ttk.Toplevel):
    def __init__(self, parent, loan_manager, index=None, refresh_callback=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.loan_manager = loan_manager
        self.index = index
        self.refresh_callback = refresh_callback
        self.popup = ttk.Frame(self)
        self.popup.grid(row=0, column=0, sticky='nsew')
        self.title("Edit Loan" if self.index is not None else "New Loan")
        self.draw()

    def draw(self):
        ttk.Label(self.popup, text="Name").grid(
            row=0, column=0, pady=10, padx=10, sticky='nw')
        self.name_var = ttk.StringVar(
            value=self.loan_manager.loans[self.index].name if self.index is not None else "")
        ttk.Entry(self.popup, textvariable=self.name_var, width=30).grid(
            row=0, column=1, pady=10, padx=10, sticky='n')

        ttk.Label(self.popup, text="Principal Balance").grid(
            row=1, column=0, sticky='nw', pady=10, padx=10)
        self.principal_var = ttk.DoubleVar(
            value=self.loan_manager.loans[self.index].principal if self.index is not None else 0)
        ttk.Entry(self.popup, textvariable=self.principal_var, width=30).grid(
            row=1, column=1, pady=10, padx=10, sticky='n')
        principal_slider = ttk.Scale(
            self.popup, from_=0, to=100000, orient=ttk.HORIZONTAL, variable=self.principal_var,
            length=500, command=lambda x: self.principal_var.set(round(self.principal_var.get(), -3)))
        principal_slider.grid(row=1, column=2, pady=10, padx=10, sticky='e')

        ttk.Label(self.popup, text="Interest Rate (%)").grid(
            row=2, column=0, sticky='nw', pady=10, padx=10)
        self.interest_var = ttk.DoubleVar(
            value=self.loan_manager.loans[self.index].rate*100 if self.index is not None else 0)
        ttk.Entry(self.popup, textvariable=self.interest_var, width=30).grid(
            row=2, column=1, pady=10, padx=10, sticky='n')
        interest_slider = ttk.Scale(
            self.popup, from_=0, to=20, orient=ttk.HORIZONTAL, variable=self.interest_var, length=500,
            command=lambda x: self.interest_var.set(round(self.interest_var.get(), 1)))
        interest_slider.grid(row=2, column=2, pady=10, padx=10, sticky='e')

        ttk.Label(self.popup, text="Minimum Payment").grid(
            row=3, column=0, sticky='nw', pady=10, padx=10)
        self.min_payment_var = ttk.DoubleVar(
            value=self.loan_manager.loans[self.index].min_pmt if self.index is not None else 0)
        ttk.Entry(self.popup, textvariable=self.min_payment_var, width=30).grid(
            row=3, column=1, pady=10, padx=10, sticky='n')
        ttk.Button(self.popup, text="Save", command=self.save_loan, bootstyle="success").grid(
            row=4, column=0, pady=10)

    def save_loan(self):
        name = self.name_var.get()
        principal = self.principal_var.get()
        interest = self.interest_var.get()
        min_payment = self.min_payment_var.get()
        if self.index is not None:
            self.loan_manager.update_loan(
                self.index, name, Decimal(str(round(principal, 2))), Decimal(str(round(interest)))/100, Decimal(str(round(min_payment, 2))))
        else:
            self.loan_manager.add_loan(
                name, Decimal(str(principal)), Decimal(str(interest))/100, Decimal(str(min_payment)))
        if self.refresh_callback:
            self.refresh_callback()
        super().destroy()


class PaymentFrame(ttk.Frame):
    def __init__(self, parent, loan_manager, refresh_callback=None, *args, **kwargs):
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


class LoanApp(ttk.Window):
    def __init__(self):
        super().__init__(title="Loan Manager")
        self.style.configure("TLabel", font=("Arial", 14))
        self.style.configure("TButton", font=("Arial", 14))

        # Initialize loan manager and plotter
        try:
            self.loan_manager = LoanManager.read_from_file()
        except FileNotFoundError:
            self.loan_manager = LoanManager()
        self.plotter = Plotter()

        # Create the info frame and place it on the grid
        self.info_frame = InfoFrame(self, self.loan_manager, self.refresh)
        self.info_frame.grid(row=1, column=0, sticky='nsew')

        # Income plotter
        self.payment_frame = PaymentFrame(
            self, self.loan_manager, self.refresh)
        self.payment_frame.grid(row=1, column=1, sticky='nsew')

        # Create the frame that will hold the plot
        self.plot_frame = ttk.Frame(self)
        self.canvas = FigureCanvasTkAgg(self.plotter.fig, self.plot_frame)
        toolbar = NavigationToolbar2Tk(
            self.canvas, self.plot_frame, pack_toolbar=False)
        toolbar.update()
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        toolbar.grid(row=1, column=0, sticky="nsew")
        self.plot_frame.grid(row=2, column=0, columnspan=2, sticky='nsew')

        # Draw the initial state
        self.refresh()

    def refresh(self):
        self.loan_manager.save_to_file()
        self.info_frame.refresh()
        self.payment_frame.refresh()
        self.plotter.refresh(self.loan_manager.loan_df)
        self.canvas.draw()


def main():
    ttk.utility.enable_high_dpi_awareness()
    app = LoanApp()
    app.mainloop()


if __name__ == "__main__":
    main()
