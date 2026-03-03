# @Author: Muhammad Talha Adnan Khan
# @Date: 2025-03-01
# @Description: This program allows the user to analyze various aspects of the Chicago traffic camera database.
# The user can find intersections by name, find all cameras at an intersection, find the percentage of violations for a specific date,
# find the number of cameras at each intersection, find the number of violations at each intersection given a year, find the number of violations by year given a camera ID,
# find the number of violations by month given a camera ID and year, and compare the number of red light and speed violations given a year.
# The program also provides the user with general statistics about the database.
# The user can also exit the program by entering 'x'.

import sqlite3
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from typing import *
import datetime

# Functions

def validate_input(user_input: str) -> bool :
    """
    Validates the user input to ensure it is a valid menu option.

    Args:
        user_input (str): The user input to validate.

    Returns:
        bool: True if input is valid, False otherwise
    """

    if user_input == "x" or ( user_input.isdigit() and int( user_input ) in range(1, 10) ):
        return True
    return False


def print_stats(db_conn: sqlite3.Connection) -> None:
    """
    Given a connection to the database, 
    executes various SQL queries to retrieve and output basic stats.

    Args:
        db_conn (sqlite3.Connection): A connection to the database.
    
    Returns:
        None
    """

    db_cursor = db_conn.cursor()
    
    db_cursor.execute("""--sql
        select 
            (select count(*) from RedCameras),
            (select count(*) from SpeedCameras),
            (select count(*) from RedViolations),
            (select count(*) from SpeedViolations),
            (select min(Violation_Date) from RedViolations),
            (select max(Violation_Date) from RedViolations),
            (select sum(Num_Violations) from RedViolations),
            (select sum(Num_Violations) from SpeedViolations)
    """)
    (
        num_red_cameras,
        num_speed_cameras,
        num_red_violations_entries,
        num_speed_violations_entries,
        min_date,
        max_date,
        total_red_violations,
        total_speed_violations
    ) = db_cursor.fetchone()

    print("General Statistics:")
    print(f"  Number of Red Light Cameras: {num_red_cameras:,}")
    print(f"  Number of Speed Cameras: {num_speed_cameras:,}")
    print(f"  Number of Red Light Camera Violation Entries: {num_red_violations_entries:,}")
    print(f"  Number of Speed Camera Violation Entries: {num_speed_violations_entries:,}")
    print(f"  Range of Dates in the Database: {min_date} - {max_date}")
    print(f"  Total Number of Red Light Camera Violations: {total_red_violations:,}")
    print(f"  Total Number of Speed Camera Violations: {total_speed_violations:,}")


def find_intersection_by_name(db_conn: sqlite3.Connection, intersection_name: str) -> None:
    """
    Given a connection to the database and an intersection name, 
    prints a list of tuples containing the street names of the intersection.

    Args:
        dbConn (sqlite3.Connection): A connection to the database.
        intersection_name (str): The name of the intersection to search for.
    """

    db_cursor = db_conn.cursor()
    db_cursor.execute("""--sql
        select Intersection_ID, Intersection
        from Intersections
        where Intersection like ?
        order by Intersection asc
    """, ( intersection_name, ))
    intersection_info = db_cursor.fetchall()
    if intersection_info:
        print("\n".join( f"{id} : {name}" for id, name in intersection_info ))
    else:
        print("No intersections matching that name were found.")


def find_cameras_by_intersection(db_conn: sqlite3.Connection, intersection_address: str) -> None:
    """
    Given a connection to the database and an intersection ID, 
    prints a list of tuples containing the camera IDs and types at the intersection.

    Args:
        dbConn (sqlite3.Connection): A connection to the database.
        intersection_id (int): The ID of the intersection to search for.
    """

    db_cursor = db_conn.cursor()

    db_cursor.execute("""--sql
        select Camera_ID, Address
        from RedCameras
        where Intersection_ID = (select Intersection_ID from Intersections where Intersection = ?)
        order by Camera_ID asc
    """, ( intersection_address, ))
    
    red_cam_info = db_cursor.fetchall()

    db_cursor.execute("""--sql
        select Camera_ID, Address
        from SpeedCameras
        where Intersection_ID = (select Intersection_ID from Intersections where Intersection = ?)
        order by Camera_ID asc
    """, ( intersection_address, ))

    speed_cam_info = db_cursor.fetchall()

    # Separating the red light and speed cameras
    red_cameras = [ (cam_id, address) for cam_id, address in red_cam_info ]
    speed_cameras = [ (cam_id, address) for cam_id, address in speed_cam_info ]

    # res validation
    if red_cameras:
        print("Red Light Cameras:")
        print("\n".join( f"   {cam_id} : {address}" for cam_id, address in red_cameras ))
        print()
    else:
        print("\nNo red light cameras found at that intersection.")

    if  speed_cameras:
        print("Speed Cameras:")
        print("\n".join( f"   {cam_id} : {address}" for cam_id, address in speed_cameras ))
        print()
    else:
        print("\nNo speed cameras found at that intersection.")

