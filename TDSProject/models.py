from enum import unique
from unittest.util import _MAX_LENGTH
from django.db import models

# This DB1 is the table name for one database from which the data is being collected 

class DB1(models.Model):
    DB_ID = models.IntegerField(primary_key=True)
    Paper_Title = models.CharField(max_length = 100)
    
    class Meta:
        db_table = "TDSProjectDB1"   


class Q(models.Model):
    # DName = models.CharField(max_length = 50)
    # PId = models.CharField(max_length = 100,primary_key=True)
    # PTitle = models.CharField(max_length = 500)
    # PAuthors = models.CharField(max_length = 500)
    # PLinks = models.CharField(max_length = 1000)

    PmId = models.CharField(max_length = 50, primary_key=True)
    Title = models.CharField(max_length = 50000, null = True)
    Abstract = models.CharField(max_length = 5000000, null = True)
    Author = models.CharField(max_length = 5000, null = True)
    Links = models.CharField(max_length = 10000,null = True)

    f1 = models.BooleanField()
    f2 = models.BooleanField()
    # f3 = models.BooleanField()
    # f4 = models.BooleanField()

    class Meta:
        db_table = "TDSProjectQ"   


class operators(models.Model):
    SNo = models.AutoField(primary_key=True)
    keyword = models.CharField(max_length = 200)
    operators = models.CharField(max_length=3, null=True)

    class Meta:
        db_table = "TDSProjectoperators"
        
class finalqquery(models.Model):
    SNo = models.AutoField(primary_key=True)
    keyword = models.CharField(max_length = 20000)
    operators = models.CharField(max_length=3, null=True)

    class Meta:
        db_table = "TDSProjectfinalqquery"

