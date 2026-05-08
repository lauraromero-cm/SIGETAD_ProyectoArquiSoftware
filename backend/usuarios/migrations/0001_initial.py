from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('id_usuario', models.BigAutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=100)),
                ('correo', models.EmailField(max_length=100, unique=True)),
                ('contrasena', models.CharField(max_length=255)),
                ('rol', models.CharField(choices=[('admin', 'Administrador'), ('analista', 'Analista de Selección'), ('jefe_area', 'Jefe de Área'), ('candidato', 'Candidato')], max_length=30)),
                ('estado', models.CharField(choices=[('activo', 'Activo'), ('inactivo', 'Inactivo')], default='activo', max_length=20)),
            ],
            options={'db_table': 'usuario', 'ordering': ['id_usuario']},
        ),
    ]
