# Generated by Django 4.1.1 on 2022-09-20 01:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerUser',
            fields=[
                ('userid', models.CharField(db_column='userid', max_length=50, primary_key=True, serialize=False, verbose_name='userid')),
                ('passwd', models.CharField(db_column='passwd', max_length=50, verbose_name='passwd')),
                ('email', models.CharField(blank=True, db_column='email', max_length=30, verbose_name='email')),
                ('birthday', models.CharField(db_column='birth', default='19001011', max_length=10, verbose_name='birth')),
                ('phone', models.IntegerField(db_column='phone', default=None, verbose_name='phone')),
            ],
        ),
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=50, verbose_name='제목')),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='작성일')),
                ('views', models.PositiveIntegerField(default=0, verbose_name='조회')),
                ('upvote', models.PositiveIntegerField(default=0, verbose_name='추천')),
                ('writer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bangdori.customeruser', verbose_name='글쓴이')),
            ],
            options={
                'verbose_name': '게시판',
                'verbose_name_plural': '게시판',
                'db_table': 'board',
            },
        ),
    ]