def find_num_violations_by_date(db_conn: sqlite3.Connection, violation_date: str) -> None:
    """
    Given a connection to the database, 
    prints the percentage of violations for a specific date.

    Args:
        dbConn (sqlite3.Connection): A connection to the database.
    """

    # Fetching the total number of red light and speed violations for the given date
    db_cursor = db_conn.cursor()
    db_cursor.execute("""--sql
        select coalesce( sum(Num_Violations), 0 )
        from RedViolations
        where Violation_Date = ?
    """, ( violation_date, ))
    total_red_violations = db_cursor.fetchone()[0] # Fetching one row since the resultant table will have only one row

    # Fetching the total number of speed violations for the given date
    db_cursor.execute("""--sql
        select coalesce( sum(Num_Violations), 0 )
        from SpeedViolations
        where Violation_Date = ?
    """, ( violation_date, ))
    total_speed_violations = db_cursor.fetchone()[0] # Fetching one row since the resultant table will have only one row

    # Guard clause
    if not ( total_red_violations and total_speed_violations ):
        print("No violations on record for that date.")
        return
        
    # Calculating the total violations and each type's percentage
    total_violations = total_red_violations + total_speed_violations
    red_violations_percentage = (total_red_violations / total_violations) * 100
    speed_violations_percentage = (total_speed_violations / total_violations) * 100
    
    # Printing the results
    print(f"Number of Red Light Violations: {total_red_violations:,} ({red_violations_percentage:.3f}%)")
    print(f"Number of Speed Violations: {total_speed_violations:,} ({speed_violations_percentage:.3f}%)")
    print(f"Total Number of Violations: {total_violations:,}")

def find_num_cameras_at_each_intersection(db_conn: sqlite3.Connection) -> None:
    """
    Given a connection to the database, 
    prints the number of cameras at each intersection.

    Args:
        dbConn (sqlite3.Connection): A connection to the database.
    """

    db_cursor = db_conn.cursor()

    db_cursor.execute("""--sql
        select Intersections.Intersection, Intersections.Intersection_ID, 
        count(RedCameras.Camera_ID) as num_cameras,
        count(RedCameras.Camera_ID) * 100.0 / (select count(RedCameras.Camera_ID) from RedCameras)
        from Intersections join RedCameras on Intersections.Intersection_ID = RedCameras.Intersection_ID
        group by Intersections.Intersection_ID
        order by num_cameras desc
        
    """)
    red_cam_intersection_info = db_cursor.fetchall()


    db_cursor.execute("""--sql
        select Intersections.Intersection, Intersections.Intersection_ID, 
        count(SpeedCameras.Camera_ID) as num_cameras,
        count(SpeedCameras.Camera_ID) * 100.0 / (select count(SpeedCameras.Camera_ID) from SpeedCameras)
        from Intersections join SpeedCameras on Intersections.Intersection_ID = SpeedCameras.Intersection_ID
        group by Intersections.Intersection_ID
        order by num_cameras desc
        
    """)
    speed_cam_intersection_info = db_cursor.fetchall()

    if red_cam_intersection_info and speed_cam_intersection_info:
        print("\nNumber of Red Light Cameras at Each Intersection")
        print("\n".join( f"  {intersection} ({intersection_id}) : {num_cameras} ({perc:.3f}%)" for intersection, intersection_id, num_cameras, perc in red_cam_intersection_info ))
        print("\nNumber of Speed Cameras at Each Intersection")
        print("\n".join( f"  {intersection} ({intersection_id}) : {num_cameras} ({perc:.3f}%)" for intersection, intersection_id, num_cameras, perc in speed_cam_intersection_info ))
    else:
        print("No intersections found.")
        
