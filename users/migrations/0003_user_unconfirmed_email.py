# Generated by Django 5.0.1 on 2024-02-05 08:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_user_confirmation_sent_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='unconfirmed_email',
            field=models.EmailField(max_length=254, null=True),
        ),
    ]
