from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('historial', '0002_ampliar_historial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historial',
            name='id_postulacion',
            field=models.ForeignKey(
                blank=True,
                db_column='id_postulacion',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='historial',
                to='postulaciones.postulacion',
            ),
        ),
    ]