def find_num_violations_at_each_intersection(db_conn: sqlite3.Connection, violation_year: int) -> None:
    """
    Given a connection to the database and a year, 
    prints the number of violations at each intersection.

    Args:
        db_conn (sqlite3.Connection): A connection to the database.
        violation_year (int): The year to search for.
    """

    db_cursor = db_conn.cursor()

    db_cursor.execute("""--sql
        select Intersections.Intersection, Intersections.Intersection_ID, 
        sum(RedViolations.Num_Violations) as num_violations,
        sum(RedViolations.Num_Violations) * 100.0 / (select sum(RedViolations.Num_Violations) from RedViolations where strftime('%Y', Violation_Date) = ? )
        from Intersections join RedCameras on Intersections.Intersection_ID = RedCameras.Intersection_ID
        join RedViolations on RedCameras.Camera_ID = RedViolations.Camera_ID
        where strftime('%Y', Violation_Date) = ?
        group by Intersections.Intersection_ID
        order by num_violations desc
    """, ( violation_year, violation_year ))

    red_cam_intersection_info_by_year = db_cursor.fetchall()

    db_cursor.execute("""--sql
        select Intersections.Intersection, Intersections.Intersection_ID, 
        sum(SpeedViolations.Num_Violations) as num_violations,
        sum(SpeedViolations.Num_Violations) * 100.0 / (select sum(SpeedViolations.Num_Violations) from SpeedViolations where strftime('%Y', Violation_Date) = ? )
        from Intersections join SpeedCameras on Intersections.Intersection_ID = SpeedCameras.Intersection_ID
        join SpeedViolations on SpeedCameras.Camera_ID = SpeedViolations.Camera_ID
        where strftime('%Y', Violation_Date) = ?
        group by Intersections.Intersection_ID
        order by num_violations desc
    """, ( violation_year, violation_year ))

    speed_cam_intersection_info_by_year = db_cursor.fetchall()

    if red_cam_intersection_info_by_year:
        print(f"\nNumber of Red Light Violations at Each Intersection for {violation_year}")
        print("\n".join( f"  {intersection} ({intersection_id}) : {num_violations:,} ({perc:.3f}%)" for intersection, intersection_id, num_violations, perc in red_cam_intersection_info_by_year ))
        print(f"Total Red Light Violations in {violation_year} : {sum( num_violations for _, _, num_violations, _ in red_cam_intersection_info_by_year ):,}" )
    else:
        print(f"\nNumber of Red Light Violations at Each Intersection for {violation_year}")
        print("No red light violations on record for that year.")
    
    if speed_cam_intersection_info_by_year:
        print(f"\nNumber of Speed Violations at Each Intersection for {violation_year}")
        print("\n".join( f"  {intersection} ({intersection_id}) : {num_violations:,} ({perc:.3f}%)" for intersection, intersection_id, num_violations, perc in speed_cam_intersection_info_by_year ))
        print(f"Total Speed Violations in {violation_year} : {sum( num_violations for _, _, num_violations, _ in speed_cam_intersection_info_by_year ):,}" )
    else:
        print(f"\nNumber of Speed Violations at Each Intersection for {violation_year}")
        print("No speed violations on record for that year.")

def num_violation_by_cam_id(db_conn: sqlite3.Connection, camera_id: int) -> None:
    """
    Given a connection to the database and a camera ID, 
    prints the number of violations by year.

    Args:
        dbConn (sqlite3.Connection): A connection to the database.
        camera_id (int): The ID of the camera to search for.
    """

    db_cursor = db_conn.cursor()
    db_cursor.execute("""--sql
        select strftime('%Y', Violation_Date) as year, sum(Num_Violations) as num_violations
        from (
            select Violation_Date, Num_Violations from RedViolations where Camera_ID = ?
            union all
            select Violation_Date, Num_Violations from SpeedViolations where Camera_ID = ?
        )
        group by year
        order by year asc
    """, ( camera_id, camera_id ))

    violation_stats = db_cursor.fetchall()
    if not violation_stats:
        print( f"No cameras matching that ID were found in the database." )
        return

    # Print results
    print(f"Yearly Violations for Camera {camera_id}")
    print("\n".join( f"{year} : {total_violations:,}" for year, total_violations in violation_stats ))

    # Asking user if they want to plot the data
    to_plot = True if input( "Plot? (y/n) " ) == "y" else False

    if to_plot:
        # Unzipping the violation stats
        year, total_violations = zip(*violation_stats)

        # Converting the years to integers
        years = list(map( int, year ))

        plt.plot( years, total_violations, color='b', linestyle='-', label=f"Yearly Violation for Camera {camera_id}" )
        plt.xlabel("Year")
        plt.xticks( years )
        plt.ylabel("Number of Violations")
        plt.show()
    
