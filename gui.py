import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from app import LoansManager, Plotter


class LoanApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Loan Visualizer")
        root.tk.call('tk', 'scaling', 2.0)

        # Set the style for the application
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TButton', background='#5c85d6',
                             foreground='white', font=('Arial', 16, 'bold'))
        self.style.map('TButton', background=[('active', '#3b5c8c')])
        self.style.configure(
            'TLabel', background='#f0f0f0', font=('Arial', 16))
        self.style.configure('TEntry')
        self.style.configure('TScale', background='#f0f0f0')

        try:
            self.loans_manager = LoansManager.read_from_file("loans.csv")
        except FileNotFoundError:
            self.loans_manager = LoansManager()

        self.plotter = Plotter()

        self.main_frame = ttk.Frame(root)
        self.main_frame.grid(row=0, column=0, sticky='nsew')

        self.new_loan_button = ttk.Button(
            self.main_frame, text="New Loan", command=self.open_loan_popup)
        self.new_loan_button.grid(row=0, column=0, pady=10, sticky='n')

        self.loans_frame = ttk.Frame(self.main_frame)
        self.loans_frame.grid(row=1, column=0, sticky='nsew')

        self.plot_frame = ttk.Frame(self.main_frame)
        self.plot_frame.grid(row=2, column=0, sticky='nsew')
        self.canvas = FigureCanvasTkAgg(self.plotter.fig, self.plot_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')

        # Configure the main frame to adjust the rows and columns proportionately
        self.root.columnconfigure(0, weight=1, minsize=800)
        self.root.rowconfigure(0, weight=1, minsize=800)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=0)  # Button row
        self.main_frame.rowconfigure(1, weight=1)  # Loans list row
        self.main_frame.rowconfigure(2, weight=3)  # Plot row

        self.refresh()

    def refresh(self):
        for widget in self.loans_frame.winfo_children():
            widget.destroy()
        for i, loan in enumerate(self.loans_manager.loans):
            ttk.Label(self.loans_frame, text=f"{loan.name}").grid(
                row=i, column=0, padx=5, pady=5, sticky='n')
            ttk.Label(self.loans_frame, text=f"${loan.principal:.2f}").grid(
                row=i, column=1, padx=5, pady=5, sticky='n')
            ttk.Label(self.loans_frame, text=f"{loan.rate:.2f}%").grid(
                row=i, column=2, padx=5, pady=5, sticky='n')
            ttk.Label(self.loans_frame, text=f"${loan.min_pmt:.2f}").grid(
                row=i, column=3, padx=5, pady=5, sticky='n')
            ttk.Button(self.loans_frame, text="Edit", command=lambda i=i: self.open_loan_popup(
                i)).grid(row=i, column=4, padx=5, pady=5)
            ttk.Button(self.loans_frame, text="Delete", command=lambda i=i: self.delete_loan(
                i)).grid(row=i, column=5, padx=5, pady=5)
        self.loans_manager.save_to_file("loans.csv")
        self.plotter.update_fig(self.loans_manager.loan_df)
        self.canvas.draw()

    def delete_loan(self, index):
        self.loans_manager.delete_loan(index)
        self.refresh()

    def open_loan_popup(self, index=None):
        popup = tk.Toplevel(self.root)
        popup.title("Edit Loan" if index is not None else "New Loan")

        frame = ttk.Frame(popup, padding="5 5 5 5")
        frame.grid(row=0, column=0, sticky="nsew")

        ttk.Label(frame, text="Name").grid(row=0, column=0, sticky='w', pady=5)
        name_var = tk.StringVar(
            value=self.loans_manager.loans[index].name if index is not None else "")
        ttk.Entry(frame, textvariable=name_var, width=60).grid(
            row=0, column=1, pady=5)

        ttk.Label(frame, text="Principal Balance").grid(
            row=1, column=0, sticky='w', pady=5)
        principal_var = tk.DoubleVar(
            value=self.loans_manager.loans[index].principal if index is not None else 0)
        ttk.Entry(frame, textvariable=principal_var,
                  width=40).grid(row=1, column=1, pady=5)
        principal_slider = ttk.Scale(
            frame, from_=0, to=100000, orient=tk.HORIZONTAL, variable=principal_var)
        principal_slider.grid(row=1, column=2, pady=2, padx=2, sticky='we')

        ttk.Label(frame, text="Interest Rate (%)").grid(
            row=2, column=0, sticky='w', pady=5)
        interest_var = tk.DoubleVar(
            value=self.loans_manager.loans[index].rate*100 if index is not None else 0)
        ttk.Entry(frame, textvariable=interest_var,
                  width=40).grid(row=2, column=1, pady=5)
        interest_slider = ttk.Scale(
            frame, from_=0, to=30, orient=tk.HORIZONTAL, variable=interest_var)
        interest_slider.grid(row=2, column=2, pady=2, padx=2, sticky='we')

        ttk.Label(frame, text="Minimum Payment").grid(
            row=3, column=0, sticky='w', pady=5)
        min_payment_var = tk.DoubleVar(
            value=self.loans_manager.loans[index].min_pmt if index is not None else 0)
        ttk.Entry(frame, textvariable=min_payment_var,
                  width=40).grid(row=3, column=1, pady=5)

        def save_loan():
            name = name_var.get()
            principal = principal_var.get()
            interest = interest_var.get()/100.0
            min_payment = min_payment_var.get()
            if index is not None:
                self.loans_manager.update_loan(
                    index, name, principal, interest, min_payment)
            else:
                self.loans_manager.add_loan(
                    name, principal, interest, min_payment)
            self.refresh()
            popup.destroy()

        ttk.Button(frame, text="Save", command=save_loan).grid(
            row=4, column=0, columnspan=3, pady=1)


def main():
    root = tk.Tk()
    app = LoanApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
