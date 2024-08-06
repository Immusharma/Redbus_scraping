import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import create_engine
import pymysql


# Function to generate time interval time between start_time and end_time
def generateTimeFun(start_time, end_time):
    time_interval = []
    current_time = start_time
    while current_time < end_time:
        next_time = current_time + timedelta(hours=1)
        time_interval.append(f"{current_time.strftime('%H:%M')} - {next_time.strftime('%H:%M')}")
        current_time = next_time
    time_interval.append(f"{end_time.strftime('%H:%M')} - 23:59")
    return time_interval


# connect mysql database
def dataBaseConnectFun(query):
    engine = create_engine("mysql+mysqlconnector://root:Jaan%400125@localhost:3306/redbus")
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    return df


# Sidebar radio button for navigation
selectRadioVar = st.sidebar.radio("Main Menu", ["Home", "Search Buses"])

# Home page
if selectRadioVar == "Home":
    st.markdown("""<h3>RedBus Site Information</h3>""", True)
    linkCol1, linkCol2 = st.columns(2)
    linkCol1.markdown("[RedBus Ticket Booking Site Link](https://www.redbus.in/)")
    linkCol2.markdown("[RedBus App Download Link](https://play.google.com/store/apps/details?id=in.redbus.android&hl=en_IN&pli=1)", True)
    st.video("https://youtu.be/Ajaik2PxMTw?si=x0PEw522PGEx0kTN")

# Search Buses page
elif selectRadioVar == "Search Buses":
    st.markdown("""<h3>Search Buses</h3>""", True)
    start_time = datetime.strptime("00:00", "%H:%M")
    end_time = datetime.strptime("23:00", "%H:%M")
    hourlyValue = generateTimeFun(start_time, end_time)

    # Content for the first tab
    form = st.form(key="BusSearchInfo")
    col1, col2, col3 = form.columns(3)
    sqlquery = "select * from bus_routes"
    bus_routes = dataBaseConnectFun(sqlquery)

    # Extract unique values for dropdowns
    busRouteInfo = bus_routes["route_name"].unique()
    ratingInfo = bus_routes["star_rating"].unique()
    priceInfo = bus_routes["price"].unique()
    busNameInfo = bus_routes["busname"].unique()
    seatAvailableInfo = bus_routes["seats_available"].unique()

    with col1:
        routeInfo = col1.selectbox("Select the Route", busRouteInfo)
        ratings = col1.selectbox("Select the Ratings", ratingInfo)
    with col2:
        busName = col2.selectbox("Select the Bus Name", busNameInfo)
        time = col2.selectbox("Time between", hourlyValue)
    with col3:
        seatAvailability = col3.selectbox("Select Number of Seats Available", seatAvailableInfo)
        price = col3.selectbox("Bus Fare Range (Start From)", priceInfo)
    submit = form.form_submit_button("Search")

    # When the form is submitted
    if submit:
        dataStart, dataEnd = time.split(" - ")
        searchRequestQuery = f"""
        select * from bus_routes
        where route_name="{routeInfo}" and star_rating >= {ratings}
        and seats_available >= {seatAvailability} AND price >= {price}
        and busname like "{busName}%" and `departing_time` between "{dataStart}" and "{dataEnd}"
        """
        searchBusInfo = dataBaseConnectFun(searchRequestQuery)
        data_testing = pd.DataFrame(searchBusInfo)

        # Convert 'departing_time' to string and extract the time part
        data_testing['departing_time'] = data_testing['departing_time'].astype(str).apply(lambda timeValue: str(timeValue).split()[-1])
        # Convert 'reaching_time' to string and extract the time part
        data_testing['reaching_time'] = data_testing['reaching_time'].astype(str).apply(lambda timeValue: str(timeValue).split()[-1])

        # Check if DataFrame is empty
        if data_testing.empty:
            st.warning("No Buses are available")
        else:
            st.success("Bus details are below")
            st.dataframe(data_testing)
