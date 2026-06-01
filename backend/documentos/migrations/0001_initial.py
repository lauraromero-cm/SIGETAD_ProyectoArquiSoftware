from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('postulaciones', '0001_initial'),
        ('usuarios', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Documento',
            fields=[
                ('id_documento', models.BigAutoField(primary_key=True, serialize=False)),
                ('nombre_original', models.CharField(max_length=255)),
                ('nombre_almacenado', models.CharField(max_length=255, unique=True)),
                ('ruta_relativa', models.CharField(max_length=500)),
                ('content_type', models.CharField(default='application/pdf', max_length=100)),
                ('tamanio_bytes', models.PositiveBigIntegerField()),
                ('checksum_sha256', models.CharField(max_length=64)),
                ('estado', models.CharField(choices=[('disponible', 'Disponible'), ('eliminado', 'Eliminado')], default='disponible', max_length=20)),
                ('fecha_subida', models.DateTimeField(auto_now_add=True)),
                ('id_postulacion', models.ForeignKey(blank=True, db_column='id_postulacion', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='documentos', to='postulaciones.postulacion')),
                ('id_usuario', models.ForeignKey(db_column='id_usuario', on_delete=django.db.models.deletion.PROTECT, related_name='documentos_subidos', to='usuarios.usuario')),
            ],
            options={
                'db_table': 'documento',
                'ordering': ['-fecha_subida'],
            },
        ),
        migrations.CreateModel(
            name='DocumentoAuditoria',
            fields=[
                ('id_auditoria', models.BigAutoField(primary_key=True, serialize=False)),
                ('accion', models.CharField(choices=[('subida', 'Subida'), ('url_generada', 'URL generada'), ('descarga', 'Descarga')], max_length=30)),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('detalles', models.JSONField(blank=True, default=dict)),
                ('id_documento', models.ForeignKey(db_column='id_documento', on_delete=django.db.models.deletion.CASCADE, related_name='auditoria', to='documentos.documento')),
                ('id_usuario', models.ForeignKey(db_column='id_usuario', on_delete=django.db.models.deletion.PROTECT, related_name='auditoria_documentos', to='usuarios.usuario')),
            ],
            options={
                'db_table': 'documento_auditoria',
                'ordering': ['-fecha'],
            },
        ),
        migrations.AddIndex(
            model_name='documento',
            index=models.Index(fields=['id_usuario', '-fecha_subida'], name='idx_doc_usuario_fecha'),
        ),
        migrations.AddIndex(
            model_name='documento',
            index=models.Index(fields=['id_postulacion', '-fecha_subida'], name='idx_doc_post_fecha'),
        ),
        migrations.AddIndex(
            model_name='documento',
            index=models.Index(fields=['checksum_sha256'], name='idx_doc_checksum'),
        ),
        migrations.AddIndex(
            model_name='documentoauditoria',
            index=models.Index(fields=['id_documento', '-fecha'], name='idx_doc_aud_doc_fecha'),
        ),
        migrations.AddIndex(
            model_name='documentoauditoria',
            index=models.Index(fields=['id_usuario', '-fecha'], name='idx_doc_aud_usr_fecha'),
        ),
        migrations.AddIndex(
            model_name='documentoauditoria',
            index=models.Index(fields=['accion', '-fecha'], name='idx_doc_aud_acc_fecha'),
        ),
    ]
