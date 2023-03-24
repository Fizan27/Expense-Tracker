import sys
import copy

"""
-> flexibility with month 
-> changed the month to title case 
-> multiple classes 
-> negative income claculations
-> data is not stored
-> need a database & login system 
"""

"""
UI 
// friday -> login 
-> login page 
    -> register -> email; username ...
    -> log in -> email : password 
if the user is alredy in the db 
    -> Page 1 : Current State -> table ( Stats) ( already a user ) 
else : 
 -> form 
 -> Page 1 

Page 1 : 
    -> Enter data for another month -> form -> update the Status page 
    -> Do you want to change your prefs -> form with pre-filled data ( previous state ) 
    -> ask them to modify 
    -> check if the user has changed anything 
    -> if yes : notify saying that they have changed it and update the db
    -> do you want an email of the report -> yes -> email else don't generate the report at all 

form -> webpage // user interface 
ExpenseTracker class 
class Expenses 
class wants implements Expenses
class need implements Expenses 
class login 
    __init__
        username 
        password -> hash 
        name
        email 
    register 
        ....
    changePassword 
        ...
    ....
    ....
class Database 
    __init__
        ....
    once the user logins -> create a table 
    ------
    how are represent the data 
    ------
    duplicate data -> username ( no duplicate usernames) 




"""


