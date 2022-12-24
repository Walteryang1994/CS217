--Create the Stock table to store stock's information
--We are only allow users to trade S&P 500 companies
--Reference: https://en.wikipedia.org/wiki/List_of_S%26P_500_companies
CREATE TABLE [dbo].STOCK(
	Stock_ID int NOT NULL UNIQUE,
	Ticker nvarchar(8) NOT NULL UNIQUE,
	Stock_Name nvarchar(100) NOT NULL,
	Sector nvarchar(50) NOT NULL,
	Location nvarchar(50) NOT NULL,
	PRIMARY KEY (Stock_ID)
); 

--Creat unique index for ticker
--Make it quicker for user to search for stock information through ticker
CREATE UNIQUE INDEX Ticker_Index ON STOCK(Ticker);


--Create the MKTDATA table to store equity market data
--For simplicity purposes, we only use market data on 11/23/2022
--All market data are closing prices for stocks
--Reference: https://www.stockmonitor.com/sp500-stocks/
CREATE TABLE [dbo].MKTDATA(
	Date date NOT NULL,
	Stock_ID int NOT NULL,
	Ticker nvarchar(8) NOT NULL,
	MKT_Price smallmoney NOT NULL,
	FOREIGN KEY (Stock_ID) REFERENCES [dbo].STOCK (Stock_ID),
	CONSTRAINT Check_MKT_Price CHECK([MKT_Price] >=0)
); 

--Creat unique index for ticker
--Make it quicker for user to search for stock market data through ticker
CREATE UNIQUE INDEX MKT_Ticker_Index ON MKTDATA(Ticker);

/* !!!If using the import wizard to import data for table STOCK and table MKTDATA in Azure, 
	please run following sql queries to add CONSTRAINTS on these two tables!!!
 
	ALTER TABLE [dbo].MKTDATA ADD CONSTRAINT FK_Stock_ID FOREIGN KEY (Stock_ID) REFERENCES [dbo].STOCK (Stock_ID);
	ALTER TABLE [dbo].STOCK ADD CONSTRAINT STOCK_UNIQUENESS UNIQUE (Stock_ID, Ticker);
	CREATE UNIQUE INDEX Ticker_Index ON STOCK(Ticker);
	ALTER TABLE [dbo].MKTDATA ADD CONSTRAINT Check_MKT_Price CHECK([MKT_Price] >=0);
*/


--Create the status table to store user's status (ACTIVE or LOCKED)
CREATE TABLE [dbo].STATUS(  
	Status_ID int NOT NULL UNIQUE,
	Status nvarchar(10) NOT NULL UNIQUE,
	PRIMARY KEY (Status_ID)
);   

--Insert data into the status table
INSERT INTO [dbo].STATUS (Status_ID, Status) VALUES (1, 'ACTIVE');
INSERT INTO [dbo].STATUS (Status_ID, Status) VALUES (2, 'LOCKED');


--Create the role table to store user's role (Trader, Manager or Admin)
--Trader can enter trades
--Manager can conduct analysis on traders' performance such as trade history, portfolio analysis, profit and loss analysis 
CREATE TABLE [dbo].ROLE(  
	Role_ID int NOT NULL UNIQUE,
	Role nvarchar(10) NOT NULL UNIQUE,
	PRIMARY KEY (Role_ID)
); 

--Insert data into the role table
INSERT INTO [dbo].ROLE (Role_ID, Role) VALUES (1, 'ADMIN');
INSERT INTO [dbo].ROLE (Role_ID, Role) VALUES (2, 'MANAGER');
INSERT INTO [dbo].ROLE (Role_ID, Role) VALUES (3, 'TRADER');


--Create the balance table to store user's account balance
CREATE TABLE [dbo].BALANCE(  
	Account_ID int NOT NULL IDENTITY(1,1) UNIQUE,
	Balance money NOT NULL,
	PRIMARY KEY (Account_ID),
	CONSTRAINT Check_Balance CHECK([Balance] >=0)
); 

--Insert the company's initial account balance into the balance table
--Since we are using IDENTITY(1,1), we just need to insert the initial amount
--The company's initial account ID is 1
INSERT INTO [dbo].BALANCE (Balance) VALUES (5000000);


