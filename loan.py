
import bisect
import csv
import matplotlib.pyplot as plt
import pandas as pd
from decimal import Decimal


class Loan:
    """
    Represents a loan with a name, principal, rate, and minimum payment
    Generates a dataframe of the ongoing balance of the loan over time through
    repeated calls to calculate_next_month
    """

    def __init__(self, name: str, principal: Decimal, rate: Decimal, min_pmt: Decimal):
        self.name = name
        self.principal = principal
        self.rate = rate
        self.min_pmt = min_pmt
        self.balances = [principal]
        self.interests = [Decimal(0)]
        self.payments = [Decimal(0)]
        self.done = False

    def calculate_next_month(self, payment: Decimal) -> Decimal:
        """
        Calculate the next month's loan data given a (max allowed) monthly payment
        Returns the value of the actual payment made (which may be less than the input if the loan is paid off)
        """
        # If the balance is 0, we don't pay anything
        if self.done:
            return 0.0

        # Calculate the new balance and interest
        prev_balance = self.balances[-1]
        interest = prev_balance * self.rate/12
        new_balance = prev_balance + interest - payment

        # If our loan is (over)paid, adjust the payment and mark complete
        if new_balance <= 0:
            payment = prev_balance + interest
            new_balance = Decimal(0)
            self.done = True

        # Add the new data to the lists
        self.interests.append(interest)
        self.balances.append(new_balance)
        self.payments.append(payment)
        # Return the actual payment made
        return payment

    def get_dataframe(self) -> pd.DataFrame:
        """Return the loan's data as a dataframe"""
        return pd.DataFrame({"Loan": self.name,
                             "Month": range(len(self.balances)),
                             "Interest": self.interests,
                             "Payment": self.payments,
                             "Balance": self.balances}
                            ).astype({"Loan": str, "Month": int, "Interest": float, "Payment": float, "Balance": float})

    def reset(self) -> None:
        """Reset the loan to its initial state"""
        self.balances = [self.principal]
        self.interests = [Decimal(0)]
        self.payments = [Decimal(0)]
        self.done = False

    def __str__(self):
        return f'Loan("{self.name}", {self.principal}, {self.rate}, {self.min_pmt})\n'