class ExpenseTracker:
    """Creates a expense tracker object"""

    def __init__(self):
        self._income = 0
        self._needs_list = ["Rent", "Utilities - Water and Electricity", "Groceries", "Gas", "Pets", "Other Needs"]
        self._wants_list = ["Dining Out", "Vacation", "TV/Streaming Services", "Clothing, shoes, accessories"]
        self._new_income = 0
        self._month_tracker = {"January": {}, "February": {}, "March": {}, "April": {}, "May": {}, "June": {},
                               "July": {}, "August": {}, "September": {}, "October": {}, "November": {},
                               "December": {}}
        self._needs_cost = 0
        self._wants_cost = 0
        self._month = None
        self._save_invest = ["Save/Invest"]
        self._target = 0
        self._new_dict = {}
        self._list_of_expenses = []
        self._cant_cut = 0
        self._ideal_budget = {"January": {}, "February": {}, "March": {}, "April": {}, "May": {}, "June": {},
                              "July": {}, "August": {}, "September": {}, "October": {}, "November": {},
                              "December": {}}
        self._month_list = ["January", "February", "March", "April", "May", "June",
                            "July", "August", "September", "October", "November",
                            "December"]

    def initial_income(self):
        """User enters their total income and the month that this income was from"""
        while True:
            try:
                self._income = int(input("What is your monthly take home income after taxes? "))
            except ValueError:
                print("You did not enter a number. Try again.")
            else:
                break
        self._new_income = self._income
        print("What month are you tracking data for?")
        while True:
            try:
                self._month = input()
                if self._month not in self._month_list:
                    raise MonthNotEnteredCorrectly
                # what if I enter a integer -> 1 for jan ect.
            except MonthNotEnteredCorrectly:
                print("You did not enter the month correctly")
            else:
                break
        self.expense_list_creation()

    def expense_list_creation(self):
        """Assigns values entered by the user to the various different expenses from the needs list"""
        expense = 0
        print("Needs Expenses:")
        while expense < len(self._needs_list):
            try:
                new_expense = int(input(self._needs_list[expense]))
            except ValueError:
                print("You did not enter a number. Try again.")
            else:
                self._new_income -= int(new_expense)
                self._month_tracker[self._month][self._needs_list[expense]] = [new_expense]
                self._needs_cost = self._new_income
                print("How high priority is this expense?, Enter p for an expense you cannot cut costs on, enter "
                      "lp on an expense you could possibly cut down on a little bit, enter np on an expense"
                      "that you could completely cut out if needed")
                priority = input()
                self._month_tracker[self._month][self._needs_list[expense]].append(priority)
                expense += 1
                print(new_expense)
        self.wants_list_creation()

    def wants_list_creation(self):
        """Assigns values entered by the user to the various different expenses from the wants list"""
        expense = 0
        print("Wants Expenses:")
        while expense < len(self._wants_list):
            try:
                new_expense = int(input(self._wants_list[expense]))
            except ValueError:
                print("You did not enter a number. Try again.")
            else:
                self._new_income -= int(new_expense)
                self._month_tracker[self._month][self._wants_list[expense]] = [new_expense]
                self._needs_cost = self._new_income
                print(new_expense)
                print("How high priority is this expense?, Enter p for an expense you cannot cut costs on, enter "
                      "lp on an expense you could possibly cut down on a little bit, enter np on an expense"
                      "that you could completely cut out if needed")
                priority = input()
                self._month_tracker[self._month][self._wants_list[expense]].append(priority)
                expense += 1
        print(self._month_tracker)
        print(self._new_income)
        self.needs_and_wants_tracker()

    def needs_and_wants_tracker(self):
        """Adds up and tracks the amount of expenses the user has and how much they have left after"""
        if self._new_income >= 1:
            print("You have $", self._new_income, "left over after necessities and wants.")
        elif self._new_income <= -1:
            print("You are $", abs(self._new_income), "over budget we'll look at some ways to cut costs later.")
        else:
            print("You have spent your entire budget we'll look at some ways to cut costs later.")
        self.debt_tracker()

    def debt_tracker(self):
        """Used to calculate how much money users should put towards their debt and has the user enter their
             current debt payments"""
        print("Ideally your debt payments should be 20% of your income, however if needed it should be at most 36% "
              "of your income")
        have_debt = (input("Do you have any debt? y/n "))
        total_debt = 0
        debt_track = ["Debt"]
        if have_debt == "n":
            print("Congratulations you don't have to worry about debt so you can put more money towards"
                  " saving or investments.")
        else:
            debt = 0
            print("Please enter your various monthly payments for your debt here. If all have been entered type no. ")
            while debt != "no":
                total_debt += int(debt)
                debt = input()
            print("You have $", total_debt, "in debt")
            self._month_tracker[self._month][debt_track[0]] = [total_debt]
            debt_percent = (total_debt / self._income) * 100
            self._new_income -= total_debt
            self._cant_cut += total_debt
            print(self._month_tracker)

            if debt_percent > 20:
                print("Your debt makes up ", debt_percent, "% of your income")
                print("Your debt is high ideally you need to cut this down to a more manageable percent"
                      " let's look at some ways we can do this")
            else:
                print("Your debt makes up ", debt_percent, "% of your income")
                print("Your debt doesn't make up too high of percent of your income, however it is important"
                      " to focus on paying off debt if possible")
        self.investment_and_save_recs()

    def investment_and_save_recs(self):
        """Used to calculate how much the user should save/invest and lets them enter how much they would like
            to save and invest"""
        if self._new_income > self._income // 5:
            invest_1 = self._income // 10
            invest_2 = self._income // 5
            print(
                "It is recommended to invest or save 10-20% of your income. You should try to invest and/or save "
                "at "
                "least 10% of your income which is $", invest_1, "or if possible you should try to invest "
                                                                 "and/or save 20% or more of your income which is $"
                , invest_2, ".")
            print("Knowing this how much would you like to put towards your savings"
                  " and investments. Remember that you currently have,", self._new_income, "left currently"
                                                                                           " and that this amount will not be changed later on")
            while True:
                try:
                    amount_saved = int(input())
                except ValueError:
                    print("You did not enter a number. Try again.")
                else:
                    try:
                        if amount_saved > self._income - self._cant_cut:
                            raise NotEnoughMoney
                    except NotEnoughMoney:
                        print("You do not have enough money to save that amount")
                    else:
                        self._month_tracker[self._month][self._save_invest[0]] = [amount_saved]
                        self._new_income -= int(amount_saved)
                        self._cant_cut += amount_saved
                        break

        elif self._new_income > self._income // 10:
            invest_1 = self._income // 10
            print("It is recommended that you invest about $", invest_1)
            print("Knowing this how much would you like to put towards your savings"
                  " and investments. Remember that you currently have,", self._new_income, "left currently"
                                                                                           " and that this amount will not be changed later on")
            while True:
                try:
                    amount_saved = int(input())
                except ValueError:
                    print("You did not enter a number. Try again.")
                else:
                    try:
                        if amount_saved >= self._income - self._cant_cut:
                            raise NotEnoughMoney
                    except NotEnoughMoney:
                        print("You do not have enough money to save that amount")
                    else:
                        self._month_tracker[self._month][self._save_invest[0]] = [amount_saved]
                        self._new_income -= int(amount_saved)
                        self._cant_cut += amount_saved
                        break
        else:
            print("Unfortunately you do not have enough to save 10% or more of your income. We will look"
                  " at ways to cut costs so that you will be able to put some more money towards saving")
        self.priority()

    def needs(self):
        """Tells the user what percent of their income that their needs make up"""
        save_needs = (self._needs_cost / self._income) * 100
        needs_percent = 100 - save_needs
        if needs_percent > 50:
            print("Your needs make up", needs_percent, "% of your income, ideally your needs should make up 50%"
                                                       " of your income. We should look at some ways"
                                                       "we could cut this down to make it more manageable")
        else:
            print("Your needs make up", needs_percent, "of your income.  Which is ideal since wants should"
                                                       " make up 50% of your income or less")

    def wants(self):
        """Tells the user what percent of their income that their wants make up"""
        save_wants = (self._wants_cost / self._income) * 100
        wants_percent = 100 - save_wants
        if wants_percent > 30:
            print("Your wants make up"), wants_percent, "% of your income ideally your wants should make up " \
                                                        "30% of your income. We should look at some ways we" \
                                                        "could cut this down to make if more manageable"
        else:
            print("Your wants make up", wants_percent, "of your income. Which is ideal since wants should"
                                                       "make up 30% of your income or less")

    def priority(self):
        """Checks to see if any expenses are deemed priority, if they are it will add those costs to the expenses
            that cannot be cut"""
        for expense in self._needs_list:
            if self._month_tracker[self._month][expense][1] == "p":
                self._cant_cut += self._month_tracker[self._month][expense][0]
        for expense in self._wants_list:
            if self._month_tracker[self._month][expense][1] == "p":
                self._cant_cut += self._month_tracker[self._month][expense][0]
        self.cost_cut()

    def cost_cut(self):
        """If the user has more than $0 left at this point it will ask them if they would like to cut costs
           if they have less than 0 it'll automatically prompt them for their target amount of money leftover
           from there it'll call various functions until costs are cut"""
        if self._new_income > 0:
            print("It seems like you are on track with your budget, would you still like to look"
                  " at some ways you could cut costs. y/n")
            go_on = input()
            if go_on == "n":
                print("Congratulations you have done a good job budgeting to ensure you can meet your needs"
                      " and save")
                self.month_budget_finder()

            else:
                print("How much money would you like to have leftover after cutting costs")
                while True:
                    try:
                        self._target = int(input())
                    except ValueError:
                        print("That is not a number try again")
                    else:
                        try:
                            if self._target >= self._income - self._cant_cut:
                                raise NotEnoughMoney
                        except NotEnoughMoney:
                            print("You do not have enough money to save that amount")
                        else:
                            break
                self.needs_cost_cut_np()
                self.wants_cost_cut_np()
                self.needs_cost_cut_lp()
                self.wants_cost_cut_lp()
        elif self._cant_cut >= self._income:
            print("I'm sorry it is impossible to cut costs because you have to high amount listed as priority"
                  " please try again and reconsider the priority of your expenses")
            self.enter_more()
        else:
            print("How much money would you like to have leftover after cutting costs")
            while True:
                try:
                    self._target = int(input())
                except ValueError:
                    print("That is not a number try again")
                else:
                    try:
                        if self._target >= self._income - self._cant_cut:
                            raise NotEnoughMoney
                    except NotEnoughMoney:
                        print("You do not have enough money to cut")
                    else:
                        break
            self.needs_cost_cut_np()
            self.wants_cost_cut_np()
            self.needs_cost_cut_lp()
            self.wants_cost_cut_lp()
        self.wants_priority()

    def needs_cost_cut_np(self):
        """Cuts costs completely for any needs expense labeled no priority or np"""
        for expense in self._needs_list:
            if self._month_tracker[self._month][expense][1] == "np":
                if self._new_income >= self._target:
                    print("Congratulations you have met your goal")
                    print("If you cut", self._list_of_expenses, "you will be at", self._new_income, "saved")
                    self.enter_more()
                else:
                    self._new_income += self._month_tracker[self._month][expense][0]
                    self._list_of_expenses.append(expense)

    def wants_cost_cut_np(self):
        """Cuts costs completely for any wants expense labeled no priority or np"""
        for expense in self._wants_list:
            if self._month_tracker[self._month][expense][1] == "np":
                if self._new_income >= self._target:
                    print("Congratulations you have met your goal")
                    print("If you cut", self._list_of_expenses, "you will be at", self._new_income, "saved")
                    self.enter_more()
                else:
                    self._new_income += self._month_tracker[self._month][expense][0]
                    self._list_of_expenses.append(expense)

    def needs_cost_cut_lp(self):
        """Has the user rate their needs on a scale of 1-10 to determine what order the costs are cut in"""
        print("Please rate all of your low priority expenses on a scale of 1-10. 1 being least important"
              " and 10 being most important. Your wants will automatically be treated as lower priority "
              " then your needs.")
        expense = 0
        while expense < len(self._needs_list):
            if self._month_tracker[self._month][self._needs_list[expense]][1] == "lp":
                print("Please rate this expense, " + self._needs_list[expense])
                try:
                    rating = int(input())
                except ValueError:
                    print("You did not enter a number")
                else:
                    self._month_tracker[self._month][self._needs_list[expense]].append(rating)
                    expense += 1
            else:
                expense += 1

    def wants_cost_cut_lp(self):
        """Has the user rate their wants on a scale of 1-10 to determine what order the costs are cut in"""
        expense = 0
        while expense < len(self._wants_list):
            if self._month_tracker[self._month][self._wants_list[expense]][1] == "lp":
                print("Please rate this expense, " + self._wants_list[expense])
                try:
                    rating = int(input())
                except ValueError:
                    print("You did not enter a number")
                else:
                    self._month_tracker[self._month][self._wants_list[expense]].append(rating)
                    expense += 1
            else:
                expense += 1

    def needs_priority(self):
        """Adds all the low priority needs to a new dictionary, so they can then be cut in correct order according
          to priority"""
        rate = 0
        expense = 0
        while rate < 10:
            while expense < len(self._needs_list):
                if self._month_tracker[self._month][self._needs_list[expense]][1] == "lp":
                    if self._month_tracker[self._month][self._needs_list[expense]][2] == rate:
                        self._new_dict[self._needs_list[expense]] = \
                            self._month_tracker[self._month][self._needs_list[expense]][0]
                    expense += 1
                else:
                    expense += 1
            rate += 1
            expense = 0
        self.lp_cost_cut()

    def wants_priority(self):
        """Adds all the low priority wants to a new dictionary, so they can then be cut in correct order according
          to priority"""
        rate = 0
        expense = 0
        while rate < 10:
            while expense < len(self._wants_list):
                if self._month_tracker[self._month][self._wants_list[expense]][1] == "lp":
                    if self._month_tracker[self._month][self._wants_list[expense]][2] == rate:
                        self._new_dict[self._wants_list[expense]] = \
                            self._month_tracker[self._month][self._wants_list[expense]][0]
                    expense += 1
                else:
                    expense += 1
            rate += 1
            expense = 0
        self.needs_priority()

    def lp_cost_cut(self):
        """Cuts the low priority costs by a certain percent until the amount of money leftover equals the goal"""
        cut = 0.25
        times_run = 0
        while self._target > self._new_income or times_run != 100:
            for expense in self._new_dict.keys():
                self._new_income += round(self._new_dict[expense] * cut)
                self._new_dict[expense] -= round(self._new_dict[expense] * cut)
                times_run += 1
                if self._target <= self._new_income:
                    print(self._new_dict)
                    print(self._new_income)
                    self.needs_results()
            if cut >= 0.06:
                cut -= 0.05
        self.needs_results()

    def needs_results(self):
        """Displays the results for what they should cut their needs by in order to reach goal"""
        for expense in self._needs_list:
            for expense_1 in self._new_dict.keys():
                if expense == expense_1:
                    saved = self._month_tracker[self._month][expense][0] - self._new_dict[expense_1]
                    print("You should cut", expense, "by", saved, "to help you meet your budget")
        self.wants_results()

    def wants_results(self):
        """Displays the results for what they should cut their wants by in order to reach goal"""
        for expense in self._wants_list:
            for expense_1 in self._new_dict.keys():
                if expense == expense_1:
                    saved = self._month_tracker[self._month][expense][0] - self._new_dict[expense_1]
                    print("You should cut", expense, "by", saved, "to help you meet your budget")
        self.ideal_budget_needs()

    def ideal_budget_needs(self):
        """Creates a copy of their dictionary showing the ideal budget for their n
        needs should look like after the costs are cut"""
        self._ideal_budget = copy.deepcopy(self._month_tracker.copy())
        for expense in self._needs_list:
            if self._ideal_budget[self._month][expense][1] == "np":
                self._ideal_budget[self._month][expense][0] = 0
            elif self._ideal_budget[self._month][expense][1] == "lp":
                for expense_1 in self._new_dict.keys():
                    if expense == expense_1:
                        self._ideal_budget[self._month][expense][0] = self._new_dict[expense_1]
        self.ideal_budget_wants()

    def ideal_budget_wants(self):
        """Creates a copy of the original dictionary showing the ideal budget for their wants
        should look like after the costs are cut"""
        for expense in self._wants_list:
            if self._ideal_budget[self._month][expense][1] == "np":
                self._ideal_budget[self._month][expense][0] = 0
            elif self._ideal_budget[self._month][expense][1] == "lp":
                for expense_1 in self._new_dict.keys():
                    if expense == expense_1:
                        self._ideal_budget[self._month][expense][0] = self._new_dict[expense_1]
        self.display_comparison()

    def display_comparison(self):
        """Displays the difference between the dictionaries for the user"""
        print("Here is your current budget,", self._month_tracker[self._month], "and this is what your budget"
                                                                                " could look like",
              self._ideal_budget[self._month])
        self.month_budget_finder()

    def month_budget_finder(self):
        """Asks them if they would like to see the budget for another month"""
        print("Please enter the month that you would like to see your data for")
        month_lookup = input()
        for month in self._month_tracker:
            if month_lookup == month:
                print(self._month_tracker[month_lookup])
        self.enter_more()

    def enter_more(self):
        """Allows the user to enter data for other months if they would like to"""
        print("Thank you so much for using budget finder would you like to enter data for another month? (y/n)")
        track_more = input()
        if track_more == "y":
            self.initial_income()
        elif track_more == "n":
            sys.exit(print("Thank you so much for using budget tracker comeback next month to continue to stay on track"
                           " with your budget"))


class NotEnoughMoney(Exception):
    """Is raised if the user does not have enough money to do what they want"""
    pass


class MonthNotEnteredCorrectly(Exception):
    """Raised if the month entered is not entered correctly"""
    pass


def main():
    tracker = ExpenseTracker()
    tracker.initial_income()
    print(tracker._income)


if __name__ == "__main__":
    main()
