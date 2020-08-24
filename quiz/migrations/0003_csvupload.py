# Generated by Django 2.0.1 on 2018-07-27 19:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import quiz.models
import quiz.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('quiz', '0002_auto_20180728_0028'),
    ]

    operations = [
        migrations.CreateModel(
            name='CSVUpload',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to=quiz.models.upload_csv_file, validators=[quiz.validators.csv_file_validator])),
                ('completed', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
