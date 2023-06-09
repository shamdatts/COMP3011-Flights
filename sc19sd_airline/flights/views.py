from django.http import HttpResponse
from django.template import loader
from flights.models import FlightDetails, Passenger, Seat, Reservation
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
import json
from datetime import datetime
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from rest_framework.decorators import api_view

# Querying Flights
@api_view(['GET'])
def query_flights(request, date, departureAirport, destinationAirport):#, date
  # Check if the request method is GET
   if request.method == "GET":
      print(departureAirport)
      print(destinationAirport)
      try: 
      #Parse the date string into a datetime object
         flight_date = datetime.strptime(date, '%Y-%m-%d')
         print(flight_date)
      except ValueError: 
         #Return an error if the date format is invalid
         return JsonResponse({"message":"Invalid date format. Please use YYYY-MM-DD."}, status=400)
      
      # Query the Flight model for flights with the specified date, departure airport, and destination airport
      flights = FlightDetails.objects.filter(departureTime__date=flight_date,
                                             destinationAirport=destinationAirport, 
                                             departureAirport=departureAirport)
      print(flights)
      # Return a 404 response if no flights are found
      if (len(flights) == 0):
         return JsonResponse({"message": "No flights found"}, status=404, safe=False)
      
      # Serialize the flights queryset into a JSON string
      data = serializers.serialize('json', flights)
      # Load the JSON data into a Python data structure
      struct = json.loads(data)
      # Add a primary key field to the first flight in the data structure
      data = addFlightPK(struct[0])
      # Return a JSON response with the flight data
      return JsonResponse(data, status=200)
   else:
      # Return a 405 response if the request method is not GET
      return JsonResponse({"message": "Validation Exception"}, status=405)

# Creating reservations
@api_view(['POST'])
def create_reservation(request):
   # Check if request method is POST
   if request.method == 'POST':
      # Parse request body as JSON
      body = json.loads(request.body)
      print(body)
      try: 
         # Extract request parameters
         passengerId = body.get('passengerId')
         print(passengerId)
         seatId = body.get('seatId')
         print(seatId)
         holdLuggage = body.get('holdLuggage')
         print(holdLuggage)
         paymentConfirmed = body.get('paymentConfirmed')
         print(paymentConfirmed)

         # Check if all required fields are present and valid
         if not all([passengerId, seatId, isinstance(holdLuggage, bool), isinstance(paymentConfirmed, bool)]):
               print("405")
               return JsonResponse({"message": "Fields have been incorrectly inputted."}, status=405)
         try:
            # Retrieve objects from database
            #passenger = get_object_or_404(Passenger, pk=passengerId)
            passenger = Passenger.objects.get(pk=passengerId)
            print(passenger)
            #seat = get_object_or_404(Seat, pk=seatId)
            seat = Seat.objects.get(pk=seatId)
            print(seat)
         except (ObjectDoesNotExist, ValueError):
            # Handle exception if object does not exist or ID is not valid
            return JsonResponse({"message": "Invalid ID(s) provided."}, status=400)

         # Create new reservation object and save it to database
         reservation = Reservation(seatId=seat, 
                           passengerId=passenger, 
                           holdLuggage=holdLuggage, 
                           paymentConfirmed=paymentConfirmed)
         
         print(reservation)
         reservation.save()

         # Serialize reservation object to JSON and add primary key
         data = serializers.serialize('json', [reservation,])
         struct = json.loads(data)
         print(struct)
         data = addReservationPK(struct[0])
         print(data)
         # Return JSON response with the new reservation data
         return JsonResponse(data, status=200)
      except: 
         return JsonResponse({"message": 'Reservation could not be created.'}, status=404) 
   else:
      # Return error message if request method is not POST
      return JsonResponse({"message": "ONLY POST REQUESTS ACCEPTED."}, status=405)

# Getting reservations
@api_view(['GET'])
def get_reservation(request, reservationId):
   # check if the request is a GET request
   if request.method == "GET":
      try:
         # get the reservation object with the given id
         reservation = get_object_or_404(Reservation, pk=reservationId)
         print(reservation)
         # serialize the reservation object to JSON format
         data = serializers.serialize('json', [reservation,])
         struct = json.loads(data)

         # add the reservation's primary key to the JSON data
         data = addReservationPK(struct[0])
         print(data)
         # return the JSON response with the reservation data and a success status code
         return JsonResponse(data, status=200)
      except:
         # if the reservation could not be found, return an error response with a 404 status code
         return JsonResponse({"message":"Reservation could not be found."}, status=404)
   else:
      # if the request is not a GET request, return an error response with a 405 status code
      return JsonResponse({"message":"ONLY GET REQUESTS ACCEPTED."}, status=405)

