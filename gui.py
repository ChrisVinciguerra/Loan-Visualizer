from decimal import Decimal
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from app import LoanManager, Plotter

# TODO
# Add a method to edit the payment bands
# Add interactivity by adding manual payments in specific months
# Round values from sliders to 2 decimal places


class InfoFrame(ttk.Frame):
    """
    Frame that displays the loan information in a table like view
    Has buttons to edit and delete loans that creates a popup window
    """

    def __init__(self, parent, loan_manager, refresh_callback=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.loan_manager = loan_manager
        self.refresh_callback = refresh_callback
        self.draw()

    def draw(self):
        # Draw header
        ttk.Label(self, text="Loan").grid(
            row=0, column=0, padx=20, pady=10, sticky='n')
        ttk.Label(self, text="Principal").grid(
            row=0, column=1, padx=20, pady=10, sticky='n')
        ttk.Label(self, text="Rate").grid(
            row=0, column=2, padx=20, pady=10, sticky='n')
        ttk.Label(self, text="Minimum Payment").grid(
            row=0, column=3, padx=20, pady=10, sticky='n')
        # Draw each net loan info
        for i, loan in enumerate(self.loan_manager.loans):
            ttk.Label(self, text=f"{loan.name}").grid(
                row=i+1, column=0, padx=20, pady=10, sticky='n')
            ttk.Label(self, text=f"${loan.principal:.2f}").grid(
                row=i+1, column=1, padx=20, pady=10, sticky='n')
            ttk.Label(self, text=f"{loan.rate*100:.2f}%").grid(
                row=i+1, column=2, padx=20, pady=10, sticky='n')
            ttk.Label(self, text=f"${loan.min_pmt:.2f}").grid(
                row=i+1, column=3, padx=20, pady=10, sticky='n')
            ttk.Button(self, text="Edit", command=lambda i=i: self.open_loan_popup(
                i), bootstyle="warning").grid(row=i+1, column=4, padx=20, pady=10)
            ttk.Button(self, text="Delete", command=lambda i=i: self.delete_loan(
                i), bootstyle="danger").grid(row=i+1, column=5, padx=20, pady=10)

    def open_loan_popup(self, index):
        """Opens a popup window to edit the loan at the given index"""
        PopupWindow(self, self.loan_manager, index,
                    refresh_callback=self.refresh_callback)

    def delete_loan(self, index):
        """Deletes the loan at the given index then refreshes the frame"""
        self.loan_manager.delete_loan(index)
        # Calls the refresh callback, will eventually calls our own refresh too
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
        self.draw()

    def draw(self):
        self.popup.grid(row=0, column=0, sticky='nsew')
        self.title("Edit Loan" if self.index is not None else "New Loan")

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
        self.refresh_callback()
        super().destroy()

    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()

    def refresh(self):
        self.clear()
        self.draw()


class LoanApp(ttk.Window):
    def __init__(self):
        super().__init__(title="Loan Manager")
        self.style.configure("TLabel", font=("Arial", 14))
        self.style.configure("TButton", font=("Arial", 14))

        # Initialize loan manager and plotter
        try:
            self.loan_manager = LoanManager.read_from_file("loans.csv")
        except FileNotFoundError:
            self.loan_manager = LoanManager()
        self.plotter = Plotter()

        # Create the new loan button
        self.new_loan_button = ttk.Button(
            self, text="New Loan", command=lambda: PopupWindow(self, self.loan_manager, refresh_callback=self.refresh), bootstyle="primary")
        self.new_loan_button.grid(row=0, column=0, pady=10, sticky='n')

        # Create the info frame and place it on the grid
        self.info_frame = InfoFrame(self, self.loan_manager, self.refresh)
        self.info_frame.grid(row=1, column=0, pady=10, sticky='n')

        # Create the frame that will hold the plot
        self.canvas = FigureCanvasTkAgg(self.plotter.fig, self)
        self.canvas.get_tk_widget().grid(row=2, column=0, sticky='new')

        # Draw the initial state
        self.refresh()

    def refresh(self):
        self.loan_manager.save_to_file("loans.csv")
        self.info_frame.refresh()
        self.plotter.refresh(self.loan_manager.loan_df)
        self.canvas.draw()
        print(self.loan_manager)


def main():
    ttk.utility.enable_high_dpi_awareness()
    app = LoanApp()
    app.mainloop()


if __name__ == "__main__":
    main()
