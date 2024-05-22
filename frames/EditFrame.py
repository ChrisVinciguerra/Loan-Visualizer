from decimal import Decimal
import ttkbootstrap as ttk

from loan import LoanManager


class EditFrame(ttk.Frame):
    def __init__(self, parent, loan_manager: LoanManager, index, refresh_callback, **kwargs):
        super().__init__(parent, **kwargs)
        self.loan_manager = loan_manager
        self.index = index
        self.refresh_callback = refresh_callback
        self.draw()

    def draw(self):
        ttk.Label(self, text="Name").grid(
            row=0, column=0, pady=10, padx=10, sticky='nw')
        self.name_var = ttk.StringVar(
            value=self.loan_manager.loans[self.index].name if self.index is not None else "")
        ttk.Entry(self, textvariable=self.name_var, width=30).grid(
            row=0, column=1, pady=10, padx=10, sticky='n')

        ttk.Label(self, text="Principal Balance").grid(
            row=1, column=0, sticky='nw', pady=10, padx=10)
        self.principal_var = ttk.DoubleVar(
            value=self.loan_manager.loans[self.index].principal if self.index is not None else 0)
        ttk.Entry(self, textvariable=self.principal_var, width=30).grid(
            row=1, column=1, pady=10, padx=10, sticky='n')
        principal_slider = ttk.Scale(
            self, from_=0, to=100000, orient=ttk.HORIZONTAL, variable=self.principal_var,
            length=500, command=lambda x: self.principal_var.set(round(self.principal_var.get(), -3)))
        principal_slider.grid(row=1, column=2, pady=10, padx=10, sticky='e')

        ttk.Label(self, text="Interest Rate (%)").grid(
            row=2, column=0, sticky='nw', pady=10, padx=10)
        self.interest_var = ttk.DoubleVar(
            value=self.loan_manager.loans[self.index].rate*100 if self.index is not None else 0)
        ttk.Entry(self, textvariable=self.interest_var, width=30).grid(
            row=2, column=1, pady=10, padx=10, sticky='n')
        interest_slider = ttk.Scale(
            self, from_=0, to=20, orient=ttk.HORIZONTAL, variable=self.interest_var, length=500,
            command=lambda x: self.interest_var.set(round(self.interest_var.get(), 2)))
        interest_slider.grid(row=2, column=2, pady=10, padx=10, sticky='e')

        ttk.Label(self, text="Minimum Payment").grid(
            row=3, column=0, sticky='nw', pady=10, padx=10)
        self.min_payment_var = ttk.DoubleVar(
            value=self.loan_manager.loans[self.index].min_pmt if self.index is not None else 0)
        ttk.Entry(self, textvariable=self.min_payment_var, width=30).grid(
            row=3, column=1, pady=10, padx=10, sticky='n')
        ttk.Button(self, text="Save", command=self._save_loan, bootstyle="success").grid(
            row=4, column=0, pady=10)
        ttk.Button(self, text="Delete", command=self._delete_loan, bootstyle="danger").grid(
            row=4, column=1, pady=10)

    def _save_loan(self):
        name = self.name_var.get()
        principal = self.principal_var.get()
        interest = self.interest_var.get()
        min_payment = self.min_payment_var.get()
        if self.index is not None:
            self.loan_manager.update_loan(
                self.index, name, Decimal(str(round(principal, 2))), Decimal(str(round(interest, 2)))/100, Decimal(str(round(min_payment, 2))))
        else:
            self.loan_manager.add_loan(
                name, Decimal(str(principal)), Decimal(str(interest))/100, Decimal(str(min_payment)))
        if self.refresh_callback:
            self.refresh_callback()
        self.master.destroy()

    def _delete_loan(self):
        self.loan_manager.delete_loan(self.index)
        if self.refresh_callback:
            self.refresh_callback()
        self.master.destroy()
