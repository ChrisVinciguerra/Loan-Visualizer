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
            command=self._open_loan_popup,
            bootstyle="primary"
        ).grid(row=0, column=0, sticky='ew', padx=20, pady=10)

        # Create Treeview
        self.tree = ttk.Treeview(self, columns=(
            'Loan', 'Principal', 'Rate', 'Min Payment', 'Edit', 'Delete'), show='headings', style='primary.Treeview')
        self.tree.grid(row=1, column=0, sticky='nsew', padx=20, pady=10)

        # Define columns

        self.tree.heading('Loan', text='Loan')
        self.tree.heading('Principal', text='Principal')
        self.tree.heading('Rate', text='Rate')
        self.tree.heading('Min Payment', text='Min Payment')
        # Configure treeview columns to expand
        # Set minimum column widths to ensure headers are not cut off
        self.tree.column('Loan', minwidth=200, stretch=True)
        self.tree.column('Principal',
                         minwidth=100, stretch=True)
        self.tree.column('Rate', minwidth=100, stretch=True)
        self.tree.column('Min Payment',
                         minwidth=100, stretch=True)
        self.tree.column('Edit', anchor='center', minwidth=20, stretch=False)

        # Add loans to Treeview
        for i, loan in enumerate(self.loan_manager.loans):
            id = self.tree.insert('', 'end', values=(
                f"{loan.name}", f"${loan.principal:.2f}", f"{loan.rate*100:.2f}%", f"${loan.min_pmt:.2f}", "Edit"))
        # Bind click events for Edit and Delete
        self.tree.bind('<ButtonRelease-1>', self._handle_click)

        # Set style for edit and delete "butons"
        self.tree.tag_configure('edit', foreground='blue')

    def _handle_click(self, event):
        item = self.tree.identify('item', event.x, event.y)
        column = self.tree.identify_column(event.x)
        if column == '#5' and item != "":  # Edit column
            self._open_loan_popup(self.tree.index(item))

    def _open_loan_popup(self, index=None):
        """Opens a popup window to edit the loan at the given index"""
        popup = Toplevel(self)
        editframe = EditFrame(popup, self.loan_manager, index,
                              refresh_callback=self.refresh_callback)
        editframe.grid(row=0, column=0, sticky='nsew')

    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()

    def refresh(self):
        self.clear()
        self.draw()
