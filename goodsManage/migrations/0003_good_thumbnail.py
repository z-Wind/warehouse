# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goodsManage', '0002_goodrepair'),
    ]

    operations = [
        migrations.AddField(
            model_name='good',
            name='thumbnail',
            field=models.ImageField(verbose_name='縮圖', null=True, upload_to='goods', blank=True),
        ),
    ]
