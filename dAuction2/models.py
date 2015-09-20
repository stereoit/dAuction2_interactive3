#!python3
__author__ = 'DP2'
from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

import random
# </standard imports>
from random import randint
import random

class Constants:
    name_in_url = 'asset_market'
    players_per_group = 2
    num_rounds = 2
    understanding_1_correct = 'P=2.5, N=2'
    understanding_2_correct = '$8, $12'
    endowment = 20
    num_shares = 10
    init_started=False
    show_theory=False
    stop=False
    setOffer_started=False
    script2={}
    div2={}
    sd_price_max=-1
    sd_price_min=-2
    sd_units=-3
    my_profit_th=-4
    my_cost_th =-5
    my_score=-6
    PR_number=3
    RE_number=3
    baseurl="http://192.168.23.1:8000/"

    def __str__(self):  #For Python 2, use __str__ on Python 3
        return self.name

class Constants2(models.Model):
    init_started= models.BooleanField(default=False)
    setOffer_started= models.BooleanField(default=False)


    def __str__(self):  #For Python 2, use __str__ on Python 3
        return str(self.id)


class Group(models.Model):
    name = models.CharField(max_length=128, default="name")
    group_id= models.IntegerField(default=0)
    def __str__(self):  #For Python 2, use __str__ on Python 3
        return str(self.group_id) #why MUST it be a string???

class SD(models.Model):
    price_max=models.IntegerField(default=-1)
    price_min=models.IntegerField(default=-1)
    units=models.IntegerField(default=-1)
    def __str__(self):  #For Python 2, use __str__ on Python 3
        return str(self.group_id) #why MUST it be a string???


class Player(models.Model):
    group = models.ForeignKey(Group)
    id_in_group= models.IntegerField(default=0)
    codename = models.CharField(max_length=10)
    codeurl = models.URLField(max_length=200)
    role = models.CharField(max_length=4, default="PR") # two roles: PRoducer and REtailer
    name = models.CharField(max_length=5, default="cost") # two names: Cost and Value
    money = models.IntegerField(default=0)
    trading_result = models.IntegerField(default=0)
    total_cost = models.IntegerField(default=0)
    total_values = models.IntegerField(default=0)
    profit = models.IntegerField(default=0)
    def __str__(self):  #For Python 2, use __str__ on Python 3
        return str(self.id_in_group)

class Voucher(models.Model):
    num_vouchers=35
    idd = models.IntegerField(default=0)
    player = models.ForeignKey(Player)
    group = models.ForeignKey(Group)
    role = models.CharField(max_length=2, default="PR") # two roles: PRoducer and REtailer
    value = models.IntegerField(default=0)
    value_cum = models.IntegerField(default=0)
    price = models.IntegerField(default=-1)
    profit = models.IntegerField(default=-999999)
    used = models.BooleanField(default=False)
    offered = models.BooleanField(default=False)

    def __str__(self):  #For Python 2, use __str__ on Python 3
        return str(self.id)

class Offer(models.Model):
    player = models.ForeignKey(Player)
    counterOffer_id = models.IntegerField(default=-11)  # the id of the parent offer
    group = models.ForeignKey(Group)
    type = models.CharField(max_length=28,default="SELL")
    offered = models.BooleanField(default=False)
    canceled = models.BooleanField(default=False)
    cleared = models.BooleanField(default=False)
    updated = models.BooleanField(default=False)
    #name = models.CharField(max_length=128)
    priceLimit = models.IntegerField(default=-5)

    parentId= models.IntegerField(default=-11)  # the id of the parent offer
    unitsAvailable = models.IntegerField(default=-1)  # the number of units that are still available (0 after clearing)
    unitsCleared = models.IntegerField(default=-2)    # the number of units that have been traded in the offer
    unitsOriginal = models.IntegerField(default=-3)   # the number of units in the original offer
    unitsInherited = models.IntegerField(default=-4)   # the number of units inherited
    priceCleared = models.IntegerField(default=-5)   # the price for the offer has been traded
    priceOriginal = models.IntegerField(default=-6)  # the price in the original offer
    timeCreated = models.DateTimeField(default=timezone.now)
    product = models.IntegerField(default=0)
    def __str__(self):  #For Python 2, use __str__ on Python 3
        return str(self.id)
    def getnumber(self):
        return self.id
    #def lastOne(self):  #For Python 2, use __str__ on Python 3
    #    lista = self.objects.all()
    #    return lista.count()

    class Meta:
        app_label = 'dAuction2'
        ordering=["id"]
        get_latest_by = 'id'

class Transaction(models.Model):
    group = models.ForeignKey('Group', related_name='group',null=True)
    sellerOffer = models.ForeignKey('Offer', related_name='sellerOffer',null=True)
    buyerOffer = models.ForeignKey('Offer', related_name='buyerOffer',null=True)
    price = models.IntegerField(default=0)
    buyerPrice= models.IntegerField(default=0)
    sellerPrice= models.IntegerField(default=0)
    units = models.IntegerField(default=0)
    name = models.CharField(max_length=128)
    timeCreated = models.DateTimeField(default=timezone.now)
    def __str__(self):  #For Python 2, use __str__ on Python 3
        return str(self.id)
    def getnumber(self):
        return self.id
    #def lastOne(self):  #For Python 2, use __str__ on Python 3
    #    lista = self.objects.all()
    #    return lista.count()

    class Meta:
        app_label = 'dAuction2'
        ordering=["id"]
        get_latest_by = 'id'


