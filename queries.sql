--Query 1
--This query retrieves train details when first name and last name is given

SELECT t.train_number,
       t.train_name,
       t.premium_fare,
       t.general_fare,
       t.source_station,
       t.destination_station
  FROM train t,
       passenger p,
       booked b
 WHERE first_name = ? AND 
       last_name = ? AND 
       p.ssn = b.ssn AND 
       b.train_number = t.train_number;

--Query 2
--This query retrieve passenger details travelling on a particular day of the week
SELECT ta.train_number,
       p.first_name,
       p.last_name,
       p.ssn,
       b.status
  FROM train_availability ta,
       passenger p,
       booked b
 WHERE available_on = ? AND 
       b.ssn = p.ssn AND 
       ta.train_number = b.train_number AND 
       b.status = 'Booked';

--Query 3
--This query retrieve passenger details under a given age range
SELECT p.first_name,
       p.last_name,
       p.address,
       CAST ( ( (julianday('now') - julianday(p.bdate) ) / 365) AS INT) AS age,
       b.ticket_type,
       t.train_number,
       t.train_name,
       t.source_station,
       t.destination_station,
       b.status
  FROM train t,
       passenger p,
       booked b
 WHERE t.train_number = b.train_number AND 
       b.ssn = p.ssn AND 
       age BETWEEN ? AND ?;
       

--Query 4
-- This query counts the number of passengers travelling in each train
SELECT t.train_number,
       t.train_name,
       COUNT(b.ssn) AS passenger_count
  FROM train t
       LEFT JOIN
       booked b ON t.train_number = b.train_number
 GROUP BY t.train_number;
 
--Query 5
-- This query retrieves passenger details based on the given train name
SELECT p.first_name,
       p.last_name,
       p.address,
       b.ticket_type,
       b.status
  FROM passenger p,
       booked b
 WHERE p.ssn = b.ssn AND 
       b.status = "Booked" AND 
       b.train_number = (
                            SELECT train_number
                              FROM train
                             WHERE train_name = ?
                        );

--Query 6 as a transaction
-- This series of queries cancels a ticket of the passenger and update the waiting list passenger to booked status.
--Begin
DELETE FROM booked WHERE ssn = ? AND train_number = ?;
DELETE FROM passenger WHERE ssn = ?;
UPDATE booked
                   SET status = 'Booked'
                 WHERE ssn = (
                                 SELECT b.ssn
                                   FROM booked b
                                  WHERE b.train_number = ? AND 
                                        b.status = 'WaitL'
                                  LIMIT 1
                             );
                             
--Commit
--End Transaction
