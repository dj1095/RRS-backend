DROP TABLE IF EXISTS booked;

DROP TABLE IF EXISTS passenger;

DROP TABLE IF EXISTS train_status;

DROP TABLE IF EXISTS train;

DROP TABLE IF EXISTS train_availability;

CREATE TABLE train (
    train_number        INTEGER NOT NULL
                                PRIMARY KEY,
    train_name          TEXT    NOT NULL,
    premium_fare        REAL    NOT NULL,
    general_fare        REAL    NOT NULL,
    source_station      TEXT    NOT NULL,
    destination_station TEXT    NOT NULL
);

CREATE TABLE train_availability (
    train_number INTEGER NOT NULL,
    available_on TEXT    NOT NULL,
    PRIMARY KEY (
        train_number,
        available_on
    ),
    FOREIGN KEY (
        train_number
    )
    REFERENCES train (train_number) 
);

CREATE TABLE passenger (
    first_name TEXT    NOT NULL,
    last_name  TEXT    NOT NULL,
    address    TEXT    NOT NULL,
    city       TEXT    NOT NULL,
    county     TEXT    NOT NULL,
    phone      TEXT    NOT NULL,
    ssn        INTEGER NOT NULL
                       PRIMARY KEY,
    bdate      DATE    NOT NULL
);

CREATE TABLE train_status (
    train_date              DATE    NOT NULL,
    train_name              TEXT    NOT NULL,
    premium_seats_available INTEGER CHECK (premium_seats_available >= 0 AND 
                                           premium_seats_available <= 10),
    gen_seats_available     INTEGER CHECK (gen_seats_available >= 0 AND 
                                           gen_seats_available <= 10),
    premium_seats_occupied  INTEGER CHECK (premium_seats_occupied >= 0 AND 
                                           premium_seats_occupied <= premium_seats_available),
    gen_seats_occupied      INTEGER CHECK (gen_seats_occupied >= 0 AND 
                                           gen_seats_occupied <= gen_seats_available),
    PRIMARY KEY (
        train_date,
        train_name
    )
);

CREATE TABLE booked (
    ssn          INTEGER NOT NULL,
    train_number INTEGER NOT NULL,
    ticket_type  TEXT    CHECK (ticket_type = "Premium" OR 
                                ticket_type = "General"),
    status       TEXT    CHECK (status = "WaitL" OR 
                                status = "Booked"),
    PRIMARY KEY (
        ssn,
        train_number
    )
);