import bisect
from typing import Generator, Optional
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


class Loan:
    """
    Class to represent a loan with a name, principal, rate, and minimum payment
    Can calculate the ongoing balance of the loan one month at a time
    """

    def __init__(self, name: str, principal: float, rate: float, min_pmt: float):
        self.name = name
        self.principal = principal
        self.rate = rate
        self.min_pmt = min_pmt
        self.balances = [principal]
        self.interests = [0]
        self.payments = [0]
        self.done = False

    def calculate_next_month(self, payment: Optional[float] = None) -> bool:
        """
        Calculate the next month's data on the loan
        Returns the value of the actual payment made
        """
        # If the balance is 0, we're done
        if self.done:
            return 0

        # Calculate the new balance and interest
        prev_balance = self.balances[-1]
        interest = prev_balance * (self.rate/12)
        new_balance = prev_balance - payment + interest
        # If our loan is overpaid, adjust the payment
        if new_balance <= 0:
            payment = payment + new_balance
            new_balance = 0
            self.done = True
        # Add the new data to the lists
        self.interests.append(interest)
        self.balances.append(new_balance)
        self.payments.append(payment)
        return self.payments[-1]

    def get_dataframe(self) -> pd.DataFrame:
        """Return the loan's data as a dataframe"""
        return pd.DataFrame({"Loan": self.name, "Month": range(len(self.balances)),  "Interest": self.interests, "Payment": self.payments, "Balance": self.balances})

    def reset(self) -> None:
        self.balances = [self.principal]
        self.interests = [0]
        self.payments = [0]
        self.done = False


def calculate_loans(loan_info: list[Loan], one_time_pmts: dict[int, float], payment_bands: tuple[list[int], list[float]]) -> pd.DataFrame:
    """
    Calculate the balance of loans over time
    Given a list of Loans, custom payments, and a snowball amount
    Returns a dataframe of Loan, Month, Balance, Interest, and Payments for all loans
    """
    # Store the loans in descending order of rate, track which still have a balance
    ongoing_loans = sorted([i for i in loan_info],
                           key=lambda x: x.rate, reverse=True)
    for loan in ongoing_loans:
        loan.reset()

    boundaries, payment_values = [i for i in zip(*payment_bands)]

    # Calculate the balance of the loans over time
    loan_data = []
    month = 1
    while ongoing_loans:
        minimum_payments = sum(
            (min(loan.min_pmt, loan.balances[-1]) for loan in ongoing_loans))
        # Find the index of the interval that the payment belongs to
        index = bisect.bisect_right(boundaries, month)
        payment = payment_values[index-1]
        # Check if we have a one-time payment this month
        if month in one_time_pmts:
            payment += one_time_pmts[month]
        snowball = payment - minimum_payments
        if snowball < 0:
            raise ValueError(
                f"Minimum payments of {minimum_payments} are greater than the payment of {payment}")
        # Calculate the next month on each loan
        for loan in ongoing_loans:
            actual_payment = loan.calculate_next_month(loan.min_pmt + snowball)
            snowball -= actual_payment - loan.min_pmt
            if loan.done:
                loan_data.append(loan.get_dataframe())
        ongoing_loans = [loan for loan in ongoing_loans if not loan.done]
        month += 1
    return pd.concat(loan_data)


def plot_balance(ax: plt.Axes, df: pd.DataFrame):
    """
    Plot a loan balances on stackplot
    """
    pivot_df = df.pivot_table(
        index="Month", columns="Loan", values="Balance", fill_value=0)
    pivot_df = pivot_df[sorted(
        pivot_df.columns, key=lambda x: pivot_df[x].iloc[0], reverse=True)]
    months = pivot_df.index.values
    loan_balances = pivot_df.transpose().values
    ax.stackplot(months, loan_balances, labels=pivot_df.columns)
    ax.legend(loc='upper right')
    ax.set_xlabel("Month")
    ax.set_ylabel("Balance")


def plot_payment(ax: plt.Axes, df: pd.DataFrame):
    """
    Plot payments by loan on a stacked bar chart
    """
    pivot_df = df.pivot_table(
        index="Month", columns="Loan", values="Payment", fill_value=0)
    pivot_df = pivot_df[sorted(
        pivot_df.columns, key=lambda x: pivot_df[x].iloc[1], reverse=True)]
    months = pivot_df.index.values
    loan_balances = pivot_df.transpose().values

    # Plot the balance and interest
    ax.stackplot(months, loan_balances, labels=pivot_df.columns)
    ax.legend(loc='upper right')
    ax.set_xlabel("Month")
    ax.set_ylabel("Payment")


def plot_interest(ax: plt.Axes, df: pd.DataFrame):
    """
    Plot loan interest on a stacked bar chart
    """
    pivot_df = df.pivot_table(
        index="Month", columns="Loan", values="Interest", fill_value=0)
    pivot_df = pivot_df[sorted(
        pivot_df.columns, key=lambda x: pivot_df[x].iloc[1], reverse=True)]
    months = pivot_df.index.values
    loan_balances = pivot_df.transpose().values

    # Plot the balance and interest
    ax.stackplot(months, loan_balances, labels=pivot_df.columns)
    ax.legend(loc='upper right')
    ax.set_xlabel("Month")
    ax.set_ylabel("Interest")


def plot_payment_dest(ax: plt.Axes, df: pd.DataFrame):
    """
    Plot loan interest vs the principal on a stackplot
    """
    grouped = df.groupby("Month").sum()
    months = grouped.index.values
    interest = grouped["Interest"].values
    principal = (grouped["Payment"] - grouped["Interest"]).values

    # Plot the balance and interest
    ax.stackplot(months, principal, interest, labels=["Principal", "Interest"])
    ax.legend(loc='upper right')
    ax.set_xlabel("Month")
    ax.set_ylabel("Payment")


def plot_cum_pmts(ax: plt.Axes, df: pd.DataFrame):
    """
    Plot cumulative payments on a line chart
    """

    grouped = df.groupby("Loan").sum()
    grouped["Principal"] = grouped["Payment"] - grouped["Interest"]
    grouped[["Principal", "Interest"]].plot(kind="bar", stacked=True, ax=ax)


def main():
    loan_info = [Loan("Test", 50000, 0.1075, 50), Loan(
        "Direct", 10000, 0.08, 200), Loan("Test2", 6000, 0.08, 200)]

    # Generator of the each loan's rows in the dataframe
    df = calculate_loans(loan_info, {}, [(0, 1000), (12, 1400)])
    print(df)
    fig, ax = plt.subplots(2, 2, figsize=(18, 8))
    plot_balance(ax[0][0], df)
    plot_cum_pmts(ax[0][1], df)
    plot_payment(ax[1][0], df)
    plot_payment_dest(ax[1][1], df)
    plt.show()


if __name__ == "__main__":
    main()
