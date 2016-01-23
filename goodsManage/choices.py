# max_length = 4
DEPARTMENT_CHOICES = {
    ('01', '一部'),
    ('02', '二部'),
    ('03', '三部'),
    ('04', '四部'),
    ('05', '五部'),
    ('06', '六部'),
    ('99', '外單位'),
}

DEPARTMENT_CHOICES_SORTED = sorted(DEPARTMENT_CHOICES, key=lambda x: x[0])
DEPARTMENT_CHOICES_SORTED_ADD_ALL = DEPARTMENT_CHOICES_SORTED + [('All','All')]

# max_length = 10
KIND_CHOICES = (
    ('01', '治具'),
    ('02', '線材'),
)

# max_length = 10
WASTAGE_STATUS_CHOICES = (
    ('01', '報廢'),
    ('02', '遺失'),
)