def num_violation_by_month_by_cam_id( db_conn: sqlite3.Connection, camera_id: int ) -> None:
    """
    Given a connection to the database, a camera ID, and a year, 
    prints the number of violations by month.

    Args:
        dbConn (sqlite3.Connection): A connection to the database.
        camera_id (int): The ID of the camera to search for.
        year (int): The year to search for.
    """

    db_cursor = db_conn.cursor()

    db_cursor.execute("""--sql
        select *  from (
            select Camera_ID from RedCameras
            union 
            select Camera_ID from SpeedCameras
        ) where Camera_ID = ?

    """, ( camera_id, ))

    is_camera_id_valid = True if db_cursor.fetchone() else False

    # Guard clause
    if not is_camera_id_valid:
        print( f"No cameras matching that ID were found in the database." )
        return

    # Asking user for the year
    year: str = input( "Enter a year: " )

    db_cursor.execute("""--sql
        select strftime('%m', Violation_Date) as month, sum(Num_Violations) as num_violations
        from (
            select Violation_Date, Num_Violations from RedViolations where Camera_ID = ? and strftime('%Y', Violation_Date) = ?
            union all
            select Violation_Date, Num_Violations from SpeedViolations where Camera_ID = ? and strftime('%Y', Violation_Date) = ?
        ) 
        group by month
        order by month asc
    """, ( camera_id, year, camera_id, year ))

    violation_stats = db_cursor.fetchall()

    print(f"Monthly Violations for Camera {camera_id} in {year}")
    print("\n".join( f"{month}/{year} : {total_violations:,}" for month, total_violations in violation_stats ))

    # Asking user if they want to plot the data
    to_plot = True if input( "Plot? (y/n) " ) == "y" else False

    if to_plot:
        # Unzipping the violation stats
        month, total_violations = zip(*violation_stats)

        # Converting the months to integers
        months = list(map( int, month ))

        plt.plot( months, total_violations, color='b', linestyle='-', label=f"Monthly Violation for Camera {camera_id} in {year}" )
        plt.xlabel("Month")
        plt.xticks( months )
        plt.ylabel("Number of Violations")
        plt.show()

