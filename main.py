import pymssql
import sys
import datatier_azure as da
from datetime import date
import csv
import os

servername = 'walteryang.database.windows.net'
login = 'ReadWriteUser'
pwd = 'nu!cs2022'
dbname = 'SP500'

print('**Trying to connect to SP500 in Microsoft Azure cloud...')
print()

try:
  dbConn = pymssql.connect(server=servername,
                           user=login,
                           password=pwd,
                           database=dbname)
  print("**connected!")
except Exception as err:
  print("Error:", err)
  print("failed to connect :-(")
  sys.exit()
finally:
  print()

############################################################################################
##System Setup
##set up the system date, fixed to be 11/23/2022
sys_date = date(2022, 11, 23)
##Check current date
actual_date = date.today()

############################################################################################
##Functions


##[Fuction 1]: Check existing users in the system and return the list
##if opt is set to "Y", it will just print out the list
def check_user(opt):
  sql = """select u.usertable_id, u.usertable_name, r.role, u.account_id, s.status
            from USERTABLE u
            inner join Role r on u.role_id=r.role_id
            inner join status s on u.status_id=s.status_id
            order by u.usertable_id asc;
            ;"""
  userlist = da.select_n_rows(dbConn, sql)
  if userlist is not None:
    if opt == "Y":
      print()
      print("Users in the system:")
      print("UserID\t UserName\t Role\t AcctID\t Status")
      start_page = 0
      end_page = 10
      while start_page < len(userlist):
        for row in userlist[start_page:end_page]:
          print(row[0], "\t\t", row[1], "\t", row[2], "\t", row[3], "\t",
                row[4])
        if end_page > len(userlist):
          break
        print()
        more = input("Display more? [yes/no] ")
        if more == "y" or more == "yes":
          start_page += 10
          end_page += 10
          continue
        else:
          break
    else:
      return userlist


##[Function 2]: Search a particur user in the system and return the search results
def search_user(opt, parameters):
  if opt == "1":  #search by ID
    sql = """select u.usertable_id, u.usertable_name, r.role, u.account_id, s.status
              from USERTABLE u
              inner join Role r on u.role_id=r.role_id
              inner join status s on u.status_id=s.status_id
              where u.usertable_id like %d
              order by u.usertable_id asc;
              ;"""
    search_results = da.select_n_rows(dbConn, sql, parameters=[parameters])
  elif opt == "2":  #search by name
    sql = """select u.usertable_id, u.usertable_name, r.role, u.account_id, s.status
              from USERTABLE u
              inner join Role r on u.role_id=r.role_id
              inner join status s on u.status_id=s.status_id
              where u.usertable_name like %d
              order by u.usertable_id asc;
              ;"""
    search_results = da.select_n_rows(dbConn, sql, parameters=[parameters])
  elif opt == "3":  #search by role
    sql = """select u.usertable_id, u.usertable_name, r.role, u.account_id, s.status
              from USERTABLE u
              inner join Role r on u.role_id=r.role_id
              inner join status s on u.status_id=s.status_id
              where r.role like %d
              order by u.usertable_id asc;
              ;"""
    search_results = da.select_n_rows(dbConn, sql, parameters=[parameters])
  elif opt == "4":  #search by status
    sql = """select u.usertable_id, u.usertable_name, r.role, u.account_id, s.status
              from USERTABLE u
              inner join Role r on u.role_id=r.role_id
              inner join status s on u.status_id=s.status_id
              where s.status like %d
              order by u.usertable_id asc;
              ;"""
    search_results = da.select_n_rows(dbConn, sql, parameters=[parameters])
  return search_results


##[Function 3]: Search function (Complete Version)
def search_function():
  check_user(opt="Y")
  print()
  sub_cmd = input("Please enter a command (s: search, b: go back): ")
  while sub_cmd != "b":
    if sub_cmd == "s":
      p = input("Enter search criteria (1: id, 2: name, 3: role, 4: status): ")
      if p == "1":
        term = input("Enter user ID (e.g. '%123%'): ")
      elif p == "2":
        term = input("Enter user name (e.g. '%John%'): ")
      elif p == "3":
        term = input("Enter user's role ('ADMIN','TRADER','MANAGER'): ")
      elif p == "4":
        term = input("Enter user's status ('ACTIVE','LOCKED'): ")

      try:
        search_results = search_user(p, term)
        print()
        print("Search results:")
        print("UserID\t UserName\t Role\t AcctID\t Status\t")
        start_page = 0
        end_page = 10
        while start_page < len(search_results):
          for row in search_results[start_page:end_page]:
            print(row[0], "\t\t", row[1], "\t", row[2], "\t", row[3], "\t",
                  row[4])
          if end_page > len(search_results):
            break
          print()
          more = input("Display more? [yes/no] ")
          if more == "y" or more == "yes":
            start_page += 10
            end_page += 10
            continue
          else:
            break
      except:
        print("**Error, unknown search criteria, try again...")

    else:
      print("**Error, unknown command, try again...")
    print()
    sub_cmd = input("Please enter a command (s: search, b: go back): ")


