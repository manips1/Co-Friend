# Generated by Django 4.2 on 2023-05-22 13:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('exercises', '0002_alter_usersolvedproblems_problems_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usersolvedproblems',
            name='id',
        ),
        migrations.AlterField(
            model_name='usersolvedproblems',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL),
        ),
    ]