def num_total_violations_by_day_comparison (db_conn: sqlite3.Connection, year: str) -> None:
    """
    Given a connection to the database and a year, 
    prints the number of violations by day.
    Also, asks the user if they want to plot the data
    to compare the number of red light and speed violations.

    Args:
        dbConn (sqlite3.Connection): A connection to the database.
        year (str): The year to search for.
    """

    db_cursor = db_conn.cursor()

    db_cursor.execute("""--sql
        select strftime('%Y-%m-%d', Violation_Date) as day, coalesce( sum(Num_Violations), 0 ) as num_violations
        from (
            select Violation_Date, Num_Violations from RedViolations where strftime('%Y', Violation_Date) = ?
        ) 
        group by day
        order by day asc
    """, ( year, ))

    red_cam_violations_per_day = dict( db_cursor.fetchall() )

    db_cursor.execute("""--sql
        select strftime('%Y-%m-%d', Violation_Date) as day, coalesce( sum(Num_Violations), 0 ) as num_violations
        from (
            select Violation_Date, Num_Violations from SpeedViolations where strftime('%Y', Violation_Date) = ?
        ) 
        group by day
        order by day asc
    """, ( year, ))

    speed_cam_violations_per_day = dict( db_cursor.fetchall() )

    date_range_start = datetime.date(int(year), 1, 1)
    date_range_end = datetime.date(int(year), 12, 31)
    full_date_range = [date_range_start + datetime.timedelta(days=i) for i in range((date_range_end - date_range_start).days + 1)]

    # Performing data impuation to handle missing data. So imputing missing values with 0
    # When getting since date is a datetime object, we need to convert it to a string to get the value from the dictionary
    # since the dictionary keys are strings and not datetime objects.
    red_cam_violations = [ red_cam_violations_per_day.get( date.strftime('%Y-%m-%d'), 0 ) for date in full_date_range ]
    speed_cam_violations = [ speed_cam_violations_per_day.get( date.strftime('%Y-%m-%d'), 0 ) for date in full_date_range ]

    # Extracting the dates with valid values associated with them i.e. not 0 to output to the user.
    red_cam_dates = [ date for date in full_date_range if red_cam_violations_per_day.get( date.strftime('%Y-%m-%d'), 0 ) > 0 ]
    speed_cam_dates = [ date for date in full_date_range if speed_cam_violations_per_day.get( date.strftime('%Y-%m-%d'), 0 ) > 0 ]
    
    # Print results
    # Since the results are too long to be outputted, we will only print the first and the last 5 results.
    print("Red Light Violations:")
    print("\n".join( 
        f"{date} {red_cam_violations_per_day.get( date.strftime('%Y-%m-%d' ), 0 )}"
        for date in ( red_cam_dates[:5] + red_cam_dates[-5:] ) 
    ))

    print("Speed Violations:")
    print("\n".join( 
        f"{ date } {speed_cam_violations_per_day.get( date.strftime( '%Y-%m-%d' ), 0 )}" 
        for date in ( speed_cam_dates[:5] + speed_cam_dates[-5:] ) 
    ))

    # Asking user if they want to plot the data
    to_plot: bool = True if input( "Plot? (y/n) " ) == "y" else False

    if to_plot:
        # Converting dates to x values for plotting
        x_values: List[int] = list(range(len( full_date_range )))

        plt.plot( x_values , red_cam_violations, color='red', linestyle='-', label=f"Red Light" )
        plt.plot( x_values , speed_cam_violations, color='orange', linestyle='-', label=f"Speed" )
        plt.xlabel("Day")
        plt.legend(loc='upper right')
        plt.title( f"Violations Each Day of {year}" )
        plt.xticks(ticks=range(0, max( x_values ), 50))  # Tick every 50 days
        plt.ylabel("Number of Violations")
        plt.show()

def find_cameras_on_a_street( db_conn: sqlite3.Connection, street_to_search_by_name: str):
    """
    Given a connection to the database and a street name,
    prints the cameras located on that street.

    Args:
        db_conn (sqlite3.Connection): _description_
        street_name (str): _description_
    """
    
    db_cursor = db_conn.cursor()

    # Converting the street name to uppercase
    # since the database stores the street names in uppercase
    street_name = street_to_search_by_name.upper()

    db_cursor.execute("""--sql
        select Camera_ID, Address, Latitude, Longitude
        from RedCameras
        where Address like ?
        order by Camera_ID asc
    """, ( f"%{street_name}%", ))

    red_cameras = db_cursor.fetchall()

    db_cursor.execute("""--sql
        select Camera_ID, Address, Latitude, Longitude
        from SpeedCameras
        where Address like ?
        order by Camera_ID asc
    """, ( f"%{street_name}%", ))

    speed_cameras = db_cursor.fetchall()

    # If no cameras are found, print a message to the user
    if not ( red_cameras or speed_cameras ):
        print( "There are no cameras located on that street." )
        return
    print()

    # Printing the results
    print( f"List of Cameras Located on Street: {street_to_search_by_name}" )
    print( "  Red Light Cameras:" )
    if red_cameras:
        print( "\n".join( f"     {cam_id} : {address} ({lat}, {long})" for cam_id, address, lat, long in red_cameras ) )
    print( "  Speed Cameras:" )
    if speed_cameras:
        print( "\n".join( f"     {cam_id} : {address} ({lat}, {long})" for cam_id, address, lat, long in speed_cameras ) )

    # Asking user if they want to plot the data
    to_plot = True if input( "Plot? (y/n) " ) == "y" else False
    
    if to_plot:

        chicago_map_image = plt.imread("chicago.png")
        xydims = [-87.9277, -87.5569, 41.7012, 42.0868]  # Chicago area map boundaries
        plt.imshow(chicago_map_image, extent=xydims)
        plt.title(f"Cameras on {street_to_search_by_name}")

        # Populating the x and y lists with (x, y) coordinates
        # Longitude is the x-coordinate and Latitude is the y-coordinate
        red_cam_x = [ long for _, _, _, long in red_cameras ]
        red_cam_y = [ lat for _, _, lat, _ in red_cameras ]
        speed_cam_x = [ long for _, _, _, long in speed_cameras ]
        speed_cam_y = [ lat for _, _, lat, _ in speed_cameras ]

        # Plotting the points on the map
        plt.plot(red_cam_x, red_cam_y, color='red', marker='o', linestyle='-',label='Red Light Cameras')
        plt.plot(speed_cam_x, speed_cam_y, color='orange', marker='o', linestyle='-', label='Speed Cameras')

        # Annotating each (long, lat) coordinate with the camera ID
        for cam_id, _, lat, long in red_cameras:
            plt.annotate( str(cam_id), (long, lat) )

        for cam_id, _, lat, long in speed_cameras:
            plt.annotate( str(cam_id), (long, lat) )
        
        # Limiting the x and y axis to the Chicago area map boundaries\
        plt.xlim(xydims[:2])
        plt.ylim(xydims[2:])
        
        # Show plt
        plt.show()