##[Function 4]: Add new user
def add_new_user():
  add_name = input("Enter user name: ")
  add_role = input("Enter user's role ('ADMIN','TRADER','MANAGER'): ")
  sub_sql = "select * from role;"
  list_of_role = da.select_n_rows(dbConn, sub_sql, parameters=[add_role])
  for row in list_of_role:
    if row[1] == add_role:
      tmp_role = row[0]

  ##Trading account won't open for user with role as Admin or Manager
  if add_role == 'ADMIN' or add_role == 'MANAGER':
    try:
      sql = "INSERT INTO [dbo].USERTABLE (USERTABLE_Name, Role_ID, Status_ID) VALUES (%s, %d, 1);"
      da.perform_action(dbConn, sql, parameters=[add_name, tmp_role])
      print()
      print("New user added!")
      print()
      sub_sql2 = """
      select u.usertable_id, u.usertable_name, r.role, u.account_id, s.status
      from USERTABLE u
      inner join Role r on u.role_id=r.role_id
      inner join status s on u.status_id=s.status_id
      where u.usertable_id = (select max(usertable_id) from USERTABLE);
      """
      new_user_info = da.select_one_row(dbConn, sub_sql2)
      print("UserID\t UserName\t Role\t AcctID\t Status\t")
      new_user_info = list(new_user_info)
      print(new_user_info[0], "\t\t", new_user_info[1], "\t", new_user_info[2],
            "\t", new_user_info[3], "\t", new_user_info[4])
    except:
      print("**Error, fail to add new user, try again...")
  ##Trading account must open for user with role as Trader
  elif add_role == 'TRADER':
    try:
      dbCursor = dbConn.cursor()
      dbCursor.execute('Set TRANSACTION Isolation level Serializable;')

      dbCursor.execute('INSERT INTO [dbo].BALANCE (Balance) VALUES (0);')
      dbCursor.execute('SELECT max(account_id) FROM balance;')
      row = dbCursor.fetchone()
      row = list(row)
      id = row[0]

      dbCursor.execute(
        "INSERT INTO [dbo].USERTABLE (USERTABLE_Name, Role_ID, Account_ID, Status_ID) VALUES (%s, %d, %s, 1);",
        (add_name, tmp_role, id))
      print()
      print("New user added!")
      print()
      sub_sql2 = """
      select u.usertable_id, u.usertable_name, r.role, u.account_id, s.status from USERTABLE u
      inner join Role r on u.role_id=r.role_id
      inner join status s on u.status_id=s.status_id
      where u.usertable_id = (select max(usertable_id) from USERTABLE);
      """
      new_user_info = da.select_one_row(dbConn, sub_sql2)
      print("UserID\t UserName\t Role\t AcctID\t Status\t")
      new_user_info = list(new_user_info)
      print(new_user_info[0], "\t\t", new_user_info[1], "\t", new_user_info[2],
            "\t", new_user_info[3], "\t", new_user_info[4])

      dbConn.commit()
    except Exception as err:
      print('Failed', ':', err)
      dbConn.rollback()
    finally:
      dbCursor.close()
  else:
    print("**Error, unknown user's role, try again...")


##[Function 5]: Modify user
def modify_user():
  print("modify user function starts")
  user_id = input("Enter user id: ")
  sub_sql = """
  select u.usertable_id, u.usertable_name, r.role, u.account_id, s.status
  from USERTABLE u
  inner join Role r on u.role_id=r.role_id
  inner join status s on u.status_id=s.status_id
  where u.usertable_id = %d;
  """
  user_info = da.select_one_row(dbConn, sub_sql, parameters=[user_id])
  user_info = list(user_info)
  if len(user_info) == 0:
    print("**Error, unknown user ID, try again...")
    return -1
  else:
    print("UserID\t UserName\t Role\t AcctID\t Status\t")
    print(user_info[0], "\t\t", user_info[1], "\t", user_info[2], "\t",
          user_info[3], "\t", user_info[4])
    sub_cmd = input(
      "Please enter a command (c: change user name; l: lock/unlock user; b: go back): "
    )
    while sub_cmd != "b":
      if sub_cmd == "c":
        new_name = input("Enter a new user name: ")
        try:
          dbCursor = dbConn.cursor()
          dbCursor.execute('Set TRANSACTION Isolation level Serializable;')
          dbCursor.execute(
            'UPDATE [dbo].USERTABLE SET usertable_name = %s where usertable_id = %d;',
            (new_name, user_id))
          print()
          print("User name updated!")
          print()
          s_user_info = search_user("1", user_id)
          print("UserID\t UserName\t Role\t AcctID\t Status\t")
          print(s_user_info[0][0], "\t\t", s_user_info[0][1], "\t",
                s_user_info[0][2], "\t", s_user_info[0][3], "\t",
                s_user_info[0][4])
          dbConn.commit()
        except Exception as err:
          print('Failed', ':', err)
          dbConn.rollback()
        finally:
          dbCursor.close()
      elif sub_cmd == "l":
        print()
        print("Current user's status is %s" % user_info[4])
        if user_info[4] == "ACTIVE":
          opt = input("Do you want to lock this account? [yes/no] ")
          if opt == "y" or opt == "yes":
            try:
              dbCursor = dbConn.cursor()
              dbCursor.execute('Set TRANSACTION Isolation level Serializable;')
              dbCursor.execute(
                'UPDATE [dbo].USERTABLE SET status_id = 2 where usertable_id = %d;',
                (user_id, ))
              print()
              print("Account has been locked!")
              print()
              user_info = search_user("1", user_id)
              print("UserID\t UserName\t Role\t AcctID\t Status\t")
              print(user_info[0][0], "\t\t", user_info[0][1], "\t",
                    user_info[0][2], "\t", user_info[0][3], "\t",
                    user_info[0][4])
              dbConn.commit()
            except Exception as err:
              print('Failed', ':', err)
              dbConn.rollback()
            finally:
              dbCursor.close()
              break
          else:
            break
        elif user_info[4] == "LOCKED":
          opt = input("Do you want to re-activate this account? [yes/no] ")
          if opt == "y" or opt == "yes":
            try:
              dbCursor = dbConn.cursor()
              dbCursor.execute('Set TRANSACTION Isolation level Serializable;')
              dbCursor.execute(
                'UPDATE [dbo].USERTABLE SET status_id = 1 where usertable_id = %d;',
                (user_id, ))
              print()
              print("Account has been activated!")
              print()
              user_info = search_user("1", user_id)
              print("UserID\t UserName\t Role\t AcctID\t Status\t")
              print(user_info[0][0], "\t\t", user_info[0][1], "\t",
                    user_info[0][2], "\t", user_info[0][3], "\t",
                    user_info[0][4])
              dbConn.commit()
            except Exception as err:
              print('Failed', ':', err)
              dbConn.rollback()
            finally:
              dbCursor.close()
              break
          else:
            break
        else:
          print("**Error, unknown user's status, try again...")

      else:
        print("**Error, unknown command, try again...")
      print()
      sub_cmd = input(
        "Please enter a command (c: change user name; l: lock/unlock user; b: go back): "
      )


