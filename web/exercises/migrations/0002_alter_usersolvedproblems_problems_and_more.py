# Generated by Django 4.2 on 2023-05-22 13:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exercises', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usersolvedproblems',
            name='problems',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='usersolvedproblems',
            name='solved',
            field=models.IntegerField(),
        ),
    ]
