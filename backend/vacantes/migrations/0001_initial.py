import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [('usuarios', '0001_initial')]
    operations = [
        migrations.CreateModel(
            name='Vacante',
            fields=[
                ('id_vacante', models.BigAutoField(primary_key=True, serialize=False)),
                ('titulo', models.CharField(max_length=100)),
                ('descripcion', models.TextField()),
                ('departamento', models.CharField(max_length=100)),
                ('salario_minimo', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('salario_maximo', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('requisitos', models.TextField(blank=True)),
                ('estado', models.CharField(choices=[('abierta', 'Abierta'), ('cerrada', 'Cerrada')], default='abierta', max_length=20)),
                ('creado_por', models.ForeignKey(db_column='creado_por', on_delete=django.db.models.deletion.PROTECT, related_name='vacantes_creadas', to='usuarios.usuario')),
            ],
            options={'db_table': 'vacante', 'ordering': ['-id_vacante']},
        ),
    ]
