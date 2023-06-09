# Generated by Django 4.1.7 on 2023-05-05 10:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Flight',
            fields=[
                ('flight_id', models.AutoField(editable=False, primary_key=True, serialize=False)),
                ('plane_model', models.CharField(max_length=255)),
                ('number_of_rows', models.IntegerField()),
                ('seats_per_row', models.IntegerField()),
                ('departure_time', models.DateTimeField()),
                ('arrival_time', models.DateTimeField()),
                ('destination', models.CharField(max_length=255)),
                ('origin', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Passenger',
            fields=[
                ('passenger_id', models.AutoField(editable=False, primary_key=True, serialize=False)),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('DOB', models.DateField()),
                ('passport_number', models.IntegerField()),
                ('address', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Seat',
            fields=[
                ('seat_id', models.AutoField(editable=False, primary_key=True, serialize=False)),
                ('seat_number', models.IntegerField()),
                ('seat_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('flight_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='flights.flight')),
            ],
        ),
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('reservation_id', models.AutoField(editable=False, primary_key=True, serialize=False)),
                ('hold_luggage', models.BooleanField()),
                ('payment_confirmed', models.BooleanField()),
                ('passenger_id', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='flights.passenger')),
                ('seat_id', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='flights.seat')),
            ],
        ),
    ]
