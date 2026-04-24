import unittest
from unittest.mock import patch, mock_open
import io
import sys

# ── import the functions you want to test ──────────────────────────────────────
from main import get_sky_condition, windchills, daylight_temp, similar_day, map_conditions

CSV_HEADER = "STATION,STATION_NAME,ELEVATION,LATITUDE,LONGITUDE,DATE,REPORTTPYE," \
             "HOURLYSKYCONDITIONS,HOURLYVISIBILITY,HOURLYPRSENTWEATHERTYPE," \
             "HOURLYDRYBULBTEMPF,HOURLYDRYBULBTEMPC,HOURLYWETBULBTEMPF," \
             "HOURLYWETBULBTEMPC,HOURLYDewPointTempF,HOURLYDewPointTempC," \
             "HOURLYRelativeHumidity,HOURLYWindSpeed,HOURLYWindDirection," \
             "HOURLYWindGustSpeed,HOURLYStationPressure,HOURLYPressureTendency," \
             "HOURLYPressureChange,HOURLYSeaLevelPressure,HOURLYPrecip," \
             "HOURLYAltimeterSetting,DAILYMaximumDryBulbTemp,DAILYMinimumDryBulbTemp," \
             "DAILYAverageDryBulbTemp,DAILYDeptFromNormalAverageTemp," \
             "DAILYAverageRelativeHumidity,DAILYAverageDewPointTemp," \
             "DAILYAverageWetBulbTemp,DAILYHeatingDegreeDays,DAILYCoolingDegreeDays," \
             "DAILYSunrise,DAILYSunset,DAILYWeather,DAILYPrecip,DAILYSnowfall," \
             "DAILYSnowDepth,DAILYAverageStationPressure,DAILYAverageSeaLevelPressure," \
             "DAILYAverageWindSpeed,DAILYPeakWindSpeed,PeakWindDirection," \
             "DAILYSustainedWindSpeed,DAILYSustainedWindDirection\n"

def make_row(date, sky="CLR:00", temp="32", wind="10",
             sunrise="700", sunset="1700"):
    """Helper: build a minimal CSV row with the columns main.py reads."""
    return (f"WBAN:13874,TEST,307,33,-84,{date},FM-15,"
            f"{sky},10,,{temp},,,,,,,"
            f"{wind},230,,28.98,,,30.09,0,30.08,"
            f",,,,,,,,,"
            f"{sunrise},{sunset},,,,,,,,,,\n")


class TestGetSkyCondition(unittest.TestCase):

    def test_clear_sky(self):
        self.assertEqual(get_sky_condition("CLR:00"), 0)

    def test_overcast(self):
        self.assertEqual(get_sky_condition("OVC:08 50"), 8)

    def test_multiple_layers_takes_max(self):
        # FEW:02 and BKN:06 → max should be 6
        self.assertEqual(get_sky_condition("FEW:02 100 BKN:06 50"), 6)

    def test_empty_string_returns_none(self):
        self.assertIsNone(get_sky_condition(""))

    def test_whitespace_only_returns_none(self):
        self.assertIsNone(get_sky_condition("   "))