##[Function 6]: Modify User Function
def function_modify_user():
  print("//Modify user information")
  sub_cmd = input(
    "Please enter a command (m: modify, s: search, b: go back): ")
  while sub_cmd != "b":
    if sub_cmd == "m":
      modify_user()
    elif sub_cmd == "s":
      search_function()
    else:
      print("**Error, unknown command, try again...")
    print()
    sub_cmd = input(
      "Please enter a command (m: modify, s: search, b: go back): ")


##[Function 7]: Check account balance
def check_balance(opt, parameters, opt2="N", parameters2="N"):
  if opt == "0":
    sub_sql = """
    select * from account_balance 
    order by account_id asc;
    """
    balance_results = da.select_n_rows(dbConn, sub_sql)
  elif opt == "1":  #Check account balance based on account_ID
    sub_sql = """
    select * from account_balance 
    where account_id like %d
    order by account_id asc;
    """
    balance_results = da.select_n_rows(dbConn,
                                       sub_sql,
                                       parameters=[parameters])
  elif opt == "2":  #Check account balance based on user_ID
    sub_sql = """
    select * from account_balance 
    where usertable_id like %d
    order by account_id asc;
    """
    balance_results = da.select_n_rows(dbConn,
                                       sub_sql,
                                       parameters=[parameters])
  elif opt == "3":  #Check account balance based on user name
    sub_sql = """
    select * from account_balance 
    where usertable_name like %s
    order by account_id asc;
    """
    balance_results = da.select_n_rows(dbConn,
                                       sub_sql,
                                       parameters=[parameters])
  elif opt == "4":  #Check account balance based on amount
    if opt2 == "smaller":
      sub_sql = """
      select * from account_balance 
      where balance <= %d
      order by account_id asc;
      """
      balance_results = da.select_n_rows(dbConn,
                                         sub_sql,
                                         parameters=[parameters])
    elif opt2 == "bigger":
      sub_sql = """
      select * from account_balance 
      where balance >= %d
      order by account_id asc;
      """
      balance_results = da.select_n_rows(dbConn,
                                         sub_sql,
                                         parameters=[parameters])
    elif opt2 == "both":
      sub_sql = """
      select * from account_balance 
      where balance >= %d and balance <= %d
      order by account_id asc;
      """
      balance_results = da.select_n_rows(dbConn,
                                         sub_sql,
                                         parameters=[parameters, parameters2])
    else:
      print("**Error, unknown option, try again...")
      return -1
  else:
    print("**Error, unknown option, try again...")
    return -1

  return balance_results


##[Function 8]: Search different account's balance based on search criteria
def search_account():
  all_acct = check_balance("0", "ALL")
  print("AcctID\tBalance\tUserID\tUserName")
  start_page = 0
  end_page = 10
  while start_page < len(all_acct):
    for row in all_acct[start_page:end_page]:
      print("%d\t\t%s\t\t%s\t%s" % (row[0], f"{row[1]:,.2f}", row[2], row[3]))
    if end_page > len(all_acct):
      break
    print()
    more = input("Display more? [yes/no] ")
    if more == "y" or more == "yes":
      start_page += 10
      end_page += 10
      continue
    else:
      break
  print()
  sub_cmd = input("Please enter a command (c: check balance, b: go back): ")
  while sub_cmd != "b":
    if sub_cmd == "c":
      p = input(
        "Enter search criteria (1: AcctID, 2: UserID, 3: UserName, 4: Balance): "
      )
      if p == "1":
        term = input("Enter Acccount ID (e.g. '%123%'): ")
      elif p == "2":
        term = input("Enter user ID (e.g. '%123%'): ")
      elif p == "3":
        term = input("Enter user name (e.g. '%John%'): ")
      elif p == "4":
        sub_opt = input(
          "Search balance amount based on (smaller: <=, bigger: >=, both: >= AND <=): "
        )
        if sub_opt == "smaller":
          term = input("Enter upper bound x (Balance<=x): ")
        elif sub_opt == "bigger":
          term = input("Enter lower bound x (Balance>=x): ")
        elif sub_opt == "both":
          term1 = input("Enter lower bound x1 (x1<=Balance<=x2): ")
          term2 = input("Enter upper bound x2 (x1<=Balance<=x2): ")

      try:
        if p == "4" and sub_opt == "both":
          search_acct = check_balance(p,
                                      term1,
                                      opt2=sub_opt,
                                      parameters2=term2)
        elif p == "4" and sub_opt == "smaller":
          search_acct = check_balance(p, term, opt2=sub_opt)
        elif p == "4" and sub_opt == "bigger":
          search_acct = check_balance(p, term, opt2=sub_opt)
        elif p == "1" or p == "2" or p == "3":
          search_acct = check_balance(p, term)
        else:
          print("**Error, unknown search criteria, try again...")
          print()
          continue
        print()
        print("Search results:")
        print("AcctID\tBalance\tUserID\tUserName")
        start_page2 = 0
        end_page2 = 10
        while start_page2 < len(search_acct):
          for row in search_acct[start_page2:end_page2]:
            print("%d\t\t%s\t\t%s\t%s" %
                  (row[0], f"{row[1]:,.2f}", row[2], row[3]))
          if end_page2 > len(search_acct):
            break
          print()
          more = input("Display more? [yes/no] ")
          if more == "y" or more == "yes":
            start_page2 += 10
            end_page2 += 10
            continue
          else:
            break
      except:
        print("**Error, unknown search criteria, try again...")
    else:
      print("**Error, unknown command, try again...")
    print()
    sub_cmd = input("Please enter a command (c: check balance, b: go back): ")