--Create the user table to store user's information
CREATE TABLE [dbo].USERTABLE(
	USERTABLE_ID int NOT NULL IDENTITY(1,1) UNIQUE,
	USERTABLE_Name nvarchar(100),
	Role_ID int NOT NULL,
	Account_ID int,
	Status_ID int NOT NULL,
	PRIMARY KEY (USERTABLE_ID),
	FOREIGN KEY (Role_ID) REFERENCES [dbo].ROLE (Role_ID),
	FOREIGN KEY (Account_ID) REFERENCES [dbo].BALANCE (Account_ID),
	FOREIGN KEY (Status_ID) REFERENCES [dbo].STATUS (Status_ID)
); 

--Insert the IT admin user account into the user table
--Since we are using IDENTITY(1,1), we just need to insert the information for the IT admin
--The IT admin's initial account ID is 1
INSERT INTO [dbo].USERTABLE (USERTABLE_Name, Role_ID, Status_ID) VALUES ('IT Admin', 1, 1);


--Create the trade table to store trading transactions
--"P" and "S" in the PS column stands for "Purchase" and "Sell" respectively
--Notional and Trade price should be bigger or equal to 0
CREATE TABLE [dbo].TRADE(
	Trade_ID int NOT NULL IDENTITY(1,1) UNIQUE,
	Date date NOT NULL,
	PS nvarchar(8) NOT NULL,
	Stock_ID int NOT NULL,
	Notional int NOT NULL,
	TRD_Price smallmoney NOT NULL,
	USERTABLE_ID int NOT NULL,
	PRIMARY KEY (Trade_ID),
	FOREIGN KEY (Stock_ID) REFERENCES [dbo].STOCK (Stock_ID),
	FOREIGN KEY (USERTABLE_ID) REFERENCES [dbo].USERTABLE (USERTABLE_ID),
	CONSTRAINT Check_PS CHECK([PS] = 'P' OR [PS] = 'S'),
	CONSTRAINT Check_Notional CHECK([Notional] >=0),
	CONSTRAINT Check_TRD_Price CHECK([TRD_Price] >=0)
); 


/* CREATE PROCEDURE*/Your location
--Fund transfer PROCEDURE
--e.g. EXEC transfer 1,2,100;
CREATE PROCEDURE transfer
    @from INT,
    @to INT,
    @amt money
AS
BEGIN
    UPDATE BALANCE SET BALANCE = BALANCE - @amt WHERE Account_ID = @from;
    UPDATE BALANCE SET BALANCE = BALANCE + @amt WHERE Account_ID = @to;
    RETURN @@ROWCOUNT;
END;

--Give ReadWriteUser permission to call all stored procedures in the database:
GRANT EXECUTE TO ReadWriteUser;

/* CREATE View*/
--Account Balance View
CREATE VIEW account_balance AS
	SELECT balance.ACCOUNT_ID, balance, usertable_id, usertable_name from balance 
	left join usertable on balance.account_id = usertable.account_id;

--Trade Portfolio View
CREATE View portfolio AS
    select USERTABLE_ID, stock_id, ps, sum(notional) as sum from trade group by USERTABLE_ID, stock_id, ps;

--Trade History VIEW
CREATE View trade_list AS
    select t.Trade_ID, t.date, t.ps, s.ticker, s.Stock_Name, t.Notional,t.TRD_Price, m.MKT_Price, s.Sector, s.location, t.USERTABLE_ID 
    from trade t left join stock s on t.Stock_ID=s.Stock_ID
    left join MKTDATA m on t.Stock_ID = m.Stock_ID;

--Portfolio Report VIEW
CREATE View position_report AS
    select USERTABLE_ID, trade_list_sign.ticker,stock_name, Sector,Location,-sum(sign_notional) as position, sum(sign_notional * TRD_Price) as transaction_amt, m.MKT_Price from 
    (select t.Trade_ID, t.date, t.ps, s.ticker, s.Stock_Name, t.Notional as sign_notional,t.Notional,TRD_Price, s.Sector, s.location, t.USERTABLE_ID 
    from trade t left join stock s on t.Stock_ID=s.Stock_ID
    where ps = 's'
    union
    select t.Trade_ID, t.date, t.ps, s.ticker, s.Stock_Name, -t.Notional as sign_notional,t.Notional,TRD_Price, s.Sector, s.location, t.USERTABLE_ID 
    from trade t left join stock s on t.Stock_ID=s.Stock_ID
    where ps = 'p') trade_list_sign
    left join MKTDATA m on trade_list_sign.ticker = m.ticker
    group by USERTABLE_ID,trade_list_sign.ticker,stock_name,m.MKT_Price,Sector,Location;