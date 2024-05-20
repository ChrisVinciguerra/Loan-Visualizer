
import ttkbootstrap as ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from loan import LoanManager, Plotter


class PlotFrame(ttk.Frame):
    def __init__(self, parent, loan_manager: LoanManager, plotter: Plotter):
        super().__init__(parent)
        self.loan_manager = loan_manager
        self.plotter = plotter
        self.canvas = FigureCanvasTkAgg(self.plotter.fig, self)
        toolbar = NavigationToolbar2Tk(
            self.canvas, self, pack_toolbar=False)
        toolbar.update()
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        toolbar.grid(row=1, column=0, sticky="nsew")
        self.refresh()

    def refresh(self):
        self.plotter.refresh(self.loan_manager.loan_df)
        self.canvas.draw()
