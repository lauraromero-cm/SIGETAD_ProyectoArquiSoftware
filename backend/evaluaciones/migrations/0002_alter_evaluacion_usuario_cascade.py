from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('evaluaciones', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='evaluacion',
            name='id_usuario',
            field=models.ForeignKey(
                db_column='id_usuario',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='evaluaciones',
                to='usuarios.usuario',
            ),
        ),
    ]