class LoanManager:
    """
    Perform CRUD updates on a list of loans
    Automatically updates the loan dataframe when loans are added, updated, or deleted
    """

    def __init__(self, loans: list[Loan] = None, payment_bands=None):
        self.loans = loans if loans is not None else []
        self.loan_df: pd.DataFrame = pd.DataFrame()
        self.payment_bands = payment_bands if payment_bands is not None else {
            0: 1000}
        self.refresh_loan_df()

    @staticmethod
    def read_from_file():
        loans = []
        with open("loans.csv", 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for line in reader:
                loans.append(
                    Loan(line["name"], Decimal(line["principal"]), Decimal(line["rate"]), Decimal(line["min_pmt"])))

        with open("payment_bands.csv", 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            payment_bands = {int(line["month"]): Decimal(
                line["payment"]) for line in reader}
        return LoanManager(loans, payment_bands)

    def save_to_file(self) -> None:
        """
        Save the loan info in loans.csv
        Save the payment bands in payment_bands.csv
        """
        with open("loans.csv", 'w') as csvfile:
            fieldnames = ["name", "principal", "rate", "min_pmt"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for loan in self.loans:
                writer.writerow({"name": loan.name, "principal": loan.principal,
                                "rate": loan.rate, "min_pmt": loan.min_pmt})
        with open("payment_bands.csv", 'w') as csvfile:
            fieldnames = ["month", "payment"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for month, payment in self.payment_bands.items():
                writer.writerow({"month": month, "payment": payment})

    def add_loan(self, name, principal, rate, min_pmt) -> None:
        self.loans.append(Loan(name, principal, rate, min_pmt))
        self.refresh_loan_df()

    def update_loan(self, index, name, principal, rate, min_pmt) -> None:
        if 0 <= index < len(self.loans):
            self.loans[index] = Loan(name, principal, rate, min_pmt)
            self.refresh_loan_df()

    def delete_loan(self, index) -> None:
        if 0 <= index < len(self.loans):
            del self.loans[index]
            self.refresh_loan_df()

    def add_payment_band(self, month: int, payment: Decimal) -> None:
        self.payment_bands[month] = payment
        self.refresh_loan_df()

    def delete_payment_band(self, month: int) -> None:
        if month in self.payment_bands:
            del self.payment_bands[month]
            if self.payment_bands == {}:
                self.payment_bands = {0: 1000}
            self.refresh_loan_df()
        # Dont let it ever be empty

    def find_payment_amount(self, month: int) -> Decimal:
        """
        Find the payment amount corresponding to a given month
        """
        months, incomes = zip(*
                              sorted(self.payment_bands.items(), key=lambda x: x[0]))
        index = bisect.bisect_right(months, month)
        return incomes[index-1]

    def refresh_loan_df(self) -> None:
        """
        Calculate the balance of loans over time
        Given a list of Loans, custom payments, and a snowball amount
        Returns a dataframe of Loan, Month, Balance, Interest, and Payments for all loans
        """
        # Store the loans in descending order of rate, track which still have a balance
        ongoing_loans = sorted([i for i in self.loans],
                               key=lambda x: x.rate, reverse=True)
        # Reset all loans
        for loan in ongoing_loans:
            loan.reset()

        # Calculate the balance of the loans over time
        loan_data = []
        month = 1
        while ongoing_loans:
            # Find the index of the interval that the payment belongs to
            payment = self.find_payment_amount(month)
            # Calculate the next month on each loan
            minimum_payments = sum(
                (min(loan.min_pmt, loan.balances[-1]) for loan in ongoing_loans))
            print(month, payment, minimum_payments)
            snowball_amt = payment - minimum_payments
            if snowball_amt < 0:
                raise ValueError(
                    f"Minimum payments of {minimum_payments} are greater than our current payment of {payment}")
            # Go through each loan, paying in order of descending interest rate
            for loan in ongoing_loans:
                minimum_payment = min(loan.min_pmt, loan.balances[-1])
                actual_payment = loan.calculate_next_month(
                    loan.min_pmt + snowball_amt)
                snowball_amt -= actual_payment - minimum_payment
                if snowball_amt < 0:
                    raise ValueError(
                        f"Snowball amount should never become negative - we paid more that we can afford!")
                if loan.done:
                    loan_data.append(loan.get_dataframe())
            ongoing_loans = [loan for loan in ongoing_loans if not loan.done]
            month += 1
        self.loan_df = pd.concat(loan_data)

    def __str__(self) -> str:
        s = ""
        for loan in self.loans:
            s += str(loan)
        return s


class Plotter:
    """
    Holds a figure containing the main loan plots
    """

    def __init__(self):
        self.fig, self.ax = plt.subplots(2, 2, figsize=(12, 6))
        self.fig.set_tight_layout(True)

    def refresh(self, df: pd.DataFrame):
        if df.empty:
            return
        for axis in self.ax.flatten():
            axis.clear()
        self.df = df
        self._plot_balance(self.ax[0][0])
        self._plot_balance_unstacked(self.ax[0][1])
        self._plot_cum_pmts(self.ax[1][1])
        self._plot_payment(self.ax[1][0])

    def _plot_balance(self, ax: plt.Axes):
        """
        Plot a loan balances on stackplot
        """
        pivot_df = self.df.pivot_table(
            index="Month", columns="Loan", values="Balance", fill_value=0)
        self.order = sorted(
            pivot_df.columns, key=lambda x: pivot_df[x].iloc[0], reverse=True)
        pivot_df = pivot_df[self.order]
        months = pivot_df.index.values
        loan_balances = pivot_df.transpose().values
        ax.stackplot(months, loan_balances, labels=pivot_df.columns)
        ax.legend(loc='upper right')
        ax.set_xlabel("Month")
        ax.set_ylabel("Balance")

    def _plot_payment(self, ax: plt.Axes):
        """
        Plot payments by loan on a stacked bar chart
        """
        pivot_df = self.df.pivot_table(
            index="Month", columns="Loan", values="Payment", fill_value=0)
        pivot_df = pivot_df[self.order]
        months = pivot_df.index.values
        loan_balances = pivot_df.transpose().values

        # Plot the balance and interest
        ax.stackplot(months, loan_balances, labels=pivot_df.columns)
        ax.legend(loc='upper right')
        ax.set_xlabel("Month")
        ax.set_ylabel("Payment")

    # def _plot_interest(self, ax: plt.Axes):
    #     """
    #     Plot loan interest on a stacked bar chart
    #     """
    #     pivot_df = self.df.pivot_table(
    #         index="Month", columns="Loan", values="Interest", fill_value=0)
    #     pivot_df = pivot_df[self.order]
    #     months = pivot_df.index.values
    #     loan_balances = pivot_df.transpose().values

        # # Plot the balance and interest
        # ax.stackplot(months, loan_balances, labels=pivot_df.columns)
        # ax.legend(loc='upper right')
        # ax.set_xlabel("Month")
        # ax.set_ylabel("Interest")

    # def _plot_payment_dest(self, ax: plt.Axes):
    #     """
    #     Plot loan interest vs the principal on a stackplot
    #     """
    #     grouped = self.df.groupby("Month").sum()
    #     months = grouped.index.values
    #     interest = grouped["Interest"].values
    #     principal = (grouped["Payment"] - grouped["Interest"]).values

    #     # Plot the balance and interest
    #     ax.stackplot(months, principal, interest,
    #                  labels=["Principal", "Interest"])
    #     ax.legend(loc='upper right')
    #     ax.set_xlabel("Month")
    #     ax.set_ylabel("Payment")

    def _plot_balance_unstacked(self, ax: plt.Axes):
        """
        Plot loan balances on a line chart
        """
        grouped = self.df.groupby("Loan")
        plots = []
        for name, group in grouped:
            plots.append((name, group["Month"], group["Balance"]))
        for name, months, balance in sorted(plots, key=lambda x: x[2].iloc[0], reverse=True):
            ax.plot(months, balance, label=name)
        ax.legend(loc='upper right')
        ax.set_xlabel("Month")
        ax.set_ylabel("Balance")

    def _plot_cum_pmts(self, ax: plt.Axes):
        """
        Plot cumulative payments on a line chart
        """
        grouped = self.df.groupby("Loan").sum()
        grouped = grouped.loc[self.order]
        grouped["Principal"] = grouped["Payment"] - grouped["Interest"]
        grouped[["Principal", "Interest"]].astype(float).plot(
            kind="bar", stacked=True, ax=ax)
        ax.set_xticklabels(self.order, rotation=30)
        ax.set_xlabel(None)
