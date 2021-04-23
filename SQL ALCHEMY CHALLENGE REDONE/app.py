# 1. Import Flask
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

engine = create_engine("sqlite:///hawaii.sqlite")
conn = engine.connect()

Base = automap_base()

Base.prepare(engine, reflect=True)
measurement=Base.classes.measurement
station=Base.classes.station

# 2. Create an app
app = Flask(__name__)


# 3. Define static routes
@app.route("/")
def welcome():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

# Convert the query results to a dictionary using date as the key and prcp as the value.

# Return the JSON representation of your dictionary.

@app.route("/api/v1.0/precipitation")
def prcp():
    session = Session(engine)
    results = session.query(measurement.date, measurement.prcp)
    session.close()
    all_prcp = []
    for date, prcp in results:
        measurement_dict={}
        measurement_dict["date"]= date
        measurement_dict["prcp"]= prcp
        all_prcp.append(measurement_dict)
        
    return jsonify(all_prcp)


# Return a JSON list of stations from the dataset.

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(station.station).all()
    session.close()
    all_stations=list(np.ravel(results))
    return jsonify(all_stations)

# Query the dates and temperature observations of the most active station for the last year of data.

@app.route("/api/v1.0/tobs")
def tobs():
   conn = engine.connect()
   session = Session(engine)
   temp_results = pd.read_sql("SELECT date, prcp FROM measurement WHERE date <='2017-08-23' AND date  >= '2016-08-23'AND station ='USC00519281'", conn)
   session.close()
   all_tobs=list(np.ravel(temp_results))
   return jsonify(all_tobs)

# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def date(start=None, end=None):
    session = Session(engine)
    sel = [
        func.max(measurement.tobs),
        func.min(measurement.tobs),
        func.avg(measurement.tobs)]
    if not end:
        results = session.query(*sel).\
            filter(measurement.date>= start).all()
        temps = list(np.ravel(results))
        return jsonify(temps)
    results = session.query(*sel).\
        filter(measurement.date >= start).\
        filter(measurement.date <=end).all()
    temps = list(np.ravel(results))
    return jsonify(temps)



# 4. Define main behavior
if __name__ == "__main__":
    app.run(debug=True)