# Update reservations
@api_view(['PUT'])
def update_reservation(request, reservationId):
   # Check if the reservation exists
   try: 
      reservation = Reservation.objects.get(pk=reservationId)
      print(reservation)
   except Reservation.DoesNotExist:
      # Return 404 if reservation not found
      return JsonResponse({"message":"Reservation not found"}, status=404)
  
   if request.method == "PUT":
      try:
         # Parse the request body as JSON
         body = json.loads(request.body)
         print(body)
         # Update the reservation with the new data
         reservation.seatId = Seat.objects.get(pk=body['seatId'])
         reservation.passengerId = Passenger.objects.get(pk=body['passengerId'])
         reservation.holdLuggage = body['holdLuggage']
         reservation.paymentConfirmed = body['paymentConfirmed']
         reservation.save()

         # Serialize the updated reservation data
         data = serializers.serialize('json', [reservation,])
         struct = json.loads(data)

         # add the reservation's primary key to the JSON data
         data = addReservationPK(struct[0])
         # return the JSON response with the updated reservation data and a success status code
         return JsonResponse(data, status=200)
      except Seat.DoesNotExist:
         # Return 404 if the seat ID in the request body is not found
         return JsonResponse({"message":"Seat not found"}, status=404)
      except Passenger.DoesNotExist:
         # Return 404 if the passenger ID in the request body is not found
         return JsonResponse({"message":"Passenger not found"}, status=404)
      except KeyError:
         # Return 400 if the request body is missing any required fields
         return JsonResponse({"message":"Invalid Request body"}, status=400)
      except ValidationError as e:
         # Return 405 if the request body contains invalid data
         return JsonResponse(e.message, status=405)
    
# Delete reservation
@api_view(['DELETE'])
def delete_reservation(request, reservationId):
  # Check if the request method is DELETE
   if request.method == "DELETE":
      try:
         # Try to get the Reservation object with the given ID
         #reservation = get_object_or_404(Reservation, pk=reservationId)
         reservation = Reservation.objects.get(pk=reservationId)
         print(reservation)
         # If the object is found, delete it from the database
         reservation.delete()
         # Return a success message with HTTP status code 200
         return JsonResponse({"message":"Reservation successfully deleted."}, status=200)
      except Reservation.DoesNotExist:
         # If the Reservation object is not found, return a 404 error message
         return JsonResponse({"message":"Reservation not found."}, status=404)
   else:
      # If the request method is not DELETE, return a 405 error message
      return JsonResponse({"message":"ONLY DELETE REQUESTS ACCEPTED."}, status=405)
  
# Confirm the payment 
@api_view(['PUT'])
def confirm_reservation(request, reservationId):
   # Check that the request method is PUT
   if request.method == "PUT":
      # Get the Reservation object with the provided reservationId or return a 404 response
      reservation = get_object_or_404(Reservation, pk=reservationId)
      # Set the paymentConfirmed field of the Reservation object to True
      reservation.paymentConfirmed = True
      # Save the reservation
      reservation.save()
      # Return a 200 response
      return HttpResponse("Reservation confirmed", status=200)
   else:
      # Return a 405 response if the request method is not PUT
      return HttpResponse("ONLY PUT REQUESTS ACCEPTED.", status=405)


def addReservationPK(data):
   # Extract fields and reservation ID from the input data
   fields = data['fields']
   reservationId = data['pk']
   # Get associated objects from the database
   seat = Seat.objects.get(pk=fields['seatId'])
   passenger = Passenger.objects.get(pk=fields['passengerId'])
   flight = seat.flightId
   # Construct a response dictionary with relevant information
   response = {
      'reservationID': reservationId,
      'seatId': str(seat),
      'holdLuggage': fields['holdLuggage'],
      'paymentConfirmed': fields['paymentConfirmed'],
      'passenger': {
         'firstName': passenger.firstName,
         'lastName': passenger.lastName,
         'dateOfBirth': passenger.dateOfBirth,
         'passportNumber': passenger.passportNumber,
         'address': passenger.address,
      },
      'flight': {
         'flightId': flight.flightId,
         'planeModel': flight.planeModel,
         'departureTime': flight.departureTime.isoformat(),
         'arrivalTime': flight.arrivalTime.isoformat(),
         'departureAirport': flight.departureAirport,
         'destinationAirport': flight.destinationAirport,
      },
   }
   # Return the response dictionary
   return response

def addFlightPK(data):
   # Extract fields and reservation ID from the input data
   fields = data['fields']
   flightId = data['pk']

   # Construct a response dictionary with relevant information
   response = {
        'flightId': flightId,
        'planeModel': fields['planeModel'],
        'numberOfRows': fields['numberOfRows'],
        'seatsPerRow': fields['seatsPerRow'],
        'departureTime': fields['departureTime'],
        'arrivalTime': fields['arrivalTime'],
        'departureAirport': fields['departureAirport'],
        'destinationAirport': fields['destinationAirport'],
   }

   # Return the response dictionary
   return response