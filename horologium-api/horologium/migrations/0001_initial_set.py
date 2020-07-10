# Generated by Django 3.0.7 on 2020-07-04 00:48

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import sanitizer.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Timer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', sanitizer.models.SanitizedCharField(blank=True, max_length=64)),
                ('description', sanitizer.models.SanitizedCharField(blank=True, max_length=4096)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('note', sanitizer.models.SanitizedCharField(max_length=4096, validators=[django.core.validators.MinLengthValidator(1, message='Field must not be empty')])),
                ('stamp', models.DateTimeField(auto_now_add=True)),
                ('writer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Duration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.DateTimeField(blank=True, null=True)),
                ('end', models.DateTimeField(blank=True, null=True)),
                ('timer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='durations', to='horologium.Timer')),
            ],
        ),
        migrations.CreateModel(
            name='Countdown',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count', models.IntegerField(blank=True, null=True)),
                ('notice', sanitizer.models.SanitizedCharField(blank=True, max_length=1024, null=True)),
                ('timer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='countdowns', to='horologium.Timer')),
            ],
            options={
                'unique_together': {('count', 'timer')},
            },
        ),
    ]
