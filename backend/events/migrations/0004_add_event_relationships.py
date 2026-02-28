# Generated migration to add organiser and interested_users fields back to Event model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0003_remove_event_interested_users_remove_event_organiser'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='organiser',
            field=models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='organised_events', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='event',
            name='interested_users',
            field=models.ManyToManyField(blank=True, related_name='interested_events', to=settings.AUTH_USER_MODEL),
        ),
    ]
