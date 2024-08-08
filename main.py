import pandas as pd
import csv
from datetime import datetime
from data_entry import getAmount, getCategory, getDate, getDescription
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import numpy as np

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

def preprocess_data(df):
    df['date'] = pd.to_datetime(df['date'], format=CSV.format)
    df['day'] = df['date'].dt.day
    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year
    df = pd.get_dummies(df, columns=['category'])
    df = df.drop(columns=['date', 'description'])
    return df

def train_model(df):
    df = preprocess_data(df)
    X = df.drop(columns=['amount'])
    y = df['amount']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = LinearRegression()
    model.fit(X_train, y_train)
    score = model.score(X_test, y_test)
    print(f'Model R^2 Score: {score:.2f}')
    return model

def predict_expense(model, year, month, day, category):
    data = {
        'day': [day],
        'month': [month],
        'year': [year],
        f'category_{category}': [1]
    }
    for cat in ['category_Income', 'category_Expense']:
        if cat not in data:
            data[cat] = [0]
    df = pd.DataFrame(data)
    prediction = model.predict(df)
    return prediction[0]

def plot_prediction(df, year, month, day, predicted_amount):
    # Convert 'date' column to datetime
    df['date'] = pd.to_datetime(df['date'], format=CSV.format)
    df.set_index('date', inplace=True)

    # Prepare data for trend line
    df['days_since_start'] = (df.index - df.index.min()).days
    X = df[['days_since_start']].values
    y = df['amount'].values

    # Fit linear regression model
    model = LinearRegression()
    model.fit(X, y)
    trend_line = model.predict(X)

    # Create a new dataframe for the prediction
    prediction_date = pd.Timestamp(year=year, month=month, day=day)
    prediction_df = pd.DataFrame({
        'date': [prediction_date],
        'amount': [predicted_amount],
        'category': ['Expense']
    })
    prediction_df.set_index('date', inplace=True)

    # Plot historical data
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['amount'], label='Historical Data', color='blue')

    # Plot trend line
    plt.plot(df.index, trend_line, label='Trend Line', color='green', linestyle='--')

    # Plot prediction
    plt.scatter(prediction_df.index, prediction_df['amount'], color='red', label='Prediction', zorder=5)

    plt.xlabel('Date')
    plt.ylabel('Amount')
    plt.title('Expense Prediction with Trend Line')
    plt.legend()
    plt.grid(True)
    plt.show()



def add():
    CSV.initialize_csv()
    date = getDate("Enter the date of the transaction (dd-mm-yyyy) or enter today's date: ", allow_default=True)
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
    global model
    CSV.initialize_csv()
    df = pd.read_csv(CSV.CSV_File)
    model = train_model(df)

    while True:
        print('\n1. Add new transaction.')
        print('2. View transactions and summary within a range of dates.')
        print('3. Predict future expenses.')
        print('4. Exit')
        choice = input("What would you like to do today? (1-4): ")

        if choice == '1':
            add()
        elif choice == '2':
            start_date = getDate('Enter the start date (dd-mm-yyyy): ')
            end_date = getDate('Enter the end date (dd-m-yyyy): ')
            df= CSV.getTransactions(start_date, end_date)
            if input("Would you like to see a plot? (yes/no) ").lower() == "yes":
                transactions_plotted(df)
        elif choice == '3':
            if model is None:
                print('Cannot predict expenses without previous transactions. Please add transactions')
            else:
                year = int(input('Enter year: '))
                month = int(input('Enter month: '))
                day = int(input('Enter day: '))
                category = 'Expense'
                prediction = predict_expense(model, year, month, day, category)
                print(f'Predicted {category} for {day}-{month}-{year}: ${prediction:.2f}')
                if input("Would you like to see a plot of the prediction? (yes/no) ").lower() == "yes":
                    plot_prediction(df, year, month, day, prediction)
        elif choice == '4':
            print('Thank you for your time!')
            break
        else:
            print('Invalid choice. Enter 1, 2, 3, or 4')

if __name__ == '__main__':
    main()
