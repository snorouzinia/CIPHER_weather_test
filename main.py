import csv
from datetime import datetime, date
import math
import sys
#if the first input on the command line is:
    #daylight_temp -> method 1
    #windchills -> method 2
    #similar-day -> method 3

#helpers

#returns the oktas for this particular cell
def get_sky_condition(condition):
    #i saw some empty cells
    if not condition or not condition.strip():
        return None
    
    oktas = 0
    elems = condition.strip().split()
    for el in elems:
        try:
            coverage = el.split(":")[1]  # get "02 55" -> actually "02"
            okta_part = int(coverage[:2])
            oktas = max(oktas, okta_part)
        except (IndexError, ValueError): #this row is not valid, so just move on to the next
            continue
    return oktas

#this method will map each date to its oktas so we can use this to compare the two airports
def map_conditions(file_path):
    my_dict = {}
    my_file = open(file_path, "r", newline="")
    reader = csv.DictReader(my_file)
    for row in reader:
        dt = datetime.strptime(row["DATE"], "%m/%d/%y %H:%M")
        oktas = get_sky_condition(row["HOURLYSKYCONDITIONS"])

        #empty row
        if oktas is None:
            continue
        
        date = dt.date()
        if date not in my_dict:
            my_dict[date] = []
        my_dict[date].append(oktas)
    
    #convert dictionary values to be a single digit
    return {date: sum(oks) / len(oks) for date, oks in my_dict.items()}


#method1: returns average and SD for farenheit dry-bulb temperatures between sunrise and sunset
#date is in column 5
def daylight_temp(file_path, target_date):
    my_file = open(file_path, "r", newline="")
    reader = csv.DictReader(my_file)
    target_date = date.fromisoformat(target_date)
    sunrise = None
    sunset = None
    temps = []

    for row in reader:
        dt = datetime.strptime(row["DATE"], "%m/%d/%y %H:%M") #get the date from each row in reader. %H and %m and %d handle edge cases
        if dt.date() == target_date:
            if sunrise is None and row["DAILYSunrise"].strip():
                try: #there's always empty cells
                    sunrise = int(row["DAILYSunrise"].strip())
                except ValueError:
                    pass
            if sunset is None and row["DAILYSunset"].strip():
                try:
                    sunset = int(row["DAILYSunset"].strip())
                except ValueError:
                    pass
            if sunrise<=(dt.hour*100 + dt.minute)<=sunset:
                try:
                    temps.append(int(row["HOURLYDRYBULBTEMPF"].strip()))
                except ValueError: #some of the rows are in weird formats
                    print ("An entry was in the wrong format")
                    continue
        
        elif dt.date() > target_date:
            #the date does not exist in this csv file
            print("This date does not have recorded data")
            break

    my_file.close()

    #so there isnt any zero division
    if not temps: 
        print("No temperature data found for this date.")
        return
    average = sum(temps) / len(temps)

    if len(temps) < 2:
        return f"{average}\n0"

    variance = sum((t - average) ** 2 for t in temps) / (len(temps) - 1)
    std_dev = math.sqrt(variance)

    return f"{average}\n{std_dev}"


#looking for HOURLYWindSpeed
#using HOURLYDRYBULBTEMPF because it says it is the standard air temp
#national weather service says: WC = 35.74 + 0.6215T - 35.75(V^0.16) + 0.4275T(V^0.16) w/ T=temp and V=wind speed
def windchills(file_path, target_date):
    my_file = open(file_path, "r", newline="")
    reader = csv.DictReader(my_file)
    target_date = date.fromisoformat(target_date)
    sunrise = None
    sunset = None
    results = []

    for row in reader:
        try:
            dt = datetime.strptime(row["DATE"], "%m/%d/%y %H:%M")
        except ValueError: #empty cell
            continue
        if dt.date() == target_date:
            try:
                temp = float(row["HOURLYDRYBULBTEMPF"].strip())
                wind_speed = float(row["HOURLYWindSpeed"].strip())
            except ValueError: #again, empty cell
                continue
            
            if temp <= 40:
                windchill = (35.74 + 0.6215*temp - 35.75*(wind_speed**0.16) + 0.4275*temp*(wind_speed**0.16))
                results.append(round(windchill))

        elif dt.date() > target_date:
            #the date does not exist in this csv file
            print("This date does not have recorded data")
            break
            
    my_file.close()
    return results

#for this method we are using HOURLYSKYCONDITIONS oktas because there is documentation in LCD about
#sky conditions and this will be a well-rounded metric to use as a sole metric since it is 
#a numeric comparison
def similar_day(file_path1, file_path2):
    #dictionary mapping of date to condition
    atlanta = map_conditions(file_path1)
    canadian = map_conditions(file_path2)

    #bitwise operator to get a set with only the common days in the two dictionaries
    common_days = set(atlanta.keys()) & set(canadian.keys())

    if not common_days:
        return "There are no such days for these two datasets"

    best_day = None
    best_dif = float("inf")
    for day in common_days:
        dif = abs(atlanta[day]-canadian[day])
        if dif < best_dif:
            best_dif = dif
            best_day = day

    return best_day


#entry point
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Incorrect number of inputs given")
        sys.exit(1)
        
    inputs = sys.argv

    if inputs[1] == "daylight_temp": 
        #method 1
        result = daylight_temp(inputs[2], inputs[3])
        print(result)
    elif inputs[1] == "windchills":
        #method 2
        result = windchills(inputs[2], inputs[3])
        for val in result:
            print(val)
    elif inputs[1] == "similar-day": 
        #method 3
        result = similar_day(inputs[2], inputs[3])
        print(result)
    else:
        print("This is not a valid input")
        sys.exit()

