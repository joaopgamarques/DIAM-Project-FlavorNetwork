# Generated by Django 5.0.4 on 2024-04-26 15:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0002_alter_recipe_images'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='images',
            field=models.ImageField(blank=True, null=True, upload_to='recipes/%Y/%m/%d/'),
        ),
    ]
