from pprint import pprint

from app.ai.tools.banking_tools import (
    get_account_balance,
    get_account_transactions,
)


def main():
    print("=== Balance ===")

    balance = get_account_balance(1)
    pprint(balance)

    print()
    print("=== Transactions ===")

    transactions = get_account_transactions(1)
    pprint(transactions)


if __name__ == "__main__":
    main()