from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vacantes', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vacante',
            name='creado_por',
            field=models.ForeignKey(
                db_column='creado_por',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='vacantes_creadas',
                to='usuarios.usuario',
            ),
        ),
    ]
