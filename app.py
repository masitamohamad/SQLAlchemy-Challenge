import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


###########################################################################################
# Database Setup
###########################################################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

###########################################################################################
# Flask Setup
###########################################################################################
app = Flask(__name__)

###########################################################################################
# 'calc_temps' Function Setup
###########################################################################################
# This function called `calc_temps` will accept start date and end date in the format '%Y-%m-%d' 
# and return the minimum, average, and maximum temperatures for that range of dates
def calc_temps(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    session = Session(engine)

    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()


###########################################################################################
# Flask Routes
###########################################################################################

# Home page
# List all routes that are available.

@app.route("/")
def home():
    print("Server received request for home page...")
    
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

###########################################################################################
# Define what to do when a user hits the "/api/v1.0/precipitation" route
# Convert the query results to a dictionary using date as the key and prcp as the value.
# Return the JSON representation of the dictionary.

@app.route("/api/v1.0/precipitation")
def precipitation():
    print("Received precipitation API request...")
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all precipitation data"""
    # Query all precipitation data
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    # Create a dictionary from the row data and append to a list of all_prcp

    all_prcp = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        all_prcp.append(prcp_dict)

    return jsonify(all_prcp)

###########################################################################################
# Define what to do when a user hits the "/api/v1.0/stations" route
# Return a JSON list of stations from the dataset.

@app.route("/api/v1.0/stations")
def station():
    print("Received station name API request...")
    session = Session(engine)

    """Return a list of all station names"""
    # Query all station names
    results = session.query(Station.name).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

###########################################################################################
# Define what to do when a user hits the "/api/v1.0/tobs" route
# Query the dates and temperature observations of the most active station for the last year of data.
# Return a JSON list of temperature observations (TOBS) for the previous year.

@app.route("/api/v1.0/tobs")
def tobs():
    print("Received temperature observations API request...")
    session = Session(engine)

    """Return a list of dates and temperature observations from the most active station since last year"""
    # Query all temperature observations and filter using results from climate_starter.ipynb: Most active station = "USC00519281" and date 1 year ago from the last data point in the database = datetime.date(2016, 8, 23)
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date>="2016-08-23").filter(Measurement.station == "USC00519281").all()

    session.close()

    all_tobs = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)

###########################################################################################
# Define what to do when a user hits the "/api/v1.0/<start>" and "/api/v1.0/<start>/<end>" routes
# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.

@app.route("/api/v1.0/<start>")
def start(start):
    print("Received temperatures API request with start date...")

    session = Session(engine)

    # Find the last date in the database & obtain the temperature results using 'calc_temps' function from above
    max_date = session.query(func.max(func.strftime("%Y-%m-%d", Measurement.date))).all()
    final_date = max_date[0][0]

    temperatures = calc_temps(start, final_date)

    session.close()

    temp_list = []
    date_dict = {'start_date': start, 'end_date': final_date}
    temp_list.append(date_dict)
    temp_list.append({'observation': 'TMIN', 'temperature': temperatures[0][0]})
    temp_list.append({'observation': 'TAVG', 'temperature': round((temperatures[0][1]),1)})
    temp_list.append({'observation': 'TMAX', 'temperature': temperatures[0][2]})

    return jsonify(temp_list)

# Define what to do when a user hits the "/api/v1.0/<start>/<end>" route

@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):
    print("Received temperatures API request with start and end dates...")

    temperatures = calc_temps(start, end)

    temp_list = []
    date_dict = {'start_date': start, 'end_date': end}
    temp_list.append(date_dict)
    temp_list.append({'observation': 'TMIN', 'temperature': temperatures[0][0]})
    temp_list.append({'observation': 'TAVG', 'temperature': round((temperatures[0][1]),1)})
    temp_list.append({'observation': 'TMAX', 'temperature': temperatures[0][2]})

    return jsonify(temp_list)

###########################################################################################
# Main Behavior
###########################################################################################

if __name__ == "__main__":
    app.run(debug=True)