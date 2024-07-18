import sys
from user import User
from group import Group
from expense import Expense
from transaction import Transaction
from connector import Connector
from datetime import datetime

class BillSharingApp:
    def __init__(self):
        db_params = {
        "password": "rootdatabase24",
        "filepath": "",
        "user": "root",
        "host": "localhost",
        "port": "3306",
        "database": "bill_sharing_app"
    }
 
    # Create a Connector object
    
        self.connector = Connector(**db_params)
        self.current_user = None

    def start(self):
        print("Welcome to the Bill Sharing App!")
        while True:
            if not self.current_user:
                self.show_auth_menu()
            else:
                self.show_main_menu()

    def show_auth_menu(self):
        print("\n1. Login")
        print("2. Register")
        print("3. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            self.login()
        elif choice == '2':
            self.register()
        elif choice == '3':
            print("Thank you for using the Bill Sharing App. Goodbye!")
            sys.exit(0)
        else:
            print("Invalid choice. Please try again.")

    def login(self):
        email = input("Enter your email: ")
        password = input("Enter your password: ")
        try:
            self.current_user = User.login(email, password, self.connector)
            print(f"Welcome, {self.current_user.name}!")
        except ValueError as e:
            print(f"Login failed: {e}")

    def register(self):
        name = input("Enter your name: ")
        email = input("Enter your email: ")
        password = input("Enter your password: ")
        try:
            self.current_user = User(name, email, password, connector=self.connector)
            print(f"Registration successful. Welcome, {self.current_user.name}!")
        except ValueError as e:
            print(f"Registration failed: {e}")

    def show_main_menu(self):
        print(f"\nHello, {self.current_user.name}!")
        print("1. Create a new group")
        #print("2. Join a group")
        print("2. View my groups")
        print("3. Manage a group")
        print("4. Manage expenses")
        print("5. Manage transactions")
        print("6. View dues")
        print("7. Logout")
        choice = input("Enter your choice: ")

        if choice == '1':
            self.create_group()
        elif choice == '2':
            self.view_groups()
        elif choice == '3':
            self.manage_group()
        elif choice == '4':
            self.manage_expenses()
        elif choice == '5':
            self.manage_transactions()
        elif choice == '6':
            self.view_dues()
        elif choice == '7':
            self.current_user = None
            print("Logged out successfully.")
        else:
            print("Invalid choice. Please try again.")

    def create_group(self):
        name = input("Enter group name: ")
        description = input("Enter group description (optional): ")
        try:
            group = Group(admin=self.current_user, name=name,members=[self.current_user], description=description, connector=self.connector)
            print(f"Group '{group.name}' created successfully with ID: {group.group_id}")
            group.add_member(self.current_user.user_id)

        except ValueError as e:
            print(f"Group creation failed: {e}")

    

    def view_groups(self):
        group_ids = self.current_user.get_groups()
        if not group_ids:
            print("You are not a member of any groups.")
            return

        print("Your groups:")
        for group_id in group_ids:
            group = Group.get_group(group_id, self.connector)
            print(f"ID: {group.group_id}, Name: {group.name}")

    def manage_group(self):
        group_id=input("entr the id of thr group you want to manage: ")

        try:
            group = Group.get_group(group_id, self.connector)
            if group.admin.user_id != self.current_user.user_id:
                print("You are not the admin of this group.")
                return
            self.show_group_management_menu(group)
        except ValueError as e:
            print(f"Failed to retrieve group: {e}")

    def show_group_management_menu(self, group):
        while True:
            print(f"\nManaging group: {group.name}")
            print("1. Add member")
            print("2. Add members")
            print("3. Remove member")
            print("4. Change group name")
            print("5. Change group description")
            print("6. View members")
            
            print("7. Back to main menu")
            choice = input("Enter your choice: ")

            if choice == '1':
                self.add_member_to_group(group)
            elif choice == '2':
                self.add_multiple_members_to_group(group)
            elif choice == '3':
                self.remove_member_from_group(group)
            elif choice == '4':
                self.change_group_name(group) 
            elif choice == '5':
                self.change_group_description(group)
            elif choice == '6':
                self.view_group_members(group)
            elif choice == '7':
                break
            else:
                print("Invalid choice. Please try again.")

    def add_member_to_group(self, group:Group):
        email = input("Enter the email of the user you want to add: ")
        try:
            user = User.get_user_by_email(email, self.connector)  # Using
            group.add_member(user.user_id)
            print(f"{user.name} has been added to the group.")
        except ValueError as e:
            print(f"Failed to add member: {e}")

    def add_multiple_members_to_group(self,group:Group):
        group_id = input("Enter the ID of the group you want to add members to: ")
        

        emails = input("Enter the emails of the users you want to add (comma-separated): ").split(',')
        emails = [email.strip() for email in emails]  # Remove any whitespace

        user_ids = []
        for email in emails:
            try:
                user = User.get_user_by_email(email, self.connector) # Using login method to retrieve user
                user_ids.append(user.user_id)
            except ValueError as e:
                print(f"Failed to find user with email {email}: {e}")

        if user_ids:
            group.add_members(user_ids)
            print(f"Successfully added {len(user_ids)} members to the group.")
        else:
            print("No valid users to add.")

   

    def remove_member_from_group(self, group:Group):
        email = input("Enter the email of the user you want to remove: ")
        try:
            user = User.get_user_by_email(email, self.connector)
            group.remove_member(user.user_id)
            print(f"{user.name} has been removed from the group.")
        except ValueError as e:
            print(f"Failed to remove member: {e}")

    def change_group_name(self, group:Group):
        new_name = input("Enter the new name for the group: ")
        try:
            group.name = new_name
            print(f"Group name has been changed to '{new_name}'")
        except ValueError as e:
            print(f"Failed to change group name: {e}")

    def change_group_description(self, group:Group):
        new_description = input("Enter the new description for the group: ")
        try:
            group.description = new_description
            print("Group description has been updated.")
        except ValueError as e:
            print(f"Failed to change group description: {e}")

    def view_group_members(self, group:Group):
        print(f"Members of group '{group.name}':")
        for member in group.members:
            print(f"- {member.name} (Email: {member.email})")
    
    def manage_expenses(self):
        while True:
            print("\nExpense Management")
            print("1. Add an expense")
            print("2. Edit an expense")
            print("3. Delete an expense")
            print("4. View expenses")
            print("5. Split an expense")
            print("6. Back to main menu")
            choice = input("Enter your choice: ")

            if choice == '1':
                self.add_expense()
            elif choice == '2':
                self.edit_expense()
            elif choice == '3':
                self.delete_expense()
            elif choice == '4':
                self.view_expenses()
            elif choice == '5':
                self.split_expense()
            elif choice == '6':
                break
            else:
                print("Invalid choice. Please try again.")

    


    def add_expense(self):
        group_id = input("Enter the group ID for this expense: ")
        try:
            group = Group.get_group(group_id, self.connector)
            amount = float(input("Enter the total expense amount: "))
            description = input("Enter a description for the expense: ")
            tag = input("Enter a tag for the expense (optional): ")
            
            participants = {}
            participants[self.current_user] = amount
            for member in group._members:
                if member.user_id != self.current_user.user_id:
                    participants[member] =0.0
            
            expense = Expense(amount=amount, payer=self.current_user, group=group,
                              participants=participants, description=description,
                              tag=tag, connector=self.connector)
            print(f"Expense added successfully with ID: {expense.expense_id}")
        except ValueError as e:
            print(f"Failed to add expense: {e}")

    


    def edit_expense(self):
        expense_id = input("Enter the ID of the expense you want to edit: ")
        try:
            expense = Expense.get_expense(expense_id, self.connector)
            if self.current_user.user_id == expense.payer.user_id:
                print(f"Current expense details: {expense}")
                
                amount = float(input("Enter new amount (press enter to keep current): ") or expense.amount)
                description = input("Enter new description (press enter to keep current): ") or expense.description
                tag = input("Enter new tag (press enter to keep current): ") or expense.tag
                
                participants = {}
                for user in expense.participants:
                    amount_owed = float(input(f"Enter new amount owed by {user.name} (press enter to keep current): ") or expense.participants[user])
                    participants[user] = amount_owed

                expense.edit_expense(amount=amount, description=description, tag=tag, participants=participants)
                print("Expense updated successfully.")
                print(f"\nUpdated Split details for expense '{expense.description}':")
                print(f"Total amount: {expense.amount:.2f}")
                print(f"Payer: {expense.payer.name}")
                print("\nSplit:")
                for participant, amount in expense.participants.items():
                    print(f"{participant.name}: {amount:.2f}")
            else:
                print(" Can't edit expense You are not the payer")
        except ValueError as e:
            print(f"Failed to edit expense: {e}")

    def delete_expense(self):
        expense_id = input("Enter the ID of the expense you want to delete: ")
        try:
            expense = Expense.get_expense(expense_id, self.connector)
            if self.current_user.user_id == expense.payer.user_id:
                expense.delete_expense()
                print(f"Expense {expense_id} has been successfully deleted.")
            else:
                print("Can't delete expense You are not the payer")
        except ValueError as e:
            print(f"Failed to delete expense: {e}")
        except Exception as e:
            print(f"An error occurred while deleting the expense: {e}")

    def view_expenses(self):

        group_id = input("Enter the group ID to view expenses: ")
        try:
            if group_id:
                expenses = Expense.get_group_expenses(group_id, self.connector)
            else:
                user_groups = self.current_user.get_groups()
                expenses = []
                for group_id in user_groups:
                    expenses.extend(Expense.get_group_expenses(group_id, self.connector))
            
            if not expenses:
                print("No expenses found.")
            else:
                for expense in expenses:
                    print(f"ID: {expense.expense_id}, Amount: ${expense.amount:.2f}, "
                          f"Payer: {expense.payer.name}, Description: {expense.description}, "
                          f"Tag: {expense.tag}, Group: {expense.group.name}")
        except ValueError as e:
            print(f"Failed to retrieve expenses: {e}")

    
    def split_expense(self):
        expense_id = input("Enter the ID of the expense you want to split: ")
        try:
            expense = Expense.get_expense(expense_id, self.connector)
            if self.current_user.user_id == expense.payer.user_id:
                print(f"Current expense details: {expense}")
                
                print("Choose split method:")
                print("1. Equal")
                print("2. Unequal")
                print("3. Percentages")
                split_method = input("Enter your choice (1/2/3): ")
                
                participants = list(expense.participants.keys())
                
                if split_method == '1':
                    expense.calculate_and_split_expense('equal', participants)
                elif split_method == '2':
                    amounts = []
                    for participant in participants:
                        if participant.user_id == self.current_user.user_id:
                            amount = float(input(f"Enter your share amount: "))
                            amounts.append(amount)
                        else:
                            amount = float(input(f"Enter  share amount for {participant.name}: "))
                            amounts.append(amount)
                    expense.calculate_and_split_expense('unequal', participants, amounts=amounts)
                elif split_method == '3':
                    percentages = []
                    for participant in participants:
                        if participant.user_id == self.current_user.user_id:
                            amount = float(input(f"Enter your share percentage: "))
                            amounts.append(amount)
                        else:
                            amount = float(input(f"Enter share percentage for {participant.name}: "))
                            amounts.append(amount)
                    expense.calculate_and_split_expense('percentages', participants, percentages=percentages)
                else:
                    print("Invalid choice. Split cancelled.")
                    return

                # Mark the payer as settled in the ExpenseParticipants table
                new_amount = 0.00
                update_query = "UPDATE ExpenseParticipants SET settled = 'SETTLED' WHERE expense_id = %s AND user_id = %s"
                self.connector.execute(update_query, (expense_id, expense.payer.user_id))
                update_query = "UPDATE ExpenseParticipants SET amount = %s WHERE expense_id = %s AND user_id = %s"
                self.connector.execute(update_query, (new_amount,expense_id, expense.payer.user_id))

                print("Expense split successfully.")
                print(f"\nSplit details for expense '{expense.description}':")
                print(f"Total amount: {expense.amount:.2f}")
                print(f"Payer: {expense.payer.name} (Settled)")
            else:
                print("Can't split expense. You are not the payer")
            
            
        except ValueError as e:
            print(f"Failed to split expense: {e}")

    def manage_transactions(self):
        while True:
            print("\nTransaction Management")
            print("1. Create a new transaction")
            print("2. View transactions for an expense")
            print("3. View your transactions")
            print("4. Delete a transaction")
            print("5. Back to main menu")
            choice = input("Enter your choice: ")

            if choice == '1':
                self.create_transaction()
            elif choice == '2':
                self.view_transactions_for_expense()
            elif choice == '3':
                self.view_user_transactions()
            elif choice == '4':
                self.delete_transaction()
            elif choice == '5':
                break
            else:
                print("Invalid choice. Please try again.")

    def create_transaction(self):
        expense_id = input("Enter the expense ID for this transaction: ")
        try:
            expense = Expense.get_expense(expense_id, self.connector)
            
            # Check if the current user is a participant in the expense
            c=0
            for member in expense.participants:
                if member.user_id == self.current_user.user_id:
                    c=1
            if c == 1:
                # Check if the expense is already settled for the current user
                query = "SELECT settled FROM ExpenseParticipants WHERE expense_id = %s AND user_id = %s"
                result = self.connector.execute(query, (expense_id, self.current_user.user_id), fetchall=False)
                if result['settled'] == 'SETTLED':
                    print("You have already settled this expense.")
                    return

                # Get the amount owed by the current user
                for member in expense.participants:
                    if member.user_id == self.current_user.user_id:
                        amount_owed =float(expense.participants[member])

                if amount_owed <= 0:
                    print("You don't owe any money for this expense.")
                    return

                print(f"You owe {amount_owed:.2f} for this expense.")
                amount = float(input("Enter the amount you want to pay (must be less than or equal to the amount owed): "))

                if amount > amount_owed:
                    print("You cannot pay more than you owe.")
                    return

                transaction = Transaction(expense=expense, payer=self.current_user, payee=expense.payer, amount=amount, connector=self.connector)
                print(f"Transaction created successfully with ID: {transaction.trans_id}")

                # Update the ExpenseParticipants table
                new_amount_owed = amount_owed - amount
                new_status = 'SETTLED' if new_amount_owed == 0 else 'PARTIAL'
                update_query = "UPDATE ExpenseParticipants SET amount = %s, settled = %s WHERE expense_id = %s AND user_id = %s"
                self.connector.execute(update_query, (new_amount_owed, new_status, expense_id, self.current_user.user_id))

                # Check if the expense is fully settled
                check_settled_query = "SELECT COUNT(*) as count FROM ExpenseParticipants WHERE expense_id = %s AND settled != 'SETTLED'"
                result = self.connector.execute(check_settled_query, (expense_id,), fetchall=False)
                if result['count'] == 0:
                    print("This expense is now fully settled.")
            else:
                print("You are not a participant")
        except ValueError as e:
            print(f"Failed to create transaction: {e}")
    
    def view_transactions_for_expense(self):
        expense_id = input("Enter the expense ID to view its transactions: ")
        try:
            expense = Expense.get_expense(expense_id, self.connector)
            if self.current_user.user_id == expense.payer.user_id:
                transactions = Transaction.get_transactions_for_expense(expense)
                if not transactions:
                    print("No transactions found for this expense.")
                else:
                    for transaction in transactions:
                        print(transaction)
            else:
                print("Can't view transactions as you are not the payer")
        except ValueError as e:
            print(f"Failed to retrieve transactions: {e}")

    def view_user_transactions(self):
        start_date = input("Enter start date (YYYY-MM-DD) or press enter to skip: ")
        end_date = input("Enter end date (YYYY-MM-DD) or press enter to skip: ")
        
        start_datetime = datetime.strptime(start_date, "%Y-%m-%d") if start_date else None
        end_datetime = datetime.strptime(end_date, "%Y-%m-%d") if end_date else None

        try:
            transactions = Transaction.get_transactions_for_user(self.current_user, start_datetime, end_datetime)
            if not transactions:
                print("No transactions found.")
            else:
                for transaction in transactions:
                    print(transaction)
        except ValueError as e:
            print(f"Failed to retrieve transactions: {e}")

    def delete_transaction(self):
        trans_id = input("Enter the ID of the transaction you want to delete: ")
        try:
            transaction = Transaction.get_transaction(trans_id, self.connector)
            transaction.delete()
            update_query = "UPDATE ExpenseParticipants SET amount = %s, settled = %s WHERE expense_id = %s AND user_id = %s"
            self.connector.execute(update_query, (transaction._amount, 'NO',transaction._expense.expense_id , self.current_user.user_id))
            print("Transaction deleted successfully.")
        except ValueError as e:
            print(f"Failed to delete transaction: {e}")

    def view_dues(self):
        print("\nYour current dues:")
        query = """
        SELECT e.expense_id, e.description, e.amount, ep.amount as owed_amount, g.name as group_name
        FROM Expenses e
        JOIN ExpenseParticipants ep ON e.expense_id = ep.expense_id
        JOIN GroupDetails g ON e.group_id = g.group_id
        WHERE ep.user_id = %s AND ep.settled != 'SETTLED'
        """
        dues = self.connector.execute(query, (self.current_user.user_id,))
        
        if not dues:
            print("You don't have any outstanding dues.")
        else:
            for due in dues:
                print(f"Expense ID: {due['expense_id']}")
                print(f"Description: {due['description']}")
                print(f"Total Amount: ${due['amount']:.2f}")
                print(f"You Owe: ${due['owed_amount']:.2f}")
                print(f"Group: {due['group_name']}")
                print("---")

    

if __name__ == "__main__":
    app = BillSharingApp()
    app.start()

