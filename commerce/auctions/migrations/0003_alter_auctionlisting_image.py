# Generated by Django 4.2.5 on 2023-09-23 16:28

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("auctions", "0002_auctionlisting"),
    ]

    operations = [
        migrations.AlterField(
            model_name="auctionlisting",
            name="image",
            field=models.ImageField(blank=True, null=True, upload_to="media/"),
        ),
    ]
