import argparse
import json
import csv
from datetime import datetime
import os

DATA = "expenses.json"

def json_to_csv(json_file_path, csv_file_path):
    with open(json_file_path, 'r') as json_file:
        data = json.load(json_file)

    if not isinstance(data, list):
        raise ValueError("JSON data must be a list of dictionaries.")

    if not data:
         return # Handle empty list case

    with open(csv_file_path, 'w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

def load_expenses():
    if not os.path.exists(DATA):
        return []
    with open(DATA, "r") as f:
        return json.load(f)

def save_expenses(expense):
    with open(DATA, "w") as f:
        json.dump(expense, f, indent=2)

def add_expense(desc, amount):
    expenses = load_expenses()
    new_expense = {
        "id": len(expenses) + 1,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "description": desc,
        "amount": amount
    }
    expenses.append(new_expense)
    save_expenses(expenses)

def list_expenses():
    expenses = load_expenses()
    if not expenses:
        print("no recorded expenses")
        return
    print("ID | Date       | Description        | Amount")
    print("-----------------------------------------------")
    for e in expenses:
        print(f"{e['id']:2} | {e['date']} | {e['description']:<18} | ${e['amount']}")
        
def delete_expense(expense_id):
    expenses = load_expenses()
    updated_expenses = [e for e in expenses if e['id'] != expense_id]
    
    if len(updated_expenses) == len(expenses):
        print("no expense found")
    else:
        for i,e in enumerate(updated_expenses, start=1):
            e["id"] = i
        save_expenses(updated_expenses)
        
def update_expense(expense_id, new_desc = None, new_amount = None):
    expenses = load_expenses()
    found = False 
    for e in expenses:
        if e["id"] == expense_id:
            if new_desc is not None:
                e["description"] = new_desc
            if new_amount is not None:
                e["amount"] = new_amount
            found = True
            break

    if not found:
        print(f"No expense found with ID {expense_id}")
        return
    
    save_expenses(expenses)
    print("expense updated")
        
def show_summary(month = None):
    expenses = load_expenses()
    if month:
        current_year = datetime.now().year
        expenses = [
            e for e in expenses
            if e["date"].startswith(f"{current_year}-{month:02d}")
        ]
        
    total = sum(e["amount"] for e in expenses)
    if month:
        print(f"Total expenses for {datetime(1900, month, 1).strftime('%B')}: ${total:.2f}")
    else:
        print(f"Total Expenses: ${total:.2f}")


def main():
    parser = argparse.ArgumentParser(description="Expense Tracker CLI")
    subparsers = parser.add_subparsers(dest="command")
    
    add_parser = subparsers.add_parser("add")
    add_parser.add_argument("--description", required=True)
    add_parser.add_argument("--amount", type=float, required=True)
    
    delete_parser = subparsers.add_parser("delete")
    delete_parser.add_argument("--id", type=int, required=True)
    
    update_parser = subparsers.add_parser("update")
    update_parser.add_argument("--id", type=int, required=True)
    update_parser.add_argument("--description", help="New description")
    update_parser.add_argument("--amount", type=float, help="New amount")
    
    summary_parser = subparsers.add_parser("summary")
    summary_parser.add_argument("--month", type=int, choices=range(1, 13), help="Month (1–12)")
    
    export_parser = subparsers.add_parser("export")
    export_parser.add_argument("--output", default="expenses.csv", help="CSV output filename")


    
    list_parser = subparsers.add_parser("list")
    
    args = parser.parse_args()
    
    if args.command == "add":
        add_expense(args.description, args.amount)
    elif args.command == "list":
        list_expenses()
    elif args.command == "delete":
        delete_expense(args.id)
    elif args.command == "summary":
        show_summary(args.month)
    elif args.command == "update":
        update_expense(args.id, args.description, args.amount)
    elif args.command == "export":
        json_to_csv(DATA, args.output)
    else:
        parser.print_help()
        
if __name__ == "__main__":
    main()
        