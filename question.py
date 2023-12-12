import json
import random
import boto3


class ParkingLot:
    def __init__(self, sq_ft, length=8, width=12, filename="parking_map.json"):
        self.sq_ft = sq_ft
        self.length = length
        self.width = width
        self.num_of_cars_in_lot = self.calculate_number_of_cars_in_lot()
        self.lot = [None]*self.num_of_cars_in_lot
        self.filename = filename

    def calculate_number_of_cars_in_lot(self):
        size = self.length * self.width
        return self.sq_ft//size

    def park_vechicle(self, car, spot_number):
        if 0 <= spot_number < self.num_of_cars_in_lot and self.lot[spot_number] is None:
            self.lot[spot_number] = car
            return True
        return False

    def is_full(self):
        return all(spot is not None for spot in self.lot)

    def generate_parking_map(self):
        parking_map = {
            f"Spot {i+1}": str(self.lot[i]) if self.lot[i] else "Empty" for i in range(self.num_of_cars_in_lot)}
        return parking_map

    def save_parking_map(self):
        with open(self.filename, 'w') as file:
            json.dump(self.generate_parking_map(), file, indent=4)

    def upload_to_s3(self, bucket_name, s3_file_name):
        s3 = boto3.client('s3')
        try:
            with self.lock:
                s3.upload_file(self.filename, bucket_name, s3_file_name)
            print(
                f"File {self.filename} uploaded to {bucket_name}/{s3_file_name}")
        except FileNotFoundError:
            print("The file was not found")
        except NoCredentialsError:
            print("Credentials not available")


class Car:
    def __init__(self, license_palate):
        self.license_palate = license_palate

    def __str__(self) -> str:
        return self.license_palate

    def park(self, parking_lot, spot_number):
        while spot_number < parking_lot.num_of_cars_in_lot:
            if parking_lot.lot[spot_number] is None:
                if parking_lot.park_vechicle(self, spot_number):
                    return f"the car with license number {self.license_palate} was parked successfully in spot {spot_number}"
            spot_number += 1

        return f"the car with license number {self.license_palate} was not parked successfully"


def main():
    car_range = int(
        input("Enter the range of car that is expected to come for parking"))
    area = input("Enter total parking area")

    parking_lot = ParkingLot(int(area))
    cars = [Car(f"{random.randint(1000000, 9999999)}")
            for _ in range(car_range)]

    while cars and not parking_lot.is_full():

        car = cars.pop()
        print(parking_lot.lot)
        spot = int(input("Enter the spot number: "))
        result = car.park(parking_lot, spot)

        print(result)

    if parking_lot.is_full():
        print("Parking is full")

    parking_lot.save_parking_map()

    bucket_name = 'enter-your-bucket-name'
    s3_file_name = 'parking_map.json'
    parking_lot.upload_to_s3(bucket_name, s3_file_name)


if __name__ == "__main__":
    main()
