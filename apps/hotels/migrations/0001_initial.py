# Generated by Django 5.0.2 on 2024-04-03 13:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('destinations', '0001_initial'),
        ('guests', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AmenityCategory',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('icon', models.ImageField(null=True, upload_to='hotels/')),
            ],
            options={
                'db_table': 'amenity_categories',
            },
        ),
        migrations.CreateModel(
            name='BedType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('icon', models.ImageField(null=True, upload_to='hotels/')),
            ],
            options={
                'db_table': 'bed_types',
            },
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('code', models.IntegerField()),
                ('description', models.CharField(max_length=255, null=True)),
                ('number_of_guests', models.PositiveIntegerField()),
            ],
            options={
                'db_table': 'rooms',
            },
        ),
        migrations.CreateModel(
            name='Amenity',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('icon', models.ImageField(null=True, upload_to='hotels/')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='amenities', to='hotels.amenitycategory')),
            ],
            options={
                'db_table': 'amenities',
            },
        ),
        migrations.CreateModel(
            name='Hotel',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('stars', models.IntegerField()),
                ('address', models.CharField(max_length=255)),
                ('longitude', models.FloatField(null=True)),
                ('latitude', models.FloatField(null=True)),
                ('website_url', models.URLField(null=True)),
                ('cover_img', models.ImageField(null=True, upload_to='hotels/')),
                ('about', models.TextField(null=True)),
                ('business_email', models.EmailField(max_length=254, null=True)),
                ('contact_number', models.CharField(max_length=20)),
                ('amenities', models.ManyToManyField(db_table='hotel_amenities', to='hotels.amenity')),
                ('city', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='hotels', to='destinations.city')),
            ],
            options={
                'db_table': 'hotels',
            },
        ),
        migrations.CreateModel(
            name='HotelImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('img', models.ImageField(null=True, upload_to='hotels/')),
                ('hotel', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='images', to='hotels.hotel')),
            ],
            options={
                'db_table': 'hotel_images',
            },
        ),
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('first_name', models.CharField(max_length=255, null=True)),
                ('last_name', models.CharField(max_length=255, null=True)),
                ('email', models.EmailField(max_length=254, null=True)),
                ('check_in', models.DateTimeField()),
                ('check_out', models.DateTimeField()),
                ('total_price', models.BigIntegerField()),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Accepted', 'Accepted'), ('Refused', 'Refused'), ('Cancelled_By_Owner', 'Cancelled By Owner'), ('Cancelled_By_Guest', 'Cancelled By Guest'), ('Completed', 'Completed'), ('Deleted_By_Admin', 'Deleted By Admin')], default='Accepted', max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('guest', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reservations', to='guests.guest')),
                ('hotel', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reservations', to='hotels.hotel')),
            ],
            options={
                'db_table': 'reservations',
            },
        ),
        migrations.CreateModel(
            name='GuestReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.PositiveIntegerField()),
                ('title', models.CharField(max_length=255)),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('reservation', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='review', to='hotels.reservation')),
            ],
            options={
                'db_table': 'guest_reviews',
            },
        ),
        migrations.CreateModel(
            name='ReservedRoomType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nb_rooms', models.PositiveIntegerField()),
                ('reservation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reserved_room_types', to='hotels.reservation')),
            ],
            options={
                'db_table': 'reserved_room_types',
            },
        ),
        migrations.CreateModel(
            name='RoomAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reserved_room_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assigned_rooms', to='hotels.reservedroomtype')),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignments', to='hotels.room')),
            ],
            options={
                'db_table': 'room_assignments',
            },
        ),
        migrations.CreateModel(
            name='RoomType',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('size', models.FloatField()),
                ('nb_beds', models.PositiveIntegerField()),
                ('price_per_night', models.BigIntegerField()),
                ('cover_img', models.ImageField(null=True, upload_to='hotels/')),
                ('amenities', models.ManyToManyField(db_table='room_type_amenities', to='hotels.amenity')),
                ('hotel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='room_types', to='hotels.hotel')),
                ('main_bed_type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='hotels.bedtype')),
            ],
            options={
                'db_table': 'room_types',
            },
        ),
        migrations.AddField(
            model_name='room',
            name='room_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rooms', to='hotels.roomtype'),
        ),
        migrations.AddField(
            model_name='reservedroomtype',
            name='room_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hotels.roomtype'),
        ),
        migrations.CreateModel(
            name='RoomTypePolicy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('free_cancellation_days', models.IntegerField()),
                ('breakfast_included', models.BooleanField()),
                ('prepayment_required', models.BooleanField()),
                ('room_type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='policy', to='hotels.roomtype')),
            ],
            options={
                'db_table': 'room_type_policy',
            },
        ),
        migrations.AddIndex(
            model_name='hotel',
            index=models.Index(fields=['name'], name='idx_name'),
        ),
        migrations.AddIndex(
            model_name='hotel',
            index=models.Index(fields=['address'], name='idx_address'),
        ),
        migrations.AddIndex(
            model_name='hotel',
            index=models.Index(fields=['latitude', 'longitude'], name='idx_location'),
        ),
        migrations.AddConstraint(
            model_name='reservation',
            constraint=models.CheckConstraint(check=models.Q(('status__in', ['Pending', 'Accepted', 'Refused', 'Cancelled_By_Owner', 'Cancelled_By_Guest', 'Completed', 'Deleted_By_Admin'])), name='chk_status'),
        ),
        migrations.AddIndex(
            model_name='guestreview',
            index=models.Index(fields=['rating'], name='idx_rating'),
        ),
        migrations.AddIndex(
            model_name='guestreview',
            index=models.Index(fields=['created_at'], name='idx_created_at'),
        ),
    ]
