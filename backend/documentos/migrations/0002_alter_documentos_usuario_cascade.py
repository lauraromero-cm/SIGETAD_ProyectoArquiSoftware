from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('documentos', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documento',
            name='id_usuario',
            field=models.ForeignKey(
                db_column='id_usuario',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='documentos_subidos',
                to='usuarios.usuario',
            ),
        ),
        migrations.AlterField(
            model_name='documentoauditoria',
            name='id_usuario',
            field=models.ForeignKey(
                db_column='id_usuario',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='auditoria_documentos',
                to='usuarios.usuario',
            ),
        ),
    ]
