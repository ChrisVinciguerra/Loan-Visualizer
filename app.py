import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def calculate_loan(name, principal, rate, min_pmt, payments):
    """
    Calculate the balance of a loan over time 
    Given the principal, interest rate, minimum payment, and a list of additional payments
    Returns a dataframe of Loan, Year, Balance, Interest, and Payments
    """
    month = 1
    balances = [principal]
    interests = [0]
    if not payments:
        payments = [0]
    # While the principal is greater than 0
    while balances[-1] > 0:
        # If there is no manual payment for the year, use the minimum payment
        if month >= len(payments):
            payments.append(min_pmt)

        # Calculate the interest and new balance
        prev_balance = balances[-1]
        interest = prev_balance * (rate/12)
        new_balance = prev_balance - payments[-1] + interest
        # If the balance is negative, reduce the last payment by the negative balance
        if new_balance < 0:
            payments[-1] = payments[-1] + new_balance
            new_balance = 0
        interests.append(interest)
        balances.append(new_balance)
        month += 1
    # Create a dataframe of the loan's data
    return pd.DataFrame({"Loan": name, "Month": range(month), "Balance": balances, "Interest": interests, "Payments": payments})


def plot_balance(ax: plt.Axes, joined_df: pd.DataFrame):
    """
    Plot a iterator of loans on a stacked bar chart
    """
    pivot_df = joined_df.pivot_table(
        index="Month", columns="Loan", values="Balance", fill_value=0)
    print(pivot_df)
    years = pivot_df.index.values
    loan_balances = pivot_df.transpose().values

    # Plot the balance and interest
    ax.stackplot(years, loan_balances, labels=pivot_df.columns)
    ax.legend(loc='upper right')
    ax.set_xlabel("Month")
    ax.set_ylabel("Balance")


def main():
    data = [{"name": "Test", "principal": 20000, "rate": 0.08, "min_pmt": 200},
            {"name": "Direct", "principal": 10000, "rate": 0.08, "min_pmt": 200},
            {"name": "Test2", "principal": 6000, "rate": 0.08, "min_pmt": 200}]

    # Generator of the each loan's rows in the dataframe
    loan_dfs_gen = (calculate_loan(loan["name"], loan["principal"], loan["rate"], loan["min_pmt"], [])
                    for loan in data)
    joined_df = pd.concat(loan_dfs_gen, ignore_index=True)

    print(joined_df)

    fig, ax = plt.subplots()
    plot_balance(ax, joined_df)
    plt.show()


if __name__ == "__main__":
    main()