def print_menu() -> None:
    print("Select a menu option: ")
    print("  1. Find an intersection by name")
    print("  2. Find all cameras at an intersection")
    print("  3. Percentage of violations for a specific date")
    print("  4. Number of cameras at each intersection")
    print("  5. Number of violations at each intersection, given a year")
    print("  6. Number of violations by year, given a camera ID")
    print("  7. Number of violations by month, given a camera ID and year")
    print("  8. Compare the number of red light and speed violations, given a year")
    print("  9. Find cameras located on a street")
    print("or x to exit the program.")
    
#
# main
#
db_conn = sqlite3.connect('chicago-traffic-cameras.db')

print("Project 1: Chicago Traffic Camera Analysis")
print("CS 341, Spring 2025")
print()
print("This application allows you to analyze various")
print("aspects of the Chicago traffic camera database.")
print()
print_stats(db_conn)
print()

print_menu()

user_choice = input("Your choice --> ")

while (not validate_input(user_choice)):
    print("Error, unknown command, try again...")
    print_menu()
    user_choice = input("Your choice --> ")

while user_choice != "x":
    if user_choice == "1":
        print()
        intersection_name = input("Enter the name of the intersection to find (wildcards _ and % allowed): ")
        find_intersection_by_name( db_conn, intersection_name )
    elif user_choice == "2":
        print()
        intersection_address = input("Enter the name of the intersection (no wildcards allowed): ")
        print()
        find_cameras_by_intersection( db_conn, intersection_address )
    elif user_choice == "3":
        print()
        violation_date = input("Enter the date that you would like to look at (format should be YYYY-MM-DD): ")
        find_num_violations_by_date( db_conn, violation_date )
    elif user_choice == "4":
        print()
        find_num_cameras_at_each_intersection( db_conn )
    elif user_choice == "5":
        print()
        violation_year = input("Enter the year that you would like to analyze: ")
        find_num_violations_at_each_intersection( db_conn, violation_year )
    elif user_choice == "6":
        print()
        cam_id = input("Enter a camera ID: ")
        num_violation_by_cam_id( db_conn, cam_id )
    elif user_choice == "7":
        print()
        cam_id = input( "Enter a camera ID: " )
        num_violation_by_month_by_cam_id( db_conn, cam_id )
    elif user_choice == "8":
        print()
        violation_year = input("Enter a year: ")
        num_total_violations_by_day_comparison( db_conn, violation_year )
    elif user_choice == "9":
        print()
        street_name = input("Enter a street name: ")
        find_cameras_on_a_street(db_conn, street_name)

    print()
    print_menu()
    user_choice = input("Your choice --> ")

    while (not validate_input(user_choice)):
        print("Error, unknown command, try again...")
        print_menu()
        user_choice = input("Your choice --> ")



print("Exiting program.")
exit() # Done
