from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField(blank=True, null=True)),
                ('location', models.CharField(blank=True, max_length=255)),
                ('cover_image', models.URLField(blank=True, max_length=1000, null=True)),
                ('organizer_object_id', models.PositiveIntegerField()),
                ('created_by_role', models.CharField(choices=[('mentor', 'Mentor'), ('admin', 'Admin')], max_length=10)),
                ('is_published', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('organizer_content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
            ],
            options={
                'ordering': ['start_time'],
            },
        ),
        migrations.AddIndex(
            model_name='event',
            index=models.Index(fields=['start_time'], name='events_even_start_t_6c54f5_idx'),
        ),
        migrations.AddIndex(
            model_name='event',
            index=models.Index(fields=['is_published'], name='events_even_is_publ_5f8db8_idx'),
        ),
    ] 