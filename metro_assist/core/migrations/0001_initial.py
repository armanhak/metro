# Generated by Django 5.0.6 on 2024-06-23 17:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Gender',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='MetroStation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_station', models.CharField(max_length=255)),
                ('name_line', models.CharField(max_length=255)),
                ('id_line', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='PassengerCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=3, unique=True)),
                ('description', models.CharField(max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Rank',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='RequestMethod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('method', models.CharField(max_length=25)),
            ],
        ),
        migrations.CreateModel(
            name='RequestStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Smena',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Uchastok',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='MetroTransferTime',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.FloatField()),
                ('id1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transfer_start_station', to='core.metrostation')),
                ('id2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transfer_end_station', to='core.metrostation')),
            ],
        ),
        migrations.CreateModel(
            name='MetroTravelTime',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.FloatField()),
                ('id_st1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='start_station', to='core.metrostation')),
                ('id_st2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='end_station', to='core.metrostation')),
            ],
        ),
        migrations.CreateModel(
            name='Passenger',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('contact_phone', models.CharField(max_length=20)),
                ('additional_phone_info', models.TextField(blank=True, null=True)),
                ('additional_info', models.TextField(blank=True, null=True)),
                ('has_eks', models.BooleanField(default=False)),
                ('gender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.gender')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.passengercategory')),
            ],
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('patronymic', models.CharField(max_length=50)),
                ('initials', models.CharField(blank=True, max_length=50)),
                ('work_phone', models.CharField(max_length=20)),
                ('personal_phone', models.CharField(max_length=20)),
                ('tab_number', models.CharField(max_length=50, null=True)),
                ('light_duty', models.BooleanField(default=False)),
                ('gender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.gender')),
                ('rank', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.rank')),
            ],
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField()),
                ('tpz', models.DateTimeField(auto_now_add=True)),
                ('insp_sex_m', models.IntegerField()),
                ('insp_sex_f', models.IntegerField()),
                ('time_over', models.TimeField()),
                ('time3', models.TimeField()),
                ('time4', models.TimeField()),
                ('meeting_point', models.CharField(max_length=255)),
                ('arrival_point', models.CharField(max_length=255)),
                ('additional_info', models.TextField()),
                ('cat_pas', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.passengercategory')),
                ('id_pas', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.passenger')),
                ('id_st1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='request_start_station', to='core.metrostation')),
                ('id_st2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='request_end_station', to='core.metrostation')),
                ('method_of_request', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.requestmethod')),
                ('status', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.requeststatus')),
            ],
        ),
        migrations.CreateModel(
            name='NoShow',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_time', models.DateTimeField()),
                ('id_bid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.request')),
            ],
        ),
        migrations.CreateModel(
            name='RequestCancellation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_time', models.DateTimeField()),
                ('id_bid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.request')),
            ],
        ),
        migrations.CreateModel(
            name='RequestReschedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_edit', models.DateTimeField()),
                ('time_s', models.DateTimeField()),
                ('time_f', models.DateTimeField()),
                ('id_bid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.request')),
            ],
        ),
        migrations.CreateModel(
            name='EmployeeSchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_work_date', models.DateField()),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.employee')),
                ('smena', models.ForeignKey(on_delete=models.SET('-'), to='core.smena')),
            ],
        ),
        migrations.CreateModel(
            name='TimeMatrix',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.FloatField()),
                ('id1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='request_start', to='core.request')),
                ('id2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='request_end', to='core.request')),
            ],
        ),
        migrations.CreateModel(
            name='WorkTime',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('uchastok', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='work_times', to='core.uchastok')),
            ],
        ),
        migrations.AddField(
            model_name='employee',
            name='work_time',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.worktime'),
        ),
    ]
