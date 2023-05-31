from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date
from baham.constants import TOWNS
from baham.enum_types import UserType, VehicleStatus, VehicleType

from baham.models import Contract, Vehicle, VehicleModel, UserProfile

# Create your tests here.



class VehicleTest(TestCase):

    def setUp(self):
        self.superuser = User.objects.create(username='admin', email='admin@gmail.com', password='abc123@@')
        return super().setUp()
    

    def test_one_vehicle_per_owner(self):
        hani = User.objects.create(username='Hani', email='hani@gmail.com', password='abc123def')
        hondacity = VehicleModel.objects.create(vendor='Honda', model='City', type=VehicleType.SEDAN, capacity=4)
        hondacivic = VehicleModel.objects.create(vendor='Honda', model='Civic', type=VehicleType.SEDAN, capacity=4)
        kuy765 = Vehicle.objects.create(registration_number='KUY-765', colour='#ff00ff', model=hondacity, 
                                        owner=hani, status=VehicleStatus.FULL)        
        with self.assertRaises(Exception):
            kuy822 = Vehicle.objects.create(registration_number='KUY-822', colour='#ff00ff', model=hondacivic, 
                                        owner=hani, status=VehicleStatus.AVAILABLE)
            


class ContractTest(TestCase):

    def setUp(self):
        self.superuser = User.objects.create(username='admin', email='admin@gmail.com', password='abc123@@')
        return super().setUp()
    
    def test_no_more_passengers_than_vehicle_sitting_capacity(self):
        hani = User.objects.create(username='Hani', email='hani@gmail.com', password='abc123def')
        hondacity = VehicleModel.objects.create(vendor='Honda', model='City', type=VehicleType.SEDAN, capacity=4)
        kuy765 = Vehicle.objects.create(registration_number='KUY-765', colour='#ff00ff', model=hondacity, 
                                        owner=hani, status=VehicleStatus.AVAILABLE)
        hamza = User.objects.create(username='Hamza', email='hamza@gmail.com', password='abc123def')
        saad = User.objects.create(username='Saad', email='saad@gmail.com', password='abc123def')
        faizan = User.objects.create(username='Faizan', email='faizan@gmail.com', password='abc123def')
        talha = User.objects.create(username='Talha', email='talha@gmail.com', password='abc123def')
        shaheer = User.objects.create(username='Shaheer', email='shaheer@gmail.com', password='abc123def')
        test_date = date(2023, 5, 31)
        test_date_str = test_date.isoformat()
        user1 = UserProfile.objects.create(user=hamza, birthdate=test_date_str, gender='M', type=UserType.COMPANION, primary_contact="03178690353",
                                           address="Gulistan-e-Johar", landmark="Balochistan Sajji", town='Gulshan-e-Iqbal')
        user2 = UserProfile.objects.create(user=saad, birthdate=test_date_str, gender='M', type=UserType.COMPANION, primary_contact="03178690353",
                                           address="Gulistan-e-Johar", landmark="Balochistan Sajji", town='Gulshan-e-Iqbal')
        user3 = UserProfile.objects.create(user=faizan, birthdate=test_date_str, gender='M', type=UserType.COMPANION, primary_contact="03178690353",
                                           address="Gulistan-e-Johar", landmark="Balochistan Sajji", town='Gulshan-e-Iqbal')
        user4 = UserProfile.objects.create(user=talha, birthdate=test_date_str, gender='M', type=UserType.COMPANION, primary_contact="03178690353",
                                           address="Gulistan-e-Johar", landmark="Balochistan Sajji", town='Gulshan-e-Iqbal')
        user5 = UserProfile.objects.create(user=shaheer, birthdate=test_date_str, gender='M', type=UserType.COMPANION, primary_contact="03178690353",
                                           address="Gulistan-e-Johar", landmark="Balochistan Sajji", town='Gulshan-e-Iqbal')
        contract1 = Contract.objects.create(vehicle=kuy765, companion=user1, effective_start_date=test_date_str, expiry_date=test_date_str, fuel_share=50, 
                                            maintenance_share=40, schedule='Monday 1st Slot')
        contract2 = Contract.objects.create(vehicle=kuy765, companion=user2, effective_start_date=test_date_str, expiry_date=test_date_str, fuel_share=50, 
                                            maintenance_share=40, schedule='Monday 1st Slot')
        contract3 = Contract.objects.create(vehicle=kuy765, companion=user3, effective_start_date=test_date_str, expiry_date=test_date_str, fuel_share=50, 
                                            maintenance_share=40, schedule='Monday 1st Slot')
        contract4 = Contract.objects.create(vehicle=kuy765, companion=user4, effective_start_date=test_date_str, expiry_date=test_date_str, fuel_share=50, 
                                            maintenance_share=40, schedule='Monday 1st Slot')
        with self.assertRaises(Exception):
            contract5 = Contract.objects.create(vehicle=kuy765, companion=user5, effective_start_date=test_date_str, expiry_date=test_date_str, fuel_share=50, 
                                            maintenance_share=40, schedule='Monday 1st Slot')
            

        
    def test_total_share_cannot_exceed_hundred_on_record_creation(self):
        hani = User.objects.create(username='Hani', email='hani@gmail.com', password='abc123def')
        hondacity = VehicleModel.objects.create(vendor='Honda', model='City', type=VehicleType.SEDAN, capacity=4)
        kuy765 = Vehicle.objects.create(registration_number='KUY-765', colour='#ff00ff', model=hondacity, 
                                        owner=hani, status=VehicleStatus.AVAILABLE)
        test_date = date(2023, 5, 31)
        test_date_str = test_date.isoformat()
        hamza = User.objects.create(username='Hamza', email='hamza@gmail.com', password='abc123def')
        user1 = UserProfile.objects.create(user=hamza, birthdate=test_date_str, gender='M', type=UserType.COMPANION, primary_contact="03178690353",
                                           address="Gulistan-e-Johar", landmark="Balochistan Sajji", town='Gulshan-e-Iqbal')
        with self.assertRaises(Exception):
            contract1 = Contract.objects.create(vehicle=kuy765, companion=user1, effective_start_date=test_date_str, expiry_date=test_date_str, fuel_share=110, 
                                            maintenance_share=90, schedule='Monday 1st Slot')


    def test_total_share_cannot_exceed_hundred_on_record_updation(self):
        hani = User.objects.create(username='Hani', email='hani@gmail.com', password='abc123def')
        hondacity = VehicleModel.objects.create(vendor='Honda', model='City', type=VehicleType.SEDAN, capacity=4)
        kuy765 = Vehicle.objects.create(registration_number='KUY-765', colour='#ff00ff', model=hondacity, 
                                        owner=hani, status=VehicleStatus.AVAILABLE)
        test_date = date(2023, 5, 31)
        test_date_str = test_date.isoformat()
        hamza = User.objects.create(username='Hamza', email='hamza@gmail.com', password='abc123def')
        user1 = UserProfile.objects.create(user=hamza, birthdate=test_date_str, gender='M', type=UserType.COMPANION, primary_contact="03178690353",
                                           address="Gulistan-e-Johar", landmark="Balochistan Sajji", town='Gulshan-e-Iqbal')
        contract1 = Contract.objects.create(vehicle=kuy765, companion=user1, effective_start_date=test_date_str, expiry_date=test_date_str, fuel_share=50, 
                                            maintenance_share=20, schedule='Monday 1st Slot')
        with self.assertRaises(Exception):
            contract1.fuel_share=100
            contract1.maintenance_share = 50
            contract1.update()

    
    def test_companions_cannot_have_multiple_active_contracts_simultaneously(self):
        hani = User.objects.create(username='Hani', email='hani@gmail.com', password='abc123def')
        hondacity = VehicleModel.objects.create(vendor='Honda', model='City', type=VehicleType.SEDAN, capacity=4)
        kuy765 = Vehicle.objects.create(registration_number='KUY-765', colour='#ff00ff', model=hondacity, 
                                        owner=hani, status=VehicleStatus.AVAILABLE)
        hamza = User.objects.create(username='Hamza', email='hamza@gmail.com', password='abc123def')
        hondacivic = VehicleModel.objects.create(vendor='Honda', model='Civic', type=VehicleType.SEDAN, capacity=4)
        kuy875 = Vehicle.objects.create(registration_number='KUY-875', colour='#ff00ff', model=hondacivic, 
                                        owner=hamza, status=VehicleStatus.AVAILABLE)
        test_date = date(2023, 5, 31)
        test_date_str = test_date.isoformat()
        saad = User.objects.create(username='Saad', email='saad@gmail.com', password='abc123def')
        user1 = UserProfile.objects.create(user=saad, birthdate=test_date_str, gender='M', type=UserType.COMPANION, primary_contact="03178690353",
                                           address="Gulistan-e-Johar", landmark="Balochistan Sajji", town='Gulshan-e-Iqbal')
        contract1 = Contract.objects.create(vehicle=kuy765, companion=user1, effective_start_date=test_date_str, expiry_date=test_date_str, fuel_share=50, 
                                            maintenance_share=40, schedule='Monday 1st Slot')
        with self.assertRaises(Exception):
            contract2 = Contract.objects.create(vehicle=kuy875, companion=user1, effective_start_date=test_date_str, expiry_date=test_date_str, fuel_share=50, 
                                            maintenance_share=40, schedule='Monday 1st Slot')
        
        
