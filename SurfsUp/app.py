# Import the dependencies.
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import datetime as dt
import numpy as np
import pandas as pd

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Declare a Base using `automap_base()`
Base = automap_base()

# Use the Base class to reflect the database tables
Base.prepare(autoload_with=engine)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start<br/>"
        f"/api/v1.0/temp/start/end<br/>"
        f"<p>'start' and 'end' date should be in the format YYYY-MM-DD"
    )

# SQL Queries
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Design a query to retrieve the last 12 months of precipitation data and plot the results.
    # Starting from the most recent data point in the database.
    
    # Calculate the date one year from the last date in data set.
    prev_yr = dt.date(2017, 8, 23) - dt.timedelta(days=365) 
    
    # Perform a query to retrieve the data and precipitation scores
    precipitation = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= prev_yr).all()
                    
    session.close()
    precipitations = {date: prcp for date, prcp in precipitation}
    return jsonify(precipitations)

@app.route("/api/v1.0/stations")
def stations():
    total_stations = session.query(func.count(Station.station)).all()

    session.close()
    stations = list(np.ravel(total_stations))
    return jsonify(stations=stations)

@app.route("/api/v1.0/tobs")
def tobs():
    prev_yr = dt.date(2017, 8, 23) - dt.timedelta(days=365) 

    results = session.query(Measurement.date, Measurement.station, Measurement.tobs).filter(Measurement.date >= prev_yr).\
        filter(Measurement.station == 'USC00519281')
    
    session.close()
    tobs = list(np.ravel(results))
    return jsonify(tobs=tobs)

@app.route("/api/v1.0/temp/<start>")
def tobs_start(start):
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start_date).\
        all()
    
    session.close()
    df = pd.DataFrame(results, columns=["min_tobs","max_tobs","avg_tobs"])
    data = df.to_dict(orient="records")
    return jsonify(data)

@app.route("/api/v1.0/temp/<start>/<end>")
def tobs_start_end(start, end):
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    end_date = dt.datetime.strptime(end, '%Y-%m-%d')
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start_date).\
        filter(Measurement.date <= end_date).\
        all()
    
    session.close()
    df = pd.DataFrame(results, columns=["min_tobs","max_tobs","avg_tobs"])
    data = df.to_dict(orient="records")
    return jsonify(data)

# Run the App
if __name__ == '__main__':
    app.run(debug=True)