import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from app import LoanManager, Plotter

# TODO
# Add a method to edit the payment bands
# Add interactivity by adding manual payments in specific months
# Round values from sliders to 2 decimal places


class LoanApp:
    def __init__(self):
        ttk.utility.enable_high_dpi_awareness()
        self.root = ttk.Window(title="Loan Visualizer")
        self.style = ttk.Style("cosmo")
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
            self.root, text="New Loan", command=self.open_loan_popup, bootstyle="primary")
        self.new_loan_button.grid(row=0, column=0, pady=10, sticky='n')

        # Create the frame where current loans info is displayed
        self.loan_info_frame = ttk.Frame(self.root)
        self.loan_info_frame.grid(row=1, column=0, pady=10, sticky='n')

        # Create the frame where the actual plot is displayed
        self.canvas = FigureCanvasTkAgg(self.plotter.fig, self.root)
        self.canvas.get_tk_widget().grid(row=2, column=0, sticky='new')

        # Draw the initial state
        self.refresh()

    def refresh(self):
        # Redraw the loans info frame
        for widget in self.loan_info_frame.winfo_children():
            widget.destroy()
        # Draw header
        ttk.Label(self.loan_info_frame, text="Loan").grid(
            row=0, column=0, padx=20, pady=10, sticky='n')
        ttk.Label(self.loan_info_frame, text="Principal").grid(
            row=0, column=1, padx=20, pady=10, sticky='n')
        ttk.Label(self.loan_info_frame, text="Rate").grid(
            row=0, column=2, padx=20, pady=10, sticky='n')
        ttk.Label(self.loan_info_frame, text="Minimum Payment").grid(
            row=0, column=3, padx=20, pady=10, sticky='n')
        # Draw each net loan info
        for i, loan in enumerate(self.loan_manager.loans):
            ttk.Label(self.loan_info_frame, text=f"{loan.name}").grid(
                row=i+1, column=0, padx=20, pady=10, sticky='n')
            ttk.Label(self.loan_info_frame, text=f"${loan.principal:.2f}").grid(
                row=i+1, column=1, padx=20, pady=10, sticky='n')
            ttk.Label(self.loan_info_frame, text=f"{loan.rate*100:.2f}%").grid(
                row=i+1, column=2, padx=20, pady=10, sticky='n')
            ttk.Label(self.loan_info_frame, text=f"${loan.min_pmt:.2f}").grid(
                row=i+1, column=3, padx=20, pady=10, sticky='n')
            ttk.Button(self.loan_info_frame, text="Edit", command=lambda i=i: self.open_loan_popup(
                i), bootstyle="warning").grid(row=i+1, column=4, padx=20, pady=10)
            ttk.Button(self.loan_info_frame, text="Delete", command=lambda i=i: self.delete_loan(
                i), bootstyle="danger").grid(row=i+1, column=5, padx=20, pady=10)
        self.loan_manager.save_to_file("loans.csv")
        self.plotter.refresh_figure(self.loan_manager.loan_df)
        # self.canvas.draw()

    def delete_loan(self, index):
        self.loan_manager.delete_loan(index)
        self.refresh()

    def open_loan_popup(self, index=None):
        popup = ttk.Toplevel(self.root).grid(row=0, column=0, sticky='nsew')
        popup.title("Edit Loan" if index is not None else "New Loan")

        ttk.Label(popup, text="Name").grid(
            row=0, column=0, pady=10, padx=10, sticky='nw')
        name_var = ttk.StringVar(
            value=self.loan_manager.loans[index].name if index is not None else "")
        ttk.Entry(popup, textvariable=name_var, width=20).grid(
            row=0, column=1, pady=10, padx=10, sticky='n')

        ttk.Label(popup, text="Principal Balance").grid(
            row=1, column=0, sticky='nw', pady=10, padx=10)
        principal_var = ttk.DoubleVar(
            value=self.loan_manager.loans[index].principal if index is not None else 0)
        ttk.Entry(popup, textvariable=principal_var, width=20).grid(
            row=1, column=1, pady=10, padx=10, sticky='n')
        principal_slider = ttk.Scale(
            popup, from_=0, to=100000, orient=ttk.HORIZONTAL, variable=principal_var,
            length=300, command=lambda x: principal_var.set(round(principal_var.get()/10)*10))
        principal_slider.grid(row=1, column=2, pady=10, padx=10, sticky='e')

        ttk.Label(popup, text="Interest Rate (%)").grid(
            row=2, column=0, sticky='nw', pady=10, padx=10)
        interest_var = ttk.DoubleVar(
            value=self.loan_manager.loans[index].rate*100 if index is not None else 0)
        ttk.Entry(popup, textvariable=interest_var, width=20).grid(
            row=2, column=1, pady=10, padx=10, sticky='n')
        interest_slider = ttk.Scale(
            popup, from_=0, to=30, orient=ttk.HORIZONTAL, variable=interest_var, length=300,
            command=lambda x: interest_var.set(round(interest_var.get(), 1)))
        interest_slider.grid(row=2, column=2, pady=10, padx=10, sticky='e')

        ttk.Label(popup, text="Minimum Payment").grid(
            row=3, column=0, sticky='nw', pady=10, padx=10)
        min_payment_var = ttk.DoubleVar(
            value=self.loan_manager.loans[index].min_pmt if index is not None else 0)
        ttk.Entry(popup, textvariable=min_payment_var, width=20).grid(
            row=3, column=1, pady=10, padx=10, sticky='n')

        def save_loan():
            name = name_var.get()
            principal = principal_var.get()
            interest = interest_var.get()/100.0
            min_payment = min_payment_var.get()
            if index is not None:
                self.loan_manager.update_loan(
                    index, name, principal, interest, min_payment)
            else:
                self.loan_manager.add_loan(
                    name, principal, interest, min_payment)
            self.refresh()
            popup.destroy()

        ttk.Button(popup, text="Save", command=save_loan, bootstyle="success").grid(
            row=4, column=0, pady=10)


def main():
    app = LoanApp()
    app.root.mainloop()


if __name__ == "__main__":
    main()
