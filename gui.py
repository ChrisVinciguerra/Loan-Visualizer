import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from frames.InfoFrame import InfoFrame
from frames.PaymentFrame import PaymentFrame
from frames.PlotFrame import PlotFrame
from loan import LoanManager, Plotter

# TODO
# Data validation for EVERYTHING
# Add more typing hints
# Show data inside a table instead? Or justify it and make it look better
# Change the income menu to snap to the nearest point
# Make it continue the last point indefinetley
# Make it draggable to select income?
# Fix figure sizing and grid box, don't guess
# Show a chart of payments over time
# Allow it to be positioned in real time, and show dates instead of months from 0


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

        # Payment plotter and put it on grid
        self.payment_frame = PaymentFrame(
            self, self.loan_manager, self.refresh)
        self.payment_frame.grid(row=1, column=1, sticky='nsew')

        # Create the frame that will hold the plot
        self.plot_frame = PlotFrame(self, self.loan_manager, self.plotter)
        self.plot_frame.grid(row=2, column=0, columnspan=2, sticky='nsew')

    def refresh(self):
        self.loan_manager.save_to_file()
        self.info_frame.refresh()
        self.payment_frame.refresh()
        self.plot_frame.refresh()


def main():
    ttk.utility.enable_high_dpi_awareness()
    app = LoanApp()
    app.mainloop()


if __name__ == "__main__":
    main()
