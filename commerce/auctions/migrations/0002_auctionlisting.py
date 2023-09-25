# Generated by Django 4.2.5 on 2023-09-23 16:00

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("auctions", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="AuctionListing",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=64)),
                ("price", models.DecimalField(decimal_places=2, max_digits=5)),
                (
                    "image",
                    models.ImageField(blank=True, null=True, upload_to="auctions/"),
                ),
                ("description", models.CharField(default="-", max_length=500)),
                ("category", models.CharField(default="-", max_length=64)),
            ],
        ),
    ]
