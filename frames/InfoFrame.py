from ttkbootstrap import Toplevel
from ttkbootstrap import ttk

from frames.EditFrame import EditFrame
from loan import LoanManager


class InfoFrame(ttk.Frame):
    """
    Frame that displays the loan information in a table like view
    Has buttons to add, edit and delete loans that creates a popup window
    """

    def __init__(self, parent, loan_manager: LoanManager, refresh_callback, **kwargs):
        super().__init__(parent, **kwargs)
        self.loan_manager = loan_manager
        self.refresh_callback = refresh_callback
        self.draw()

    def draw(self):
        ttk.Button(
            self, text="New Loan",
            command=self.open_loan_popup,
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

    def open_loan_popup(self, index=None):
        """Opens a popup window to edit the loan at the given index"""
        popup = Toplevel(self)
        editframe = EditFrame(popup, self.loan_manager, index,
                              refresh_callback=self.refresh_callback)
        editframe.grid(row=0, column=0, sticky='nsew')

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
