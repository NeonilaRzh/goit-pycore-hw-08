from collections import UserDict
from functools import wraps
from datetime import datetime, date, timedelta
import pickle

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("The phone number must consist of 10 digits.")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            date_value = datetime.strptime(value, "%d.%m.%Y").date()
            super().__init__(date_value)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, del_phone):
        for phone in self.phones:
            if phone.value == del_phone:
                self.phones.remove(phone)

    def edit_phone(self, new_phone):
        if self.phones:
            self.phones[0] = Phone(new_phone)
            return True
        return False

    def find_phone(self, phone):
        for i in self.phones:
            if i.value == phone:
                return i
        return None

    def __str__(self):
        phones_str = ', '.join(str(phone) for phone in self.phones)
        birthday_str = f", birthday: {self.birthday.value.strftime('%d.%m.%Y')}" if self.birthday else ""
        return f"Contact name: {self.name}, phone: {phones_str}, birthday: {birthday_str}"

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self, days=7):
        upcoming_birthdays = []
        today = date.today()

        for record in self.data.values():
            if record.birthday:
                birthday_this_year = record.birthday.value.replace(year=today.year)
                if birthday_this_year < today:
                    birthday_this_year = record.birthday.value.replace(year=today.year + 1)

                if 0 <= (birthday_this_year - today).days <= days:
                    if birthday_this_year.weekday() >= 5:
                        delta = (7 - birthday_this_year.weekday())
                        birthday_this_year += timedelta(days=delta)
                        
                    congratulation_date_str = birthday_this_year.strftime('%Y.%m.%d')
                    upcoming_birthdays.append({"name": record.name.value, "congratulation_date": congratulation_date_str})
        
        return upcoming_birthdays

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, args

def input_error(func):
    @wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as ve:
            return str(ve)
        except KeyError:
            return "Contact not found."
        except IndexError:
            return "Please enter the command, name and number."
    return inner

@input_error
def add_contact(args, book: AddressBook):
    name, phone = args
    record = book.find(name)
    message = f"Contact {name} updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = f"Contact {name} added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_contact(args, book: AddressBook):
    name, new_phone = args
    record = book.find(name)
    if record.edit_phone(new_phone):
        return "Phone updated."
    else:
        return "This contact doesn't exist, please add new contact."

@input_error
def show_phone(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record:
        return ', '.join(phone.value for phone in record.phones)
    else:
        return "This contact doesn't exist."

@input_error
def show_all(args, book: AddressBook):
    if book:
        return '\n'.join([str(record) for record in book.values()])
    else:
        return "No contacts found."

@input_error
def add_birthday(args, book: AddressBook):
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return f"Birthday added for {name}."
    else:
        return f"Contact '{name}' not found."

@input_error
def show_birthday(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if record:
        if record.birthday:
            return f"Birthday for {name}: {record.birthday.value.strftime('%d.%m.%Y')}"
        else:
            return f"No birthday set for {name}."
    else:
        return f"Contact '{name}' not found."

@input_error
def birthdays(args, book: AddressBook):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if upcoming_birthdays:
        return "\n".join([f"{item['name']}: {item['congratulation_date']}" for item in upcoming_birthdays])
    else:
        return "No upcoming birthdays."

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

def main():
    book = load_data()

    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)
            print("Data has been saved. Good bye!")
            break
        
        elif command == "hello":
            print("How can I help you?")
            
        elif command == "add":
            print(add_contact(args, book))
            
        elif command == "change":
            print(change_contact(args, book))
            
        elif command == "phone":
            print(show_phone(args, book))
            
        elif command == "all":
            print(show_all(args, book))
            
        elif command == "add-birthday":
            print(add_birthday(args, book))
            
        elif command == "show-birthday":
            print(show_birthday(args, book))
            
        elif command == "birthdays":
            print(birthdays(args, book))
            
        else:
            print("Invalid command.")         

if __name__ == "__main__":
    main()