# Intro
You will be parsing and analyzing hourly weather data from Hartsfield-Jackson Airport and Canadian, TX.

# Provided
Attached are two CSV files with hourly weather data for Hartsfield-Jackson Airport and Canadian, TX.
Also included is the Local Climatological Data (LCD) Dataset Documentation, which contains definitions of weather codes within the data set.

# Instructions
Please select one of the following languages with which to complete the test. If you would like to use a different language, feel free to ask us.

- Java
- Python
- Rust

Include a `README_solution.txt` file which includes the following:

- which version of the language you are using. Ensure you do not use platform-specific features as your solution may be tested on Mac, Linux, or Windows.
- a short paragraph justifying or explaining your language choice.
- optionally, an explanation or documentation of your code.

Note: PLEASE DO NOT INCLUDE YOUR NAME IN THE README OR CODE!

## Requirements
Read the data as input and write three methods:

1. a method that takes a data set and a date as its arguments and returns a data structure with the average and sample standard deviation of the Fahrenheit dry-bulb temperature between the times of sunrise and sunset.
2. a method that takes a data set and a date as its arguments and returns the wind chills rounded to the nearest integer for the times when the temperature is less than or equal to 40 degrees Fahrenheit.
3. a method that reads both data sets and finds the single same day in which the conditions in Canadian, TX, were most similar to Atlanta's Hartsfield-Jackson Airport.
You may use any column(s) for your similarity metric, but be prepared to justify your choice of measurements.

Try to apply the best practices for your language of choice and keep your code clean: we are grading your code too, not just your ability to find the correct answers to the questions.

## Interface for Grading
In order for us to pre-grade your code, you also need to adhere to a strict, standardized input/output interface.
Accordingly, you must provide a command-line entrypoint that accepts input in the following formats:

The first argument will be either `daylight_temp` (to invoke Method 1), `windchills` (to invoke Method 2), or `similar-day` to invoke Method 3.

### Method 1
For method 1, the command line input will be:

    daylight_temp <path-to-csv-file-here> <date in YYYY-MM-dd format>

The output (on stdout) should be:

    <average temp>
    <sample standard deviation of temp>

### Method 2
For method 2, the command line input will be:

    windchills <path-to-csv-file-here> <date in YYYY-MM-dd format>

The output (on stdout) should be:

    windchill1
    windchill2
    ...
    windchillN

### Method 3
For method 3, the command line input will be:

    similar-day <path-to-csv-file-1> <path-to-csv-file-2>

The output (on stdout) should be:

    <YYYY-MM-dd>


### Auto-grading
We will be autograding your tests as a first-pass.
Therefore, please adhere to the following requirements:

- Do not use any external / 3rd-party libraries. If you want to write your own library, please do!
- If you are using Python, please place your entrypoint in a `main.py`. We will test your code by running `python3.11 main.py <arguments as described above>`
- If you are using Java, please place your entrypoint in a `Main.java`. We will test your code with Java 19 by running `javac *.java; java Main <arguments as described above>`
- If you are using Rust, we will test your code by running `cargo run -- <arguments as described above>`

# Submission
Please submit a `.zip` or `.tar.gz` archive named `CIPHER_weather_test` containing your source code.

Please do NOT include:
- Your name anywhere in the submission or filenames.
- Bytecode, machine code, or non-source code.
