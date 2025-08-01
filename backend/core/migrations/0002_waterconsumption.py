# Generated by Django 5.1.6 on 2025-06-09 15:13

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='WaterConsumption',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('consumption', models.FloatField(help_text='Water consumption in liters')),
                ('period', models.CharField(choices=[('total', 'Total'), ('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly'), ('minute', 'Minute')], help_text='Time period of consumption (total, daily, weekly, monthly, minute)', max_length=20)),
                ('timestamp', models.DateTimeField(auto_now_add=True, help_text='Time the reading was recorded')),
                ('sensor_id', models.CharField(help_text="Unique identifier for the sensor (e.g., 'main_flow_sensor')", max_length=50)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='water_consumption_records', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-timestamp'],
                'indexes': [models.Index(fields=['user', 'period', 'timestamp'], name='core_waterc_user_id_af3a4a_idx'), models.Index(fields=['sensor_id'], name='core_waterc_sensor__47c9b3_idx')],
            },
        ),
    ]
