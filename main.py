import sqlite3
from traceback import print_exc

from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("home.html")


# Query 1
@app.route("/get_booked_trains", methods=["POST"])
def get_booked_trains():
    if request.method == "POST":
        form1 = request.form
    conn = sqlite3.connect('rrs.db')
    cur = conn.cursor()
    cur.execute(
        """SELECT t.train_number,
               t.train_name,
               t.premium_fare,
               t.general_fare,
               t.source_station,
               t.destination_station
          FROM train t,
               passenger p,
               booked b
         WHERE first_name = ? AND 
               last_name =  ? AND 
               p.ssn = b.ssn AND 
               b.train_number = t.train_number;"""
        , (form1.get("fname"), form1.get('lname')))
    records = cur.fetchall()
    if len(records) == 0:
        records = None
    conn.close()
    return render_template("pax_by_fname_lname_view.html", records=records)


# Query 2
@app.route("/get_booked_passengers_by_day", methods=["POST"])
def get_booked_passengers_by_day():
    if request.method == "POST":
        form = request.form
        print(form)
    conn = sqlite3.connect('rrs.db')
    cur = conn.cursor()
    cur.execute(
        """SELECT ta.train_number, 
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
               b.status = 'Booked';"""
        , (form.get("day"),))
    records = cur.fetchall()
    if len(records) == 0:
        records = None
    conn.close()
    return render_template("booked_passenger_by_day_view.html", records=records)


# Query 3
@app.route("/get_passenger_details", methods=['POST'])
def get_passenger_details():
    if request.method == "POST":
        form2 = request.form
    conn = sqlite3.connect('rrs.db')
    cur = conn.cursor()
    cur.execute(
        """SELECT p.first_name,
               p.last_name,
               p.address,
               CAST(( (julianday('now') - julianday(p.bdate) ) / 365) as Int) AS age,
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
               age BETWEEN ? AND ?;"""
        , (int(form2.get("llimit")), int(form2.get('ulimit'))))
    records = cur.fetchall()
    if len(records) == 0:
        records = None
    conn.close()
    return render_template("pax_by_age_range_view.html", records=records)


# Query 4
@app.route("/get_passenger_count", methods=['GET'])
def get_passenger_count():
    conn = sqlite3.connect('rrs.db')
    cur = conn.cursor()
    cur.execute(
        """SELECT t.train_number, t.train_name,
               COUNT(b.ssn) AS passenger_count
          FROM train t LEFT JOIN 
               booked b ON t.train_number = b.train_number
         GROUP BY t.train_number;""")
    records = cur.fetchall()
    if len(records) == 0:
        records = None
    conn.close()
    return render_template("passenger_count_view.html", records=records)


# Query 5
@app.route("/get_confirmed_passengers", methods=['POST'])
def get_confirmed_passengers():
    if request.method == "POST":
        form3 = request.form
    conn = sqlite3.connect('rrs.db')
    cur = conn.cursor()
    cur.execute(
        """SELECT p.first_name,
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
                                );"""
        , (form3.get('train_name'),))
    records = cur.fetchall()
    if len(records) == 0:
        records = None
    conn.close()
    return render_template("booked_passenger_by_train_name_view.html", records=records)


@app.route("/cancel_ticket", methods=['POST'])
def cancel_ticket():
    global cancellation_success
    cancellation_success = False
    if request.method == "POST":
        form = request.form
    user_ssn = int(form.get("ssn"))
    train_number = int(form.get("train_number"))
    try:
        conn = sqlite3.connect('rrs.db')
        cur = conn.cursor()
        # fetch status
        cur.execute("SELECT status FROM booked WHERE ssn = ? AND train_number = ?;", (user_ssn, train_number))
        status = cur.fetchone()
        if status[0] == 'Booked':
            cur.execute("DELETE FROM booked WHERE ssn = ? AND train_number = ?;", (user_ssn, train_number))
            cur.execute("DELETE FROM passenger WHERE ssn = ?;", (user_ssn,))
            cur.execute(
                """UPDATE booked
                   SET status = 'Booked'
                 WHERE ssn = (
                                 SELECT b.ssn
                                   FROM booked b
                                  WHERE b.train_number = ? AND 
                                        b.status = 'WaitL'
                                  LIMIT 1
                             );""", (train_number,))
            cancellation_success = True
            conn.commit()
        elif status[0] == 'WaitL':
            cur.execute("DELETE FROM booked WHERE ssn = ? AND train_number = ?;", (user_ssn, train_number))
            cur.execute("DELETE FROM passenger WHERE ssn = ?;", (user_ssn,))
            cancellation_success = True
            conn.commit()
        else:
            cancellation_success = False
    except:
        conn.rollback()
        print_exc()
    finally:
        conn.close()
    return render_template("delete_passenger_view.html", cancel_status=cancellation_success)


if __name__ == "__main__":
    app.run(debug=True)
