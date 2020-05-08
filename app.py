import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

from pandas.core.common import flatten

test_dict = {"key":"value"}
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
station = Base.classes.station
measurement = Base.classes.measurement

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
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
        
    )

@app.route("/api/v1.0/precipitation")
def prcp():

    # Convert the query results to a dictionary using date as the key and prcp as the value.
    # Return the JSON representation of your dictionary.


    # Create our session (link) from Python to the DB
    session = Session(engine)

    results = session.query(measurement.date,measurement.prcp).all()

    session.close()

    precip = {date:prcp for date, prcp in results}
    return jsonify(precip)




@app.route("/api/v1.0/stations")
def stations():
#    Return a JSON list of stations from the dataset.
#    # Create our session (link) from Python to the DB
    session = Session(engine)

    results = session.query(station.station).all()

    session.close()

#     # Create a dictionary from the row data and append to a list of all_passengers
    stations_list = []
    for row in results:
        stations_dict = {}
        
        stations_list.append(row[0])
    
    stations_dict["station"] = stations_list

    return jsonify(stations_dict)
    
@app.route("/api/v1.0/tobs")
def tobs():

    # Query the dates and temperature observations of the most active station for the last year of data.
    # Return a JSON list of temperature observations (TOBS) for the previous year.

    session = Session(engine)
    #2017-08-23 is last date recorded so all dates after 2016-08-23 will be included
    result = session.query(measurement.date,measurement.tobs).filter(measurement.station == "USC00519281" , measurement.date >= "2016-08-23")

    session.close()
    
    tobs = {date:tobs for date, tobs in result}
    
    return jsonify(tobs)
    
@app.route("/api/v1.0/<start>")

# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.

def start_date(start):
   
    session = Session(engine)
    
    result = session.query(measurement.tobs).filter( measurement.date >= start)

    session.close()
    
#using pandas df to tailor the results

    df_tobs = pd.DataFrame(result)

    TMIN = df_tobs.min()
    TMIN = TMIN['tobs']

    TAVG = df_tobs.mean()
    TAVG = TAVG['tobs']

    TMAX  = df_tobs.max()
    TMAX  = TMAX['tobs']

    temp_dict = {"TMIN": TMIN, "TAVG": TAVG, "TMAX": TMAX}
    
    return jsonify(temp_dict)



@app.route("/api/v1.0/<start>/<end>")

# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.

def start_end_date(start, end):
   
    session = Session(engine)
    
    result = session.query(measurement.tobs).filter(measurement.date <= end , measurement.date >= start)

    session.close()

    df_tobs = pd.DataFrame(result)

    TMIN = df_tobs.min()
    TMIN = TMIN['tobs']

    TAVG = df_tobs.mean()
    TAVG = TAVG['tobs']

    TMAX  = df_tobs.max()
    TMAX  = TMAX['tobs']

    temp_dict = {"TMIN": TMIN, "TAVG": TAVG, "TMAX": TMAX}
    
    return jsonify(temp_dict)

if __name__ == '__main__':
    app.run(debug=True)
