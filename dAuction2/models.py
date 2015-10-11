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


#???IDU= I Don't Understand - perhaps you can clarify.

class Constants:
# I need some variables and I thought using a class like this is the easiest way
# ???IDU: this class does not inherit from models.Model. Is that good or bad?
# I let Constants2 inherit from models.Model for no specific reason

# Variables not used(yet)
    name_in_url = 'asset_market'
    players_per_group = 2
    num_rounds = 2
    endowment = 20
    num_shares = 10

# Variables used
    init_started=False  # To avoid a double start
    show_theory=False   # Can show or hide the theoretical prediction
    stop=False          # Can stop the programmed agents - not relevant for this version
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
    baseurl="http://quadro:8000/"
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
# A player is one of the subjects. (S)he is a member of a group and has an id in the group.
# the player has also a codename, and this how the player can get his screen by putting
# http://correct-url-/codename into the browser
    group = models.ForeignKey(Group)
    id_in_group= models.IntegerField(default=0)
    codename = models.CharField(max_length=10)
    codeurl = models.URLField(max_length=200)
    role = models.CharField(max_length=4, default="PR") # two roles: PRoducer and REtailer
    name = models.CharField(max_length=5, default="cost")
        # two names: "cost" and "value"- used to print "cost" on the page for producers and
        # "value" for retailers
    money = models.IntegerField(default=0)
        # the money that a player has
    trading_result = models.IntegerField(default=0)
        # the money earned by a player if the player (is positive if selling, negative if buying)
    total_cost = models.IntegerField(default=0)
        # the costs of production for a producer
    total_values = models.IntegerField(default=0)
        # the total of the values of the units a retailer purchased
    profit = models.IntegerField(default=0)
        # net earnings of a player
    def __str__(self):  #For Python 2, use __str__ on Python 3
        return str(self.id_in_group)

class Voucher(models.Model):
        # a "voucher" is a unit of the good that is held by players in their stock
        # Producers may produce units against incurring a cost. Vouchers is for producers the object that
        # gives the details of the number of units that can be produced by a producer and against what costs.
        # Retailers earn money by buying units - it can be thought of that producers again sell the units
        # Vouchers is for Retailers the object that gives the details on the number of units that Retailers
        # can purchase and how much earnings this brings
    num_vouchers=35
        # number of vouchers - may be larger, eg 50? MUST BE SET AS IS USED IN SOME CALCULATIONS
    idd = models.IntegerField(default=0)
        # to be able to number them from 1 till 35
    player = models.ForeignKey(Player)
        # vouchers are owned by players
    group = models.ForeignKey(Group)
        # players are part of groups, so maybe we dont need group in here ?
    role = models.CharField(max_length=2, default="PR")
        # two roles: "PR"=PRoducer and "RE"=REtailer
    value = models.IntegerField(default=0)
        # For a retailer, the value is the money the retailer earns for purchasing the unit.
        # For a producer, the value is the cost of producing that the producer
        # must pay if the producer sells this unit.
    value_cum = models.IntegerField(default=0)
        # Gives the cummulative value of all values
    price = models.IntegerField(default=-1)
        # price for which a unit has been sold or purchased
    profit = models.IntegerField(default=-999999)
        # profit on the purchase (=value - price) or sale (=price - value) of the unit
    used = models.BooleanField(default=False)
        # True if the unit has been used (unit can be used only once)
    offered = models.BooleanField(default=False)
        # is the unit included in one of the offers on the market?

    def __str__(self):  #For Python 2, use __str__ on Python 3
        return str(self.id)

class Offer(models.Model):
        # An offer is a triple of price, number of units, and indication if you want to buy or sell
        # An offer can be original as given by a player
        # However, an offer may only be partly matched (eg, I offer 2 units for 10, and there is a buyer who
        # only wants 1 unit. The offer is than split into two parts, the original one, and a new one that
        # is marked as "updated". The original one is matched (made into a transaction) and deleted (cleared),
        # the new, "updated" offer lives on until it is matched, cancelled or the game ends.
    player = models.ForeignKey(Player)
        # offers are owned by the players
    counterOffer_id = models.IntegerField(default=-11)
        # the counteroffer only exists if the offer has been matched and cleared. In that case the
        # counteroffer is the offer with which an offer has been matched
    group = models.ForeignKey(Group)
        # Should group also be an owner of offer???
    type = models.CharField(max_length=28,default="SELL")
         # indication if you want to buy or sell
    offered = models.BooleanField(default=False)
        # true if the offer is on the market at the moment
    canceled = models.BooleanField(default=False)
        # true if the offer was cancelled by the player
    cleared = models.BooleanField(default=False)
        # true if the offer was matched with a counteroffer and cleared
    updated = models.BooleanField(default=False)
        # true if the offer is the "descendant"of an offer (the "parent" offer)that was only partially matched and cleared
    priceLimit = models.IntegerField(default=-5)
        # pricelimit??? What is this? Do we need this?
    parentId= models.IntegerField(default=-11)
        # the id of the parent offer
    unitsAvailable = models.IntegerField(default=-1)
        # the number of units that are still available (0 after clearing)
    unitsCleared = models.IntegerField(default=-2)
        # the number of units that have been traded in the offer
    unitsOriginal = models.IntegerField(default=-3)
        # the number of units in the original offer
    unitsInherited = models.IntegerField(default=-4)
        # the number of units inherited from the direct parent offer
    priceCleared = models.IntegerField(default=-5)
        # the price for the offer has been traded (can be different from priceOriginal
    priceOriginal = models.IntegerField(default=-6)
        # the price in the original offer
    timeCreated = models.DateTimeField(default=timezone.now)
        # time the offer was created
    product = models.IntegerField(default=0)
        # not sure what this is: unitsCleared times priceCleared perhaps???
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
        # when an offer is cleared, a transaction is created. This is the registration of a trade between
        # a seller and a buyer
    group = models.ForeignKey('Group', related_name='group',null=True)
    sellerOffer = models.ForeignKey('Offer', related_name='sellerOffer',null=True)
        # shows what the seller offered (doesnt need to be the same as the price
    buyerOffer = models.ForeignKey('Offer', related_name='buyerOffer',null=True)
        # shows what the buyer offered (doesnt need to be the same as the price
    price = models.IntegerField(default=0)
        # the price for which the units are traded, is either equal to sellerOffer or to buyerOffer
    buyerPrice= models.IntegerField(default=0)
        # not sure???
    sellerPrice= models.IntegerField(default=0)
        # not sure???
    units = models.IntegerField(default=0)
        # the number of units in the transaction
    name = models.CharField(max_length=128)
        # notsure, what do I need a name for???
    timeCreated = models.DateTimeField(default=timezone.now)
        # time the transaction was created
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


