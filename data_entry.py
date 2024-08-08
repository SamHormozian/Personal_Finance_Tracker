from datetime import datetime

dateFormat = '%d-%m-%Y'
categories = {
    'I':'Income',
    'E':'Expense'
}

def getDate(prompt, allow_default = False):
    date_string = input(prompt)
    if allow_default and not date_string:
        return datetime.today().strftime(dateFormat)

    try:
        validDate = datetime.strptime(date_string, dateFormat)
        return validDate.strftime(dateFormat)
    except ValueError:
        print('Invalid Date Format, Enter in dd-mm-yyyy format')
        return getDate(prompt, allow_default)

def getAmount():
    try:
        amount = float(input('Enter Amount: '))
        if amount <= 0:
            raise ValueError("Amount cannot be a negative or zero value.")
        return amount
    except ValueError as e:
        print(e)
        return getAmount()

def getCategory():
    category = input('Enter Category of Transaction "I" for income, "E" for expense): ').upper()
    if category in categories:
        return categories[category]

    print('Invalid category, please enter "I" for income, "E" for expense.')
    return getCategory


def getDescription():
    return input('Enter description (optional): ')
