import tkinter as tk
from ttkbootstrap import Style
from ttkbootstrap.widgets import Frame, Button, Label, Entry, Scale
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from app import LoanManager, Plotter

# TODO
# Add a method to edit the payment bands
# Add interactivity by adding manual payments in specific months
# Round values from sliders to 2 decimal places


class LoanApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Loan Visualizer")
        root.tk.call('tk', 'scaling', 2.0)

        # Configure the main frame to adjust the rows and columns proportionately
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Set the style for the application
        self.style = Style('superhero')

        # Initialize loan manager and plotter
        try:
            self.loan_manager = LoanManager.read_from_file("loans.csv")
        except FileNotFoundError:
            self.loan_manager = LoanManager()
        self.plotter = Plotter()

        # Create the main frame
        self.main_frame = Frame(root)
        self.main_frame.grid(row=0, column=0, sticky='nsew')

        # Create the new loan button
        self.new_loan_button = Button(
            self.main_frame, text="New Loan", command=self.open_loan_popup, bootstyle="primary")
        self.new_loan_button.grid(row=0, column=0, pady=10, sticky='n')

        # Create the frame where current loans info is displayed
        self.loans_frame = Frame(self.main_frame)
        self.loans_frame.grid(row=1, column=0, sticky='n')

        # Create the frame where the actual plot is displayed
        self.plot_frame = Frame(self.main_frame)
        self.plot_frame.grid(row=2, column=0, sticky='n')
        self.canvas = FigureCanvasTkAgg(self.plotter.fig, self.plot_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0)

        # Draw the initial state
        self.refresh()

    def refresh(self):
        # Delete current loan info and redraw
        for widget in self.loans_frame.winfo_children():
            widget.destroy()
        # Draw header
        Label(self.loans_frame, text="Loan").grid(
            row=0, column=0, padx=20, pady=10, sticky='n')
        Label(self.loans_frame, text="Principal").grid(
            row=0, column=1, padx=20, pady=10, sticky='n')
        Label(self.loans_frame, text="Rate").grid(
            row=0, column=2, padx=20, pady=10, sticky='n')
        Label(self.loans_frame, text="Minimum Payment").grid(
            row=0, column=3, padx=20, pady=10, sticky='n')
        # Draw each net loan info
        for i, loan in enumerate(self.loan_manager.loans):
            Label(self.loans_frame, text=f"{loan.name}").grid(
                row=i+1, column=0, padx=20, pady=10, sticky='n')
            Label(self.loans_frame, text=f"${loan.principal:.2f}").grid(
                row=i+1, column=1, padx=20, pady=10, sticky='n')
            Label(self.loans_frame, text=f"{loan.rate*100:.2f}%").grid(
                row=i+1, column=2, padx=20, pady=10, sticky='n')
            Label(self.loans_frame, text=f"${loan.min_pmt:.2f}").grid(
                row=i+1, column=3, padx=20, pady=10, sticky='n')
            Button(self.loans_frame, text="Edit", command=lambda i=i: self.open_loan_popup(
                i), bootstyle="warning").grid(row=i+1, column=4, padx=20, pady=10)
            Button(self.loans_frame, text="Delete", command=lambda i=i: self.delete_loan(
                i), bootstyle="danger").grid(row=i+1, column=5, padx=20, pady=10)
        self.loan_manager.save_to_file("loans.csv")
        self.plotter.refresh_figure(self.loan_manager.loan_df)
        self.canvas.draw()

    def delete_loan(self, index):
        self.loan_manager.delete_loan(index)
        self.refresh()

    def open_loan_popup(self, index=None):
        popup = tk.Toplevel(self.root)
        popup.title("Edit Loan" if index is not None else "New Loan")

        frame = Frame(popup, padding="5 5 5 5")
        frame.grid(row=0, column=0, sticky="nsew")

        Label(frame, text="Name").grid(
            row=0, column=0, pady=10, padx=10, sticky='nw')
        name_var = tk.StringVar(
            value=self.loan_manager.loans[index].name if index is not None else "")
        Entry(frame, textvariable=name_var, width=20).grid(
            row=0, column=1, pady=10, padx=10, sticky='n')

        Label(frame, text="Principal Balance").grid(
            row=1, column=0, sticky='nw', pady=10, padx=10)
        principal_var = tk.DoubleVar(
            value=self.loan_manager.loans[index].principal if index is not None else 0)
        Entry(frame, textvariable=principal_var, width=20).grid(
            row=1, column=1, pady=10, padx=10, sticky='n')
        principal_slider = Scale(
            frame, from_=0, to=100000, orient=tk.HORIZONTAL, variable=principal_var,
            length=300, command=lambda x: principal_var.set(round(principal_var.get()/10)*10))
        principal_slider.grid(row=1, column=2, pady=10, padx=10, sticky='e')

        Label(frame, text="Interest Rate (%)").grid(
            row=2, column=0, sticky='nw', pady=10, padx=10)
        interest_var = tk.DoubleVar(
            value=self.loan_manager.loans[index].rate*100 if index is not None else 0)
        Entry(frame, textvariable=interest_var, width=20).grid(
            row=2, column=1, pady=10, padx=10, sticky='n')
        interest_slider = Scale(
            frame, from_=0, to=30, orient=tk.HORIZONTAL, variable=interest_var, length=300,
            command=lambda x: interest_var.set(round(interest_var.get(), 1)))
        interest_slider.grid(row=2, column=2, pady=10, padx=10, sticky='e')

        Label(frame, text="Minimum Payment").grid(
            row=3, column=0, sticky='nw', pady=10, padx=10)
        min_payment_var = tk.DoubleVar(
            value=self.loan_manager.loans[index].min_pmt if index is not None else 0)
        Entry(frame, textvariable=min_payment_var, width=20).grid(
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

        Button(frame, text="Save", command=save_loan, bootstyle="success").grid(
            row=4, column=0, pady=10)


def main():
    root = tk.Tk()
    app = LoanApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
