import argparse
import json
import os
import sys
from datetime import datetime
import csv
from idlelib.debugobj_r import remote_object_tree_item

FILE = 'expense-tracker.json'
BUDGET = 'budget.json'

def load_expenses():
    if not os.path.exists(FILE):
        return []
    try:
        with open(FILE, 'r') as f:
            content = json.load(f)
            return content if content else []
    except (json.JSONDecodeError, OSError):
        return []

def save_expenses(expenses):
    with open(FILE, 'w') as f:
        json.dump(expenses, f, indent=2)

def cmd_add(args):
    description = args.description
    amount = args.amount

    expenses = load_expenses()

    if not expenses:
        new_id = 0
    else:
        new_id = max(expense['id'] for expense in expenses) + 1

    now = datetime.now()

    if amount > 0:
        new_expense = {
            'id': new_id,
            'title': description,
            'amount': amount,
            'date': now.strftime("%d.%m.%Y %H:%M:%S"),
            'status': 'active',
        }
    else:
        print("Error: amount must be positive")
        return

    expenses.append(new_expense)
    save_expenses(expenses)

def cmd_delete(args):
    expenses = load_expenses()
    expense_id = int(args.delete_id)

    for i, expense in enumerate(expenses):
        if expense['id'] == expense_id:
            expense['status'] = 'deleted'
            save_expenses(expenses)
            print(f"Deleted ID expense:{expense_id}")
            return

    print("Error: ID does not exist")

def cmd_sum(args):
    expenses = load_expenses()
    total = 0
    month = getattr(args, 'month', None)

    for expense in expenses:
        if expense.get("status") != "active":
            continue

        if month:
            date_str = expense['date']
            expense_month = int(date_str.split()[0].split('.')[1])
            if expense_month != month:
                continue

        total += expense['amount']

    if month:
        print(f"Total expenses for month {month}: ${total}")
    else:
        print(f"Total expenses: ${total}")

def cmd_update(args):
    expenses = load_expenses()
    expense_id = int(args.id)

    for i, expense in enumerate(expenses):
        if expense['id'] == expense_id:
            if args.description:
                expense['title'] = args.description

            if args.amount is not None:
                if args.amount <= 0:
                    print("Error: amount must be positive")
                    return
                expense['amount'] = args.amount

            expense['date'] = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
            save_expenses(expenses)
            print(f"Updated ID expense:{expense_id}")
            return


def load_budget():
    if not os.path.exists(BUDGET):
        return {}
    try:
        with open(BUDGET, 'r') as f:
            content = json.load(f)
            return content if content else {}
    except (json.JSONDecodeError, OSError):
        return {}

def save_budget(budget):
    with open(BUDGET, 'w') as f:
        json.dump(budget, f, indent=2)

def cmd_set_budget(args):
    month = args.month
    amount = args.amount

    if not (1 <= month <= 12):
        print("Error: month must be between 1 and 12")
        return

    if amount <= 0:
        print("Error: amount must be positive")
        return

    budgets = load_budget()
    budgets[str(month)] = amount
    save_budget(budgets)
    print(f"Budget for month {month} set to ${amount}")


def cmd_list (args):
    expenses = load_expenses()

    if not expenses:
        print("No expenses found")
        return

    active = [e for e in expenses if e.get("status") == 'active']
    deleted = [e for e in expenses if e.get("status") == 'deleted']



    #Active
    print("ID   Date                Description  Amount  Status")
    print("=" * 23, "Active", "=" * 23)
    if not active:
        print("No active expenses found")
    else:
        for expense in active:
            print(f"{expense['id']:<4} {expense['date']:<12} {expense['title']:<12} ${expense['amount']:<5}  {expense['status']}")

    print("-" * 55)
    cmd_sum(args)
    print()

    current_month = datetime.now().month
    budgets = load_budget()
    budget = budgets.get(str(current_month), 0)

    spent = 0
    for expense in expenses:
        if expense.get("status", "active") != "active":
            continue
        try:
            expense_month = int(expense['date'].split()[0].split('.')[1])
            if expense_month == current_month:
                spent += expense['amount']
        except (IndexError, ValueError):
            continue

    remaining = budget - spent

    print(f"Budget (month {current_month}): ${budget}")
    print(f"Spent: ${spent} | Remaining: ${remaining}")
    if budget > 0 and remaining < 0:
        print("Warning: Budget exceeded!")

    #Deleted
    print("=" * 23, "Deleted", "=" * 23)
    if not deleted:
        print("No deleted expenses found")
    else:
        for expense in deleted:
            print(f"{expense['id']:<4} {expense['date']:<12} {expense['title']:<12} ${expense['amount']:<5}  {expense['status']}")

def cmd_export(args):
    expenses = load_expenses()
    filename = args.output

    if not expenses:
        print("No expenses found")
        return

    with open(filename, "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Date", "Description", "Amount", "Status"])

        for expense in expenses:
            writer.writerow([
                expense.get('id'),
                expense.get('date'),
                expense.get('title'),
                expense.get('amount'),
                expense.get('status', 'active'),
            ])

        print(f"Exported to {filename}")

def main():
    parser = argparse.ArgumentParser(description="expense-tracker")
    subparsers = parser.add_subparsers(dest='command', help='all commands')

    #command add
    e_add = subparsers.add_parser('add', help='add expense')
    e_add.add_argument('description', type=str, help='expense description')
    e_add.add_argument('amount',type=int, help='expense amount')
    e_add.set_defaults(func=cmd_add)

    #command list
    e_list = subparsers.add_parser('list', help='list all expenses')
    e_list.set_defaults(func=cmd_list)

    #command delete
    e_delete = subparsers.add_parser('delete', help='delete expense')
    e_delete.add_argument('delete_id', help='expense id')
    e_delete.set_defaults(func=cmd_delete)

    #command sum
    e_sum = subparsers.add_parser('sum', help='sum expense')
    e_sum.add_argument('month', nargs='?', type=int, help='month number')
    e_sum.set_defaults(func=cmd_sum)

    #command update
    e_update = subparsers.add_parser('update', help='update expense')
    e_update.add_argument('id',  type=int, help='expense description')
    e_update.add_argument('description', nargs='?', help='expense amount')
    e_update.add_argument('amount', type=int, nargs='?', help='expense amount')
    e_update.set_defaults(func=cmd_update)

    #command set-budget
    e_set_budget = subparsers.add_parser('set-budget', help='set expense budget')
    e_set_budget.add_argument('month', type=int, help='month number')
    e_set_budget.add_argument('amount', type=int, help='expense budget')
    e_set_budget.set_defaults(func=cmd_set_budget)

    #command export
    e_export = subparsers.add_parser('export', help='export expenses to CSV')
    e_export.add_argument('--output', default='expenses.csv', help='output CSV file name')
    e_export.set_defaults(func=cmd_export)

    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)

    args.func(args)

if __name__ == "__main__":
    main()