##[Function 9]: Transfer fund between accounts
def fund_transfer(from_acct, to_acct, amount):

  ##Check the balance information
  print("Checking account balances")
  acct1_sql = "select account_id, balance from balance where account_id = %d"
  acct2_sql = "select account_id, balance from balance where account_id = %d"
  acct1_info = da.select_one_row(dbConn, acct1_sql, parameters=[from_acct])
  acct2_info = da.select_one_row(dbConn, acct2_sql, parameters=[to_acct])

  if len(acct1_info) == 0:
    print("**Error, from_account doesn't exist, try again...")
    return -1
  elif acct1_info[1] < amount:
    print("**Error, from_account doesn't have enough money, try again...")
    return -1
  else:
    pass
  if len(acct2_info) == 0:
    print("**Error, to_account doesn't exist, try again...")
    return -1
  else:
    pass

  ##Perform transfer procedure
  try:
    dbCursor = dbConn.cursor()
    dbCursor.execute('Set TRANSACTION Isolation level Serializable;')
    #"transfer" procedure defined in sql file
    dbCursor.execute('EXEC transfer %d,%d,%d;', (from_acct, to_acct, amount))
    dbConn.commit()
    print()
    print("Transfer successfully!")
  except Exception as err:
    print('Failed', ':', err)
    dbConn.rollback()
  finally:
    dbCursor.close()

  new_acct_sql = "select account_id, balance from balance where account_id in (%d,%d)"
  new_acct_info = da.select_n_rows(dbConn,
                                   new_acct_sql,
                                   parameters=[from_acct, to_acct])
  print()
  print("New accounts' balances:")
  print("AcctID\tBalance")
  for row in new_acct_info:
    print("%d\t\t%s" % (row[0], f"{row[1]:,.2f}"))


##[Function 10]: Transfer fund Function
def function_fund_transfer():
  all_acct = check_balance("0", "ALL")
  print("AcctID\tBalance\tUserID\tUserName")
  for row in all_acct:
    print("%d\t\t%s\t\t%s\t%s" % (row[0], f"{row[1]:,.2f}", row[2], row[3]))
  sub_cmd = "start"
  while sub_cmd != "b":
    from_acct = input(
      "Which account do you want to transfer money from? Account ID: ")
    to_acct = input(
      "Which account do you want to transfer money to? Account ID: ")
    amount = input("How much do you want to transfer? Amount: ")
    try:
      from_acct = int(from_acct)
      to_acct = int(to_acct)
      amount = int(amount)
    except:
      print("**Error, input should be int, try again...")
      sub_cmd = "b"  #error, exit this cmd
      continue
    fund_transfer(from_acct, to_acct, amount)
    sub_cmd = "b"  #success, exit this cmd


##[Function 11]: Only check user's own balance (based on login user's id)
##could not check others' balances for compliance purposes
def trader_check_balance():
  all_acct = check_balance("2", parameters=login)
  print("AcctID\tBalance\tUserID\tUserName")
  for row in all_acct:
    print("%d\t\t%s\t\t%s\t%s" % (row[0], f"{row[1]:,.2f}", row[2], row[3]))


##[Function 12] Check current market price according to
def check_mktprice(date, ticker):
  sql = """
  select Stock_ID, ticker, MKT_Price from mktdata
  where ticker = %s and date =%s;
  """
  return da.select_one_row(dbConn, sql, parameters=[ticker, date])


##[Function 13] Check whether a specific ticker is within the S&P 500 list
def check_ticker(ticker):
  all_sql = "select ticker from stock;"
  sp500_list = da.select_n_rows(dbConn, all_sql)
  sp500_list = list(zip(*sp500_list))[0]
  if ticker in sp500_list:
    sub_sql = "select ticker, Stock_ID from stock where ticker = %s;"
    return da.select_one_row(dbConn, sub_sql, parameters=[ticker])
  else:
    return None


##[Function 14] Enter a new trade
def trade_entry():
  trade_date = sys_date
  print()
  print("Trade date is %s" % (trade_date))
  PS = input("Enter trade direction (p: purchase, s: sell): ")
  if PS == "p" or PS == "s":  #Error handling: PS entry
    pass
  else:
    print("**Error, unknown trade direction, try again...")
    return -1

  ticker = input("Enter stock ticker (e.g. AMZN for amazon): ").upper()
  stock_ticker_id = check_ticker(ticker)
  if stock_ticker_id is None:  #Error handling: ticker entry
    print("**Error, not a ticker in S&P500 index, try again...")
    return -1
  stock_id = stock_ticker_id[1]  #Get its stock ID according to ticker

  notional = input("Enter trade notional: ")
  try:  #Error handling: notional entry
    notional = int(notional)
  except:
    print("**Error, notional should be integer, try again...")
    return -1

  trd_price = input("Enter trade price: ")
  try:  #Error handling: trade price entry
    trd_price = float(trd_price)
  except:
    print("**Error, Trade price should be integer, try again...")
    return -1
  mktprice = float(check_mktprice(sys_date, ticker)[2])
  ##Compliance Checking 1: trading price deviation--1% tolerance level
  if trd_price > mktprice * 1.01 or trd_price < mktprice * 0.99:
    print()
    print("**Warning, Trade price exceeds 1% deviation range!")
    print("Market Price: %f" % (mktprice))
    print("Trade Price: %f" % (trd_price))
    print()
    trade_execute_opt = input(
      "Do you still want to execute the trade? [yes/no] ")
    if trade_execute_opt == "y" or trade_execute_opt == "yes":
      pass
    else:
      print()
      print("Trade canceled...")
      return -1
  else:
    pass

  print()
  print("Pass price deviation check. Processing...")
  print()

  ##Check account balance--Long Only Fund>could not do short selling
  print("Checking account balance...")
  trade_value = trd_price * notional
  if PS == "p":
    ##Compliance Checking 2: if it is long,
    ##check whether the trader has enough money to purchase the stocks
    acct_bal = check_balance("2",
                             parameters=login)[0][1]  #check user's balance
    acct_bal = float(acct_bal)
    if trade_value > acct_bal:
      print("**Error, insufficient money to purchase the stocks, try again...")
      print("You need to pay: $%d" % (trade_value))
      print("Your account's balance: $%d" % (acct_bal))
      print("Difference: $%d" % (acct_bal - trade_value))
      return -1
    else:
      pass
  elif PS == "s":
    ##Compliance Checking 3: if it is short,
    ##check whether the trader has enough holding position to sell the stocks
    ##Portfolio is a view created in database
    ##check sql file for details
    sub_sql = """
    select ps,sum from portfolio where USERTABLE_ID = %d and stock_ID = %d;
    """
    port_results = da.select_n_rows(dbConn,
                                    sub_sql,
                                    parameters=[login, stock_id])
    port_sum = 0
    for row in port_results:
      if row[0] == "p":
        port_sum = port_sum + row[1]
      elif row[0] == "s":
        port_sum = port_sum - row[1]
    port_sum = int(port_sum)
    if notional > port_sum:
      print("**Error, insufficient amount of stocks to sell, try again...")
      print("You want to sell this amount: %d" % (notional))
      print("Your holding amount: %d" % (port_sum))
      print("Difference: %d" % (port_sum - notional))
      return -1
    else:
      pass
  else:
    print("**Error, PS has unknown value, try again...")
    return -1

  print()
  print("Pass account balance check. Processing...")
  print()
  #Insert Trade info into Database
  acct_id = check_balance("2",
                          parameters=login)[0][0]  #check user's account ID
  try:
    dbCursor = dbConn.cursor()
    dbCursor.execute('Set TRANSACTION Isolation level Serializable;')
    sql = """
    INSERT INTO TRADE (Date,PS,Stock_ID,Notional,TRD_Price,USERTABLE_ID)
    VALUES (%s,%s,%d,%d,%d,%d)
    """
    dbCursor.execute(sql, (sys_date, PS, stock_id, notional, trd_price, login))
    #Balance before transaction
    start_balance = check_balance("2", parameters=login)[0][1]
    ##change the trader's account balance after executing the trade
    if PS == "p":
      bal_sql = """
      update balance set balance = balance - %d where Account_ID = %d;
      """
    elif PS == "s":
      bal_sql = """
      update balance set balance = balance + %d where Account_ID = %d;
      """
    dbCursor.execute(bal_sql, (trade_value, acct_id))

    dbConn.commit()
    print()
    print("Trade is Done!")
    print()
    #Balance after transaction
    end_balance = check_balance("2", parameters=login)[0][1]
    print("//Start balance: $%d" % (start_balance))
    print("//Transaction amount: $%d" % (end_balance - start_balance))
    print("//End balance: $%d" % (end_balance))
  except Exception as err:
    print('Failed', ':', err)
    dbConn.rollback()
  finally:
    dbCursor.close()


##[Function 15] Check Stocks Info
def check_stock(opt, parameters):
  if opt == "0":  #Check all stock info
    sub_sql = """
    select * from stock 
    order by ticker asc;
    """
    stock_info = da.select_n_rows(dbConn, sub_sql)
  elif opt == "1":  #Check stock info based on ticker
    sub_sql = """
    select * from stock
    where ticker like %s
    order by ticker asc;
    """
    stock_info = da.select_n_rows(dbConn, sub_sql, parameters=[parameters])
  elif opt == "2":  #Check stock info based on Stock Name
    sub_sql = """
    select * from stock 
    where Stock_Name like %s
    order by ticker asc;
    """
    stock_info = da.select_n_rows(dbConn, sub_sql, parameters=[parameters])
  elif opt == "3":  #Check stock info based on Sector
    sub_sql = """
    select * from stock 
    where sector like %s
    order by ticker asc;
    """
    stock_info = da.select_n_rows(dbConn, sub_sql, parameters=[parameters])
  elif opt == "4":  #Check stock info based on Location
    sub_sql = """
    select * from stock 
    where location like %s
    order by ticker asc;
    """
    stock_info = da.select_n_rows(dbConn, sub_sql, parameters=[parameters])
  else:
    print("**Error, unknown option, try again...")
    return -1
  return stock_info


##[Function 16] Search stock info based on different search criteria
def search_stock():
  all_stock_info = check_stock("0", "ALL")
  print("Ticker\tName\tSector\tLocation")
  start_page = 0
  end_page = 10
  while start_page < len(all_stock_info):
    for row in all_stock_info[start_page:end_page]:
      print("%s\t\t%s\t\t%s\t%s" % (row[1], row[2], row[3], row[4]))
    if end_page > len(all_stock_info):
      break
    print()
    more = input("Display more? [yes/no] ")
    if more == "y" or more == "yes":
      start_page += 10
      end_page += 10
      continue
    else:
      break
  sub_cmd = input("Please enter a command (s: search stock, b: go back): ")
  while sub_cmd != "b":
    if sub_cmd == "s":
      p = input(
        "Enter search criteria (1: Ticker, 2: Stock Name, 3: Sector, 4: Location): "
      )
      if p == "1":
        term = input("Enter Ticker (e.g. '%AMZN%'): ")
      elif p == "2":
        term = input("Enter Stock Name (e.g. '%Amazon%'): ")
      elif p == "3":
        term = input("Enter Sector (e.g. '%Consumer%'): ")
      elif p == "4":
        term = input("Enter Location (e.g. '%Washington%'): ")
      else:
        print("**Error, unknown search criteria, try again...")
        print()
        continue
      try:
        search_stock = check_stock(p, term)
        print()
        print("Search results:")
        print("Ticker\tName\t\tSector\t\tLocation")
        start_page2 = 0
        end_page2 = 10
        while start_page2 < len(search_stock):
          for row in search_stock[start_page2:end_page2]:
            print("%s\t%s\t\t%s\t\t%s" % (row[1], row[2], row[3], row[4]))
          if end_page2 > len(search_stock):
            break
          print()
          more = input("Display more? [yes/no] ")
          if more == "y" or more == "yes":
            start_page2 += 10
            end_page2 += 10
            continue
          else:
            break
      except:
        print("**Error, unknown search criteria, try again...")
    else:
      print("**Error, unknown command, try again...")
    print()
    sub_cmd = input("Please enter a command (s: search stock, b: go back): ")


##[Function 17] Check Market Data
def check_mktdata(opt, date, parameters):
  if opt == "0":  #Check all market data
    sub_sql = """
    select * from mktdata order by ticker asc;
    """
    mktdata_info = da.select_n_rows(dbConn, sub_sql)
  elif opt == "1":  #Check market data based on a particular date
    sub_sql = """
    select * from mktdata
    where date = %s
    order by ticker asc;
    """
    mktdata_info = da.select_n_rows(dbConn, sub_sql, parameters=[parameters])
  elif opt == "2":  #Check market data based on ticker
    sub_sql = """
    select * from mktdata 
    where date = %s and ticker like %s
    order by ticker asc;
    """
    mktdata_info = da.select_n_rows(dbConn,
                                    sub_sql,
                                    parameters=[date, parameters])
  else:
    print("**Error, unknown option, try again...")
    return -1
  return mktdata_info


##[Function 18] Search Market Data based on different search criteria
def search_mktdata():
  sub_cmd = input(
    "Please enter a command (m: search market data, b: go back): ")
  while sub_cmd != "b":
    if sub_cmd == "m":
      p = input("Enter search criteria (1: Date, 2: ticker): ")
      if p == "1":
        term = input("Enter Date (e.g. '2022-11-23'): ")
      elif p == "2":
        term = input("Enter Ticker (e.g. '%AMZN%'): ")

      try:
        mktdata_results = check_mktdata(p, sys_date, term)
        print()
        print("Search results:")
        print("Date\t\tTicker\t\tMktPrice")
        start_page = 0
        end_page = 10
        while start_page < len(mktdata_results):
          for row in mktdata_results[start_page:end_page]:
            print("%s\t%s\t\t%s" % (row[0], row[2], row[3]))
          if end_page > len(mktdata_results):
            break
          print()
          more = input("Display more? [yes/no] ")
          if more == "y" or more == "yes":
            start_page += 10
            end_page += 10
            continue
          else:
            break
      except:
        print("**Error, unknown search criteria, try again...")
    else:
      print("**Error, unknown command, try again...")
    print()
    sub_cmd = input(
      "Please enter a command (m: search market data, b: go back): ")


##[Function 19] Check trade history
def check_his_trade(opt, parameters, date1='2000-01-01', date2='2100-12-31'):
  if opt == "0":  #Check all trade history
    sub_sql = """
    select * from trade_list order by trade_id asc;
    """
    his_trade_list = da.select_n_rows(dbConn, sub_sql)
  elif opt == "1":  #Check trade history based on a date range
    sub_sql = """
    select * from trade_list
    where date >= %s and date <= %s
    order by trade_id asc;
    """
    his_trade_list = da.select_n_rows(dbConn,
                                      sub_sql,
                                      parameters=[date1, date2])
  elif opt == "2":  #Check trade history based on ticker
    sub_sql = """
    select * from trade_list 
    where date = %s and ticker like %s
    order by trade_id asc;
    """
    his_trade_list = da.select_n_rows(dbConn,
                                      sub_sql,
                                      parameters=[date1, parameters])
  elif opt == "3":  #Check trade history based on user ID
    sub_sql = """
    select * from trade_list 
    where date = %s and usertable_id like %s
    order by trade_id asc;
    """
    his_trade_list = da.select_n_rows(dbConn,
                                      sub_sql,
                                      parameters=[date1, parameters])
  else:
    print("**Error, unknown option, try again...")
    return -1
  return his_trade_list


##[Function 20] Ad Hoc Trade history Report
def trd_his_report(opt="Y"):
  #[Compliance] Trader can only check his/her trade history report;
  #Manager can check all of the traders' reports
  #(Default) opt="Y": doesn't filter out trade results based on user ID
  #opt="N" to only print out user's own trades
  sub_cmd = input(
    "Please enter a command (r: trd history report, b: go back): ")
  while sub_cmd != "b":
    if sub_cmd == "r":
      term = 'ALL'
      p = input(
        "Enter search criteria (1: Date Range, 2: ticker, 3: User ID): ")
      if p == "1":
        print("Enter Date Range")
        print("P.S. Enter pass to use default value")
        print()
        date1 = input("Lower Bound, >=, (e.g. '2022-11-23'): ")
        if date1 == "pass" or date1 == "Pass":
          date1 = "2000-01-01"
        date2 = input("Upper Bound, <=, (e.g. '2022-11-23'): ")
        if date2 == "pass" or date2 == "Pass":
          date2 = "2100-12-31"
      elif p == "2":
        term = input("Enter Ticker (e.g. '%AMZN%'): ")
      elif p == "3":
        term = input("Enter User ID (e.g. '%12%'): ")
      else:
        print("**Error, unknown search criteria, try again...")
        print()
        continue

      try:
        if p == "1":
          report_results = check_his_trade(p, term, date1, date2)
        elif p == "2" or "3":
          today = sys_date
          report_results = check_his_trade(p, term, today)
        #Create an incrementing filename
        i = 0
        while os.path.exists("tradelist_%s.csv" % i):
          i += 1
        file = open('tradelist_%s.csv' % i, 'w')
        writer = csv.writer(file)  #Save the report results into local csv file
        print()
        print("Search results:")
        print("TrdID", "Date", "PS", "Ticker", "Stock", "Notional", "TrdPrice",
              "MktPrice", "TrdValue", "P&L", "Sector", "location", "UserID")
        title = [
          "TrdID", "Date", "PS", "Ticker", "Stock", "Notional", "TrdPrice",
          "MktPrice", "TrdValue", "P&L", "Sector", "location", "UserID"
        ]
        writer.writerow(title)
        for row in report_results:
          if opt == "Y":
            if row[2] == "p":
              print(row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                    row[7], f"{row[5] * row[6]:,.2f}",
                    f"{(row[7] - row[6]) * row[5]:,.2f}", row[8], row[9],
                    row[10])
              row_data = [
                row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7],
                round(row[5] * row[6], 2),
                round((row[7] - row[6]) * row[5], 2), row[8], row[9], row[10]
              ]
              writer.writerow(row_data)
            elif row[2] == "s":
              print(row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                    row[7], f"{-row[5] * row[6]:,.2f}",
                    f"{(row[6] - row[7]) * row[5]:,.2f}", row[8], row[9],
                    row[10])
              row_data = [
                row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7],
                round(-row[5] * row[6], 2),
                round((row[6] - row[7]) * row[5], 2), row[8], row[9], row[10]
              ]
              writer.writerow(row_data)
          elif opt == "N":  #only print out user's own trades
            if row[2] == "p" and row[10] == login_userid:
              print(row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                    row[7], f"{row[5] * row[6]:,.2f}",
                    f"{(row[7] - row[6]) * row[5]:,.2f}", row[8], row[9],
                    row[10])
              row_data = [
                row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7],
                round(row[5] * row[6], 2),
                round((row[7] - row[6]) * row[5], 2), row[8], row[9], row[10]
              ]
              writer.writerow(row_data)
            elif row[2] == "s" and row[10] == login_userid:
              print(row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                    row[7], f"{-row[5] * row[6]:,.2f}",
                    f"{(row[6] - row[7]) * row[5]:,.2f}", row[8], row[9],
                    row[10])
              row_data = [
                row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7],
                round(-row[5] * row[6], 2),
                round((row[6] - row[7]) * row[5], 2), row[8], row[9], row[10]
              ]
              writer.writerow(row_data)
        file.close()
      except:
        print("**Error, unknown search criteria, try again...")
    else:
      print("**Error, unknown command, try again...")
    print()
    sub_cmd = input(
      "Please enter a command (r: trd history report, b: go back): ")


##[Function 21] Ad Hoc Portfolio Report
def port_report(opt="Y"):
  #[Compliance] Trader can only check his/her portfolio report;
  #Manager can check all of the traders' reports
  #(Default) opt="Y": doesn't filter out portfolio results based on user ID
  #opt="N" to only print out user's own portfolio
  sql = "select * from position_report order by USERTABLE_ID;"
  report_results = da.select_n_rows(dbConn, sql)
  #Create an incrementing filename
  i = 0
  while os.path.exists("portfolio_report_%s.csv" % i):
    i += 1
  file = open('portfolio_report_%s.csv' % i, 'w')
  writer = csv.writer(file)  #Save the report results into local csv file
  print()
  print("Search results:")
  print("UserID", "Ticker", "Stock", "Sector", "Location", "OpenPos",
        "AvgPrice", "MktPrice", "P&L")
  title = [
    "UserID", "Ticker", "Stock", "Sector", "Location", "OpenPos", "AvgPrice",
    "MktPrice", "P&L"
  ]
  writer.writerow(title)
  for row in report_results:
    if opt == "Y":
      if row[5] != 0:
        print(row[0], row[1], row[2], row[3], row[4], row[5],
              round(-row[6] / row[5], 4), row[7],
              f"{row[5] * row[7] + row[6]:,.2f}")
        row_data = [
          row[0], row[1], row[2], row[3], row[4], row[5],
          round(-row[6] / row[5], 4), row[7],
          round(row[5] * row[7] + row[6], 2)
        ]
        writer.writerow(row_data)
      elif row[5] == 0:
        print(row[0], row[1], row[2], row[3], row[4], row[5], 0, row[7],
              f"{row[6]:,.2f}")
        row_data = [
          row[0], row[1], row[2], row[3], row[4], row[5], 0, row[7], row[6]
        ]
        writer.writerow(row_data)
    elif opt == "N":  #only print out user's own trades
      if row[5] != 0 and row[0] == login_userid:
        print(row[0], row[1], row[2], row[3], row[4], row[5],
              round(-row[6] / row[5], 4), row[7],
              f"{row[5] * row[7] + row[6]:,.2f}")
        row_data = [
          row[0], row[1], row[2], row[3], row[4], row[5],
          round(-row[6] / row[5], 4), row[7],
          round(row[5] * row[7] + row[6], 2)
        ]
        writer.writerow(row_data)
      elif row[5] == 0 and row[0] == login_userid:
        print(row[0], row[1], row[2], row[3], row[4], row[5], 0, row[7],
              f"{row[6]:,.2f}")
        row_data = [
          row[0], row[1], row[2], row[3], row[4], row[5], 0, row[7], row[6]
        ]
        writer.writerow(row_data)
  file.close()


##[Function 22] Helper function print out command list
def helper_function(opt):
  if opt == "1":
    print("""
///////////////////////////////////////////////////////////
//                 the NU Trading Platform               //
//                       Mode: ADMIN                     //
//                                                       //
// You can perform following actions:                    //
// 1) Check user list                                    //
// 2) Add new user                                       //
// 3) Modify user information                            //
//                                                       //
// x) EXIT                                               //
///////////////////////////////////////////////////////////
    """)
  elif opt == "2":
    print("""
///////////////////////////////////////////////////////////
//                 the NU Trading Platform               //
//                       Mode: TRADER                    //
//                                                       //
// You can perform following actions:                    //
// 1) Check user list                                    //
// 2) Check market data                                  //
// 3) Check account balance                              //
// 4) Check stock information                            //
// 5) Enter a trade                                      //
// 6) [Report]: Transaction history                      //
// 7) [Report]: Portfolio analysis                       //
//                                                       //
// x) EXIT                                               //
///////////////////////////////////////////////////////////
    """)
  elif opt == "3":
    print("""
///////////////////////////////////////////////////////////
//                 the NU Trading Platform               //
//                       Mode: MANAGER                   //
//                                                       //
// You can perform following actions:                    //
// 1) Check user list                                    //
// 2) Check market data                                  //
// 3) Check account balance                              //
// 4) Check stock information                            //
// 5) Transfer money between accounts                    //
// 6) [Report]: Transaction history                      //
// 7) [Report]: Portfolio analysis                       //
//                                                       //
// x) EXIT                                               //
///////////////////////////////////////////////////////////
    """)


############################################################################################
##Main program
print("""
///////////////////////////////////////////////////////////
//         Welcome to the NU Trading Platform            //
//                   Version V1.0                        //
//               System Date: %s                 //
//                                                       //
// You can buy or sell any S&P 500 company's stock here. //
// Hope you can beat the market. Enjoy trading :)        //
///////////////////////////////////////////////////////////
""" % sys_date)

##First, the Login section
login = input(
  "Please type in your user ID (f to check the user list, x to exit): ")
while login != "x":
  userlist = check_user(opt="N")
  if login == "f":
    check_user(opt="Y")  ##print out the userlist
  else:
    try:
      login_userid = int(login)
      id_list = list(zip(*userlist))[0]
      if login_userid in id_list:  ##make sure the user ID is in the system
        print("**Log in successfully!")
        print()

        ##Record the login user info for the latest section
        login_user = search_user("1", login_userid)
        print("//Welcome %s" % login_user[0][1])
        print("//Your User ID: %d" % login_user[0][0])
        print("//Your Role: %s" % login_user[0][2])
        print("//Your Account ID: %s" % login_user[0][3])
        break  ##log in successfully, break out the while loop
      else:
        print("**Error, unknown user, try again...")
    except:
      print("**Error, unknown commend, try again...")

  print()
  login = input(
    "Please type in your user ID (f to check the user list, x to exit): ")

#Second, check the user's status; if its acount is locked, exit
if login == "x":
  pass
else:
  if login_user[0][4] == "LOCKED":
    print()
    print("**Error, this account is LOCKED, please contact IT admin...")
    sys.exit("**Exit...")

#Third, the application section
if login == "x":
  pass
else:
  if login_user[0][2] == "ADMIN":  ##Admin's desktop
    helper_function("1")  ##Admin's commend options
    cmd = input("Please enter a command (1-3, h for help, x to exit): ")
    while cmd != "x":
      if cmd == "1":  ##Function 1: Check user list
        search_function()
      elif cmd == "2":  ##Function 2: Add new user
        add_new_user()
      elif cmd == "3":  ##Function 3: Modify user information
        function_modify_user()
      elif cmd == "h":  ##Print out command list
        helper_function("1")
      else:
        print("**Error, unknown command, try again...")
      print()
      cmd = input("Please enter a command (1-3, h for help, x to exit): ")

  elif login_user[0][2] == "TRADER":  ##Trader's desktop
    helper_function("2")  ##Trader's commend options
    cmd = input("Please enter a command (1-7, h for help, x to exit): ")
    while cmd != "x":
      if cmd == "1":  ##Function 1: Check user list
        search_function()
      elif cmd == "2":  ##Function 2: Check market data
        search_mktdata()
      elif cmd == "3":  ##Function 3: Check account balance
        trader_check_balance()
      elif cmd == "4":  ##Function 4: Check stock information
        search_stock()
      elif cmd == "5":  ##Function 5: Enter a trade
        trade_entry()
      elif cmd == "6":  ##Function 6: [Report] Transaction history
        trd_his_report("N")
      elif cmd == "7":  ##Function 7: [Report] Portfolio analysis
        port_report("N")
      elif cmd == "h":  ##Print out command list
        helper_function("2")
      else:
        print("**Error, unknown command, try again...")

      print()
      cmd = input("Please enter a command (1-7, h for help, x to exit): ")

  elif login_user[0][2] == "MANAGER":  ##Manager's desktop
    helper_function("3")  ##Manager's commend options
    cmd = input("Please enter a command (1-7, h for help, x to exit): ")
    while cmd != "x":
      if cmd == "1":  ##Function 1: Check user list
        search_function()
      elif cmd == "2":  ##Function 2: Check market data
        search_mktdata()
      elif cmd == "3":  ##Function 3: Check account balance
        search_account()
      elif cmd == "4":  ##Function 4: Check stock information
        search_stock()
      elif cmd == "5":  ##Function 5: Transfer money between accounts
        function_fund_transfer()
      elif cmd == "6":  ##Function 6: [Report] Transaction history
        trd_his_report()
      elif cmd == "7":  ##Function 7: [Report] Portfolio analysis
        port_report()
      elif cmd == "h":  ##Print out command list
        helper_function("3")
      else:
        print("**Error, unknown command, try again...")
      print()
      cmd = input("Please enter a command (1-7, h for help, x to exit): ")

  else:
    print("Error, user role undefined, log out...")

print()
print('**Done')
dbConn.close()