class TestWindchills(unittest.TestCase):

    def _make_csv(self, rows):
        return CSV_HEADER + "".join(rows)

    def test_temp_above_40_excluded(self):
        """Rows with temp > 40 should produce no wind chill entries."""
        csv_data = self._make_csv([
            make_row("1/15/08 12:00", temp="41", wind="10", sunrise="700", sunset="1700")
        ])
        with patch("builtins.open", mock_open(read_data=csv_data)):
            result = windchills("fake.csv", "2008-01-15")
        self.assertEqual(result, [])

    def test_temp_exactly_40_included(self):
        """Temp exactly 40 satisfies <= 40 and should be included."""
        csv_data = self._make_csv([
            make_row("1/15/08 12:00", temp="40", wind="10", sunrise="700", sunset="1700")
        ])
        with patch("builtins.open", mock_open(read_data=csv_data)):
            result = windchills("fake.csv", "2008-01-15")
        self.assertEqual(len(result), 1)

    def test_known_windchill_value(self):
        """T=30, V=10 → WC = 35.74 + 0.6215*30 - 35.75*(10^0.16) + 0.4275*30*(10^0.16)
           ≈ 21.0, matches the NWS chart."""
        csv_data = self._make_csv([
            make_row("1/15/08 12:00", temp="30", wind="10", sunrise="700", sunset="1700")
        ])
        with patch("builtins.open", mock_open(read_data=csv_data)):
            result = windchills("fake.csv", "2008-01-15")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], 21)  # matches NWS chart value

    def test_missing_date_returns_empty(self):
        """A date not in the file should return an empty list."""
        csv_data = self._make_csv([
            make_row("1/15/08 12:00", temp="30", wind="10")
        ])
        with patch("builtins.open", mock_open(read_data=csv_data)):
            result = windchills("fake.csv", "2008-01-20")
        self.assertEqual(result, [])


class TestDaylightTemp(unittest.TestCase):

    def _make_csv(self, rows):
        return CSV_HEADER + "".join(rows)

    def test_average_and_stddev(self):
        """Two temps of 30 and 50 → avg=40, sample std dev=~14.14."""
        csv_data = self._make_csv([
            make_row("1/15/08 8:00",  temp="30", sunrise="700", sunset="1700"),
            make_row("1/15/08 12:00", temp="50", sunrise="700", sunset="1700"),
        ])
        with patch("builtins.open", mock_open(read_data=csv_data)):
            output = daylight_temp("fake.csv", "2008-01-15")
        avg, sd = output.split("\n")
        self.assertAlmostEqual(float(avg), 40.0)
        self.assertAlmostEqual(float(sd), 14.142, places=2)

    def test_outside_sunrise_sunset_excluded(self):
        """A row before sunrise should not count toward the average."""
        csv_data = self._make_csv([
            make_row("1/15/08 5:00",  temp="10", sunrise="700", sunset="1700"),  # before sunrise
            make_row("1/15/08 12:00", temp="40", sunrise="700", sunset="1700"),  # in window
        ])
        with patch("builtins.open", mock_open(read_data=csv_data)):
            output = daylight_temp("fake.csv", "2008-01-15")
        avg, _ = output.split("\n")
        self.assertEqual(float(avg), 40.0)


class TestSimilarDay(unittest.TestCase):

    def test_returns_closest_matching_day(self):
        """The day where okta values are closest across both files should be returned."""
        # File 1: Jan 1 okta=4, Jan 2 okta=8
        # File 2: Jan 1 okta=4, Jan 2 okta=0
        # Jan 1 has diff=0, Jan 2 has diff=8 → best is Jan 1
        file1 = (CSV_HEADER +
                 make_row("1/1/08 12:00", sky="SCT:04 50") +
                 make_row("1/2/08 12:00", sky="OVC:08 50"))
        file2 = (CSV_HEADER +
                 make_row("1/1/08 12:00", sky="SCT:04 50") +
                 make_row("1/2/08 12:00", sky="CLR:00"))

        opener = mock_open()
        opener.side_effect = [
            mock_open(read_data=file1)(),
            mock_open(read_data=file2)(),
        ]
        with patch("builtins.open", opener):
            result = similar_day("file1.csv", "file2.csv")
        from datetime import date
        self.assertEqual(result, date(2008, 1, 1))

    def test_no_common_days(self):
        file1 = CSV_HEADER + make_row("1/1/08 12:00", sky="CLR:00")
        file2 = CSV_HEADER + make_row("1/2/08 12:00", sky="CLR:00")
        opener = mock_open()
        opener.side_effect = [
            mock_open(read_data=file1)(),
            mock_open(read_data=file2)(),
        ]
        with patch("builtins.open", opener):
            result = similar_day("file1.csv", "file2.csv")
        self.assertEqual(result, "There are no such days for these two datasets")


if __name__ == "__main__":
    unittest.main(verbosity=2)