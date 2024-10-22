# from django.core.management.base import BaseCommand
# from wallefy_backend.models import Location, LocationWiseCategoryDetails
# import csv
# import os
#
# class Command(BaseCommand):
#     help = 'Imports data from the CSV file to the database.'
#
#     def handle(self, *args, **kwargs):
#         # Path to the CSV file, adjust for the correct file path
#         csv_file_path = 'Hackhaton - dummy.csv'
#
#         # Ensure the file exists
#         if not os.path.exists(csv_file_path):
#             self.stdout.write(self.style.ERROR(f"File not found: {csv_file_path}"))
#             return
#
#         # Open and read the CSV file
#         try:
#             with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
#                 csvreader = csv.reader(csvfile)
#
#                 # Skip the header
#                 next(csvreader)
#
#                 # Iterate over each row in the CSV
#                 for row in csvreader:
#                     try:
#                         location_name = row[0]  # The location or area
#                         preference = row[1]  # The preference (e.g., RICH)
#                         print(preference,"***********")
#                         gender = row[2]  # Gender (e.g., MALE or FEMALE)
#                         rent = float(row[3])  # Rent percentage
#                         food = float(row[4])  # Food percentage
#                         shopping = float(row[5])  # Shopping percentage
#                         travelling = float(row[6])  # Travelling percentage
#                         health = float(row[7])  # Health percentage
#                         entertainment = float(row[8])  # Entertainment percentage
#                         savings = float(row[9])  # Savings percentage
#                         miscellaneous = float(row[10])  # Miscellaneous percentage
#
#                         # Print for visibility (optional)
#                         print(f"Processing Location: {location_name}, Preference: {preference}, Gender: {gender}")
#
#                         # Get or create the Location entry
#                         location, created = Location.objects.get_or_create(
#                             City=location_name,
#                             area=location_name
#                         )
#
#                         # Get or create the LocationWiseCategoryDetails entry
#                         location_category, created = LocationWiseCategoryDetails.objects.get_or_create(
#                             location=location,
#                             preference=preference,
#                             gender=gender,
#                             defaults={
#                                 'Rent_percentage': rent,
#                                 'Food_percentage': food,
#                                 'Shopping_percentage': shopping,
#                                 'Travelling_percentage': travelling,
#                                 'Health_percentage': health,
#                                 'Entertainment_percentage': entertainment,
#                                 'Savings_percentage': savings,
#                                 'Miscellaneous_percentage': miscellaneous,
#                             }
#                         )
#
#                         # If the record already exists, update the percentages
#                         if not created:
#                             location_category.Rent_percentage = rent
#                             location_category.Food_percentage = food
#                             location_category.Shopping_percentage = shopping
#                             location_category.Travelling_percentage = travelling
#                             location_category.Health_percentage = health
#                             location_category.Entertainment_percentage = entertainment
#                             location_category.Savings_percentage = savings
#                             location_category.Miscellaneous_percentage = miscellaneous
#                             location_category.save()
#
#                         # Print completion message (optional)
#                         print(f"Saved Location: {location_name}, Preference: {preference}, Gender: {gender}")
#
#                     except ValueError as ve:
#                         self.stdout.write(self.style.ERROR(f"Error in row {row}: {ve}"))
#
#         except FileNotFoundError:
#             self.stdout.write(self.style.ERROR(f"File not found: {csv_file_path}"))
#
#         self.stdout.write(self.style.SUCCESS('Successfully imported data from CSV!'))


from django.core.management.base import BaseCommand
from wallefy_backend.models import Location, LocationWiseCategoryDetails
import csv
import os


class Command(BaseCommand):
    help = 'Imports data from the CSV file to the database.'

    def handle(self, *args, **kwargs):
        # Path to the CSV file, adjust for the correct file path
        csv_file_path = 'Hackhaton - Sheet1.csv'

        # Ensure the file exists
        if not os.path.exists(csv_file_path):
            self.stdout.write(
                self.style.ERROR(f"File not found: {csv_file_path}"))
            return

        # Open and read the CSV file
        try:
            with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
                csvreader = csv.reader(csvfile)

                # Skip the header
                next(csvreader)

                # Iterate over each row in the CSV
                for row in csvreader:
                    # Check if the row has the required number of columns (11 columns)
                    if len(row) < 11:
                        self.stdout.write(self.style.ERROR(
                            f"Incomplete row, skipping: {row}"))
                        continue  # Skip to the next row if incomplete

                    try:
                        # Map the data from the CSV columns to variables
                        city_name = row[0]  # The city or location
                        preference = row[1]  # The preference (e.g., RICH)
                        gender = row[2]  # Gender (e.g., MALE or FEMALE)
                        rent = float(row[3])  # Rent percentage
                        food = float(row[4])  # Food percentage
                        shopping = float(row[5])  # Shopping percentage
                        travelling = float(row[6])  # Travelling percentage
                        health = float(row[7])  # Health percentage
                        entertainment = float(
                            row[8])  # Entertainment percentage
                        savings = float(row[9])  # Savings percentage
                        miscellaneous = float(
                            row[10])  # Miscellaneous percentage

                        # Print for visibility (optional)
                        print(
                            f"Processing City: {city_name}, Preference: {preference}, Gender: {gender}")

                        # Get or create the Location entry
                        location, created = Location.objects.get_or_create(
                            City=city_name,
                            area=city_name
                            # Assuming area is the same as city for now
                        )

                        # Get or create the LocationWiseCategoryDetails entry
                        location_category, created = LocationWiseCategoryDetails.objects.get_or_create(
                            location=location,
                            preference=preference,
                            gender=gender,
                            defaults={
                                'Rent_percentage': rent,
                                'Food_percentage': food,
                                'Shopping_percentage': shopping,
                                'Travelling_percentage': travelling,
                                'Health_percentage': health,
                                'Entertainment_percentage': entertainment,
                                'Savings_percentage': savings,
                                'Miscellaneous_percentage': miscellaneous,
                            }
                        )

                        # If the record already exists, update the percentages
                        if not created:
                            location_category.Rent_percentage = rent
                            location_category.Food_percentage = food
                            location_category.Shopping_percentage = shopping
                            location_category.Travelling_percentage = travelling
                            location_category.Health_percentage = health
                            location_category.Entertainment_percentage = entertainment
                            location_category.Savings_percentage = savings
                            location_category.Miscellaneous_percentage = miscellaneous
                            location_category.save()

                        # Print completion message (optional)
                        print(
                            f"Saved City: {city_name}, Preference: {preference}, Gender: {gender}")

                    except ValueError as ve:
                        self.stdout.write(
                            self.style.ERROR(f"Error in row {row}: {ve}"))

        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f"File not found: {csv_file_path}"))

        self.stdout.write(
            self.style.SUCCESS('Successfully imported data from CSV!'))
