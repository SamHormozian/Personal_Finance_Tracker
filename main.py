import pandas as pd
import csv
from datetime import datetime
from data_entry import getAmount, getCategory, getDate, getDescription
import matplotlib.pyplot as plt

class CSV:
    CSV_File = 'transaction_data.csv'
    columns=['date', 'amount', 'category', 'description']
    format = '%d-%m-%Y'

    @classmethod
    def initialize_csv(cls):
        try:
            pd.read_csv(cls.CSV_File)
        except FileNotFoundError:
            df = pd.DataFrame(columns=cls.columns)
            df.to_csv(cls.CSV_File, index=False)

    @classmethod
    def add_entry(cls, date, amount, category, description):
        newEntry = {
            'date':date,
            'amount':amount,
            'category':category,
            'description':description
        }
        with open(cls.CSV_File, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=cls.columns)
            writer.writerow(newEntry)
        print('Entry Added!')

    @classmethod
    def getTransactions(cls, start_date, end_date):
        df = pd.read_csv(cls.CSV_File)
        df['date'] = pd.to_datetime(df['date'], format = CSV.format)
        start_date = datetime.strptime(start_date, CSV.format)
        end_date = datetime.strptime(end_date, CSV.format)

        mask = (df['date'] >= start_date) & (df['date'] <= end_date)
        filtered_df = df.loc[mask]

        if filtered_df.empty:
            print('No transactions in given date in range.')
        else:
            print(f"Transactions from {start_date.strftime(CSV.format)} to {end_date.strftime(CSV.format)}")
            print(filtered_df.to_string(index = False, formatters= {"date": lambda x: x.strftime(CSV.format)}))

            total_income = filtered_df[filtered_df['category']=='Income']['amount'].sum()
            total_expense = filtered_df[filtered_df['category']=='Expense']['amount'].sum()
            print('\nSummary:')
            print(f'Total Income: ${total_income:.2f}')
            print(f'Total Expense: ${total_expense:.2f}')
            print(f'Net Savings: ${(total_income - total_expense):.2f}')

        return filtered_df




def add():
    CSV.initialize_csv()
    date = getDate("Enter the date of the transaction (dd/mm/yyyy) or enter today's date: ", allow_default=True)
    amount = getAmount()
    category = getCategory()
    description = getDescription()
    CSV.add_entry(date, amount, category, description)

def transactions_plotted(df):
    df.set_index('date', inplace = True)

    income_df = df[df['category'] == 'Income'].resample('D').sum().reindex(df.index, fill_value=0)
    expense_df = df[df['category'] == 'Expense'].resample('D').sum().reindex(df.index, fill_value=0)

    plt.figure(figsize=(10,5))
    plt.plot(income_df.index, income_df['amount'], label = 'Income', color='b')
    plt.plot(income_df.index, expense_df['amount'], label = 'Expense', color='r')
    plt.xlabel('Date')
    plt.ylabel('Amount')
    plt.title('Income and Expenses over Time')
    plt.legend()
    plt.grid(True)
    plt.show()

def main():
    while True:
        print('\n1. Add new transaction.')
        print('2. View transactions and summary within a range of dates.')
        print('3. Exit.')
        choice = input("What would you like to do today? (1-3): ")

        if choice == '1':
            add()
        elif choice == '2':
            start_date = getDate('Enter the start date (dd-mm-yyyy): ')
            end_date = getDate('Enter the end date (dd-m-yyyy): ')
            df= CSV.getTransactions(start_date, end_date)
            if input("Would you like to see a plot? (yes/no) ").lower() == "yes":
                transactions_plotted(df)
        elif choice == '3':
            print('Thank you for your time')
            break
        else:
            print('Invalid choice. enter 1, 2 or 3')

if __name__ == '__main__':
    main()
