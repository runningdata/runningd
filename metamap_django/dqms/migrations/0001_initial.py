# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-02 08:20
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DqmsAck',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('result_msg', models.CharField(blank=True, max_length=5000, null=True)),
                ('ack_user', models.CharField(blank=True, max_length=300, null=True)),
                ('ctime', models.DateTimeField(default=django.utils.timezone.now)),
                ('utime', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'db_table': 'willdqms_ack',
            },
        ),
        migrations.CreateModel(
            name='DqmsCase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('case_name', models.CharField(blank=True, max_length=300, null=True)),
                ('creator', models.CharField(blank=True, max_length=300, null=True)),
                ('editor', models.CharField(blank=True, max_length=300, null=True)),
                ('query', models.CharField(blank=True, max_length=3000, null=True)),
                ('status', models.IntegerField(blank=True, null=True)),
                ('param', models.CharField(blank=True, max_length=300, null=True)),
                ('ctime', models.DateTimeField(default=django.utils.timezone.now)),
                ('utime', models.DateTimeField(default=django.utils.timezone.now)),
                ('remark', models.CharField(blank=True, max_length=300, null=True)),
            ],
            options={
                'db_table': 'willdqms_case',
            },
        ),
        migrations.CreateModel(
            name='DqmsCaseInst',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('result_code', models.IntegerField(blank=True, null=True)),
                ('result_mes', models.CharField(blank=True, max_length=1000, null=True)),
                ('is_schedule', models.IntegerField(blank=True, null=True)),
                ('is_ack', models.IntegerField(blank=True, null=True)),
                ('ack_count', models.IntegerField(blank=True, null=True)),
                ('start_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('end_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('case', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dqms.DqmsCase')),
            ],
            options={
                'db_table': 'willdqms_case_inst',
            },
        ),
        migrations.CreateModel(
            name='DqmsCheck',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chk_name', models.CharField(blank=True, max_length=300, null=True)),
                ('creator', models.CharField(blank=True, max_length=300, null=True)),
                ('editor', models.CharField(blank=True, max_length=300, null=True)),
                ('ctime', models.DateTimeField(default=django.utils.timezone.now)),
                ('utime', models.DateTimeField(default=django.utils.timezone.now)),
                ('remark', models.CharField(blank=True, max_length=300, null=True)),
            ],
            options={
                'db_table': 'willdqms_check',
            },
        ),
        migrations.CreateModel(
            name='DqmsCheckCase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ctime', models.DateTimeField(default=django.utils.timezone.now)),
                ('utime', models.DateTimeField(default=django.utils.timezone.now)),
                ('case', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dqms.DqmsCase')),
                ('chk', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dqms.DqmsCheck')),
            ],
            options={
                'db_table': 'willdqms_check_case',
            },
        ),
        migrations.CreateModel(
            name='DqmsCheckInst',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('case_num', models.IntegerField(blank=True, null=True)),
                ('case_finish_num', models.IntegerField(blank=True, null=True)),
                ('result_code', models.IntegerField(blank=True, null=True)),
                ('result_mes', models.CharField(blank=True, max_length=300, null=True)),
                ('is_schedule', models.IntegerField(blank=True, null=True)),
                ('start_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('end_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('chk', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dqms.DqmsCheck')),
            ],
            options={
                'db_table': 'willdqms_check_inst',
            },
        ),
        migrations.CreateModel(
            name='DqmsDatasource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('src_name', models.CharField(blank=True, max_length=300, null=True)),
                ('src_type', models.CharField(blank=True, max_length=300, null=True)),
                ('src_desc', models.CharField(blank=True, max_length=300, null=True)),
                ('ctime', models.DateTimeField(default=django.utils.timezone.now)),
                ('utime', models.DateTimeField(default=django.utils.timezone.now)),
                ('valid', models.IntegerField(default=1)),
            ],
            options={
                'db_table': 'willdqms_datasource',
            },
        ),
        migrations.CreateModel(
            name='DqmsIndex',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('idx_name', models.CharField(blank=True, max_length=300, null=True)),
                ('data_type', models.CharField(blank=True, max_length=300, null=True)),
                ('col_name', models.CharField(blank=True, max_length=300, null=True)),
                ('ctime', models.DateTimeField(default=django.utils.timezone.now)),
                ('utime', models.DateTimeField(default=django.utils.timezone.now)),
                ('remark', models.CharField(blank=True, max_length=300, null=True)),
                ('case', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dqms.DqmsCase')),
            ],
            options={
                'db_table': 'willdqms_index',
            },
        ),
        migrations.CreateModel(
            name='DqmsIndexInst',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('result_code', models.IntegerField(blank=True, null=True)),
                ('result_mes', models.CharField(blank=True, max_length=1000, null=True)),
                ('start_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('end_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('case', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dqms.DqmsCase')),
                ('chkinst', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dqms.DqmsCheckInst')),
                ('index', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dqms.DqmsIndex')),
            ],
            options={
                'db_table': 'willdqms_index_inst',
            },
        ),
        migrations.CreateModel(
            name='DqmsRule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rule_type', models.IntegerField(blank=True, null=True)),
                ('rule_desc', models.CharField(blank=True, max_length=300, null=True)),
                ('measure_src', models.CharField(blank=True, max_length=300, null=True)),
                ('measure_desc', models.CharField(blank=True, max_length=300, null=True)),
                ('measure_param', models.CharField(blank=True, max_length=300, null=True)),
                ('rule_predicate', models.CharField(blank=True, max_length=300, null=True)),
                ('ctime', models.DateTimeField(default=django.utils.timezone.now)),
                ('utime', models.DateTimeField(default=django.utils.timezone.now)),
                ('remark', models.CharField(blank=True, max_length=300, null=True)),
                ('case', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dqms.DqmsCase')),
            ],
            options={
                'db_table': 'willdqms_rule',
            },
        ),
        migrations.CreateModel(
            name='DqmsRuleInst',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('result_code', models.IntegerField(blank=True, null=True)),
                ('result_mes', models.CharField(blank=True, max_length=1000, null=True)),
                ('start_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('end_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('rule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dqms.DqmsRule')),
            ],
            options={
                'db_table': 'willdqms_rule_inst',
            },
        ),
        migrations.CreateModel(
            name='DqmsView',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('viewer', models.CharField(blank=True, max_length=300, null=True)),
                ('ctime', models.DateTimeField(default=django.utils.timezone.now)),
                ('utime', models.DateTimeField(default=django.utils.timezone.now)),
                ('chk', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dqms.DqmsCheck')),
            ],
            options={
                'db_table': 'willdqms_view',
            },
        ),
        migrations.AddField(
            model_name='dqmscase',
            name='datasrc',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dqms.DqmsDatasource'),
        ),
        migrations.AddField(
            model_name='dqmsack',
            name='caseins',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dqms.DqmsCaseInst'),
        ),
        migrations.AlterUniqueTogether(
            name='dqmscheckcase',
            unique_together=set([('chk', 'case')]),
        ),
    ]
