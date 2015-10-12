#!python3
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from dAuction2.models import Player, Group, Offer, Transaction, Voucher,Constants,Constants2, SD
import random
#import numpy as np
##import matplotlib.pyplot as plt
from django.shortcuts import render
#import pylab
#import io
from functools import reduce
from django.contrib import messages
from django.template import RequestContext, loader
from bokeh.plotting import figure, output_file, show
#from bokeh.resources import CDN
from bokeh.embed import components
import time
from django.db.models import Avg,Sum
from dAuction2.functions import *
from dAuction2.functions_mature import *
import random, string


def initialize(request):
    # DEM
    # create the players a total of producers equal to #Constants.PR_number and a total of retailers equal to
    # #Constants.RE_number


    #create codes for the other players
    #Constants.PR_number, Constants.RE_number
    #group_id, id_in_group=decode(codename)

    if not Constants.init_started:
    #if True:
        Constants.init_started=True # to assure the process is started only once
        print ("Constants.init_started",Constants.init_started)
        Voucher.objects.all().delete()
        Transaction.objects.all().delete()
        Offer.objects.all().delete()
        Player.objects.all().delete()
        Group.objects.all().delete()
        group_id=int(1)
            # everything is deleted to clean up
        g=getGroup(group_id)
        for i in range(1,Constants.PR_number+1):
            #random.seed(i)
            createPlayer(g,i,"PR") # 5 producers, with index i={1,2}
        for i in range(Constants.PR_number+1,Constants.PR_number+Constants.RE_number+1):
            #random.seed(i)
            createPlayer(g,i,"RE") # 2 retailers, with index i={3,4}
            print("Drawing the theoretical prediction")
        #players_qlist= Player.objects.all()
        #'offers':offer_listST
        player_list = Player.objects.filter(id_in_group__lt=99).order_by('id')
        Constants.script2, Constants.div2,Constants.sd_price_max,Constants.sd_price_min,Constants.sd_units=D_S_analysis()
    #what?

    else:
        time.sleep(1)
        Constants.init_started=False
        print("Constants.init_started",Constants.init_started)
        print("ERROR: Why is initialize called a second time???")
        return request
    Constants.init_started=False
    return render(request, 'dAuction2/code_assign.html', context={"player_list":player_list})
    # ToDo: the page still shows "initialize" and refresh creates new codes. How to make this a new page?
    #return HttpResponseRedirect(reverse('code_assignment'))




#def code_assignment:

def Admin_page1(request):
    player_list = Player.objects.all().order_by('id')
    context2=index_calculations(0, 0)

    #context2={"Constants":Constants,"player_list":player_list}
    return render(request,'dAuction2/Admin_page1.html', context= context2)



#def index(request, group_id, id_in_group):
def index(request, codename):
    print("index called")
    if Constants.stop:
        print("Constants.stop",Constants.stop)
        return request
    print("codename",codename)
    group_id, id_in_group=decode(codename)
    print("group_id, id_in_group",group_id, id_in_group)
    context2=index_calculations(group_id, id_in_group)
    context = RequestContext(request, context2)
    return render(request,'dAuction2/spot_market/index.html', context= context2)


def all_transactions(request,group_id, id_in_group):
#def all_transactions(request,codename):
#    group_id, id_in_group=decode(codename)

    context2=index_calculations(group_id, id_in_group)
    #print("all_trans called!")
    return render(request, 'dAuction2/spot_market/all_transactions.html', context=context2)


def all_standing_market_offers(request,group_id, id_in_group):
    #print("all_stand called!")
    #print("Connected player group id is:", group_id,)
    #print("Connected player id in group is:", id_in_group,)
    context2=index_calculations(group_id, id_in_group)
    return render(request,'dAuction2/spot_market/all_standing_market_offers.html',context = context2)


def my_standing_offer(request,group_id, id_in_group):
    context2=index_calculations(group_id, id_in_group)
    #print("my_stand 3333333333333333333333333333!")
    return render(request,'dAuction2/spot_market/my_standing_offer.html',context= context2)

def refresh(request,group_id, id_in_group):
#def refresh(request,codename):
#    group_id, id_in_group=decode(codename)
    print("BEGIN refresh!")
    context2=index_calculations(group_id, id_in_group)  # index_calculations calculates the up-to-date state

    print("END refresh!")
    return render(request,'dAuction2/spot_market/content_refresh.html',context= context2)

def show_theory(request,group_id, id_in_group):
    print("*********************************Show theory", Constants.show_theory)
    Constants.show_theory=not Constants.show_theory
    if Constants.show_theory:
       Constants.script2, Constants.div2,Constants.sd_price_max,Constants.sd_price_min,Constants.sd_units=D_S_analysis()

    print("*********************************Show theory", Constants.show_theory)
    return request


def stop(request,group_id, id_in_group):
    print("*********************************Stop", Constants.stop)

    Constants.stop=not Constants.stop
    if Constants.stop:
        Constants.show_theory=True
    print("*********************************Show theory", Constants.stop)
    return request



def refresh2(request,group_id, id_in_group):
    # DEM
    # remember: 1-2 are PR, 3-4 are RE
    # choose at random a player 2:1 odd a retailer
    # let make a bid
    if Constants.stop:
        return request
    print("refresh2 called")
    if random.randint(0,9)<6:
        type="BUY"
        p_id=random.randint(Constants.PR_number+1,Constants.PR_number+Constants.RE_number)
    else:
        type="SELL"
        p_id=random.randint(2,Constants.PR_number)
    #get rand_player's min and max value and decide its bid (but not player 1: the human! :) )

    g=getGroup(1)
    p=getPlayer(g,p_id)
    print("player:",p)

    # maximum 15 offers per player

    #     sell_priceST=[entry for entry in sell_listST.values_list('price',flat=True)]
    offer_list2 = Offer.objects.filter(player=p)\
                .exclude(canceled=True)\
                .filter(cleared=False)
    if offer_list2.count()>2: # once he has 2 offers out, with 66%change he makes a better offer
        #print("x=random(): BEFORE")
        x=random.random()
        #print("x=random():",x)
        if x<.6:
            print("BETTER OFFER ....................................................................... 1")
            offer_better=offer_list2.first()
            print("BETTER OFFER ....................................................................... 2", offer_better)
            print("offer_better.priceOriginal",offer_better.priceOriginal)
            p_vouchers=Voucher.objects.filter(player=p, used=False)
            p_values= [entry for entry in p_vouchers.values_list('value',flat=True)]
            print("type:",offer_better.type)
            newPrice= round(0.01+(( p_values[1]) - offer_better.priceOriginal)* 0.6+offer_better.priceOriginal)
            newUnits=round(0.01+offer_better.unitsAvailable*.6)
            print("offer_better : newPrice",newPrice)

            offer_better.delete()
            #offer_better.save()
            set_offer(request,1,p_id,newUnits,newPrice,offer_better.type)

            return request # ends here


    if offer_list2.count()<5:
        p_vouchers=Voucher.objects.filter(player=p, used=False, offered=False)
        #print(p_vouchers)
        p_values= [entry for entry in p_vouchers.values_list('value',flat=True)]
        print("p_values", p_values)
        p_unitsleft=p_vouchers.count()

        print("p_unitsleft", p_unitsleft)
        if p_unitsleft>0:
            p_units=random.randint(0,round(0.01+p_unitsleft/2))
            print("p_units",p_units)
            if type=="SELL":
                p_values_min=p_values[p_units-1]
                p_values_max=p_values[-1]
                print("p_values_max,p_values_min (sell)",p_values_max,p_values_min)
                p_price=random.randint(p_values_min,p_values_min+.25*(p_values_max-p_values_min))
                #print("p_vouchers",p_vouchers)
                print("BEFORE vouchers_offered=p_vouchers.filter(value__lte=p_price)")
                vouchers_offered=p_vouchers.filter(value__lte=p_price)
                print("AFTER vouchers_offered=p_vouchers.filter(value__lte=p_price)")
                print("vouchers_offered",vouchers_offered)
            else:
                p_values_min=p_values[-p_units]
                p_values_max=p_values[1]
                print("p_values_max,p_values_min (buy)",p_values_max,p_values_min)
                p_price=random.randint(p_values_min+.5*(p_values_max-p_values_min),p_values_max)
                #print("p_vouchers",p_vouchers)
                print("BEFORE vouchers_offered=p_vouchers.filter(value__lte=p_price) (buy)")
                vouchers_offered=p_vouchers.filter(value__gte=p_price)
                print("vouchers_offered",vouchers_offered)
            print("BEFORE for i in range(int(p_units/2)):")
            for i in range(int(p_units/2)):
                qq=vouchers_offered[i]
                #print("BEFORE i.offered=True")
                qq.offered=True
                qq.save()
                #print("AFTER i.offered=True")



            print("p_values_min",p_values_min)
            print("p_values_max",p_values_max)

            #filter(priceOriginal__gte=c.priceOriginal)

            #if type=="BUY":
            #    p_price=20
            #    p_units=random.randint(2,3)
            # FOR CHECKING - DELETE ABOVE LINE AFTERWARDS!!!!!!!!!!!!!!!!!!!!!! - OK, commented out
            # create bid
            # def set_offer(request,group_id, id_in_group,valUnits,valPrice,valType):


            set_offer(request,1,p_id,p_units,p_price,type)
        else:
            print("player ",p_id," has no units left")

        #context2=index_calculations(group_id, id_in_group)  # index_calculations calculates the up-to-date state
        #print("refresh!")
    else:
        print("player has already 3 offers out")
    return request


def cancel_so(request,group_id, id_in_group):
    if Constants.stop:
        return request
    print("cancel called")
    g=getGroup(int(group_id))
    p = getPlayer(g,int(id_in_group)) # ToDO: Group!!
    #Offer.objects.get(player=p).filter(cleared=False).last().delete()
    c=Offer.objects.filter(player=p).filter(cleared=False).filter(canceled=False).order_by('-id').first()
    c.canceled=True
    c.save()
    #Offer.objects.filter(player=p).filter(cleared=False).order_by('-id').first().delete()
    return render(request,'dAuction2/spot_market/my_standing_offer.html')





def set_offer(request,group_id, id_in_group,valUnits,valPrice,valType):
    # a player makes an offer. The offer is first created and then checked against the existing offers and matched and cleared if
    # possible

    #if Constants.stop:
    #    return request

    #state = Constants2.objects.get_or_create(id=1)[0]
    #print("state.setOffer_started", state.setOffer_started)
    #print ("state",state)

    #if not Constants.setOffer_started:
    if True:
        Constants.setOffer_started=True
        #state.save()

        print("set_offer called!")
        context2=""
        valUnits = int(valUnits)
        valPrice = int(valPrice)
        group_id = int(group_id)
        id_in_group = int(id_in_group)
        g=getGroup(group_id)
        p = Player.objects.get(id_in_group=id_in_group,group=g)
        p.save()
        #print("BEFORE if valUnits and valPrice and int(valPrice)>0 and int(valUnits)>0:")
        if valUnits and valPrice and int(valPrice)>0 and int(valUnits)>0:
            # first delete the last standing offer
            #if Offer.objects.filter(player=p).filter(cleared=False).order_by('-id').count()>0:
            #    Offer.objects.filter(player=p).filter(cleared=False).order_by('-id').first().delete()
            #!!!!!!!!!!!!!!! must be uncommented- commented for demo

            #now create the new offer
            c = Offer(player=p)
            c.unitsAvailable = int(valUnits)
            c.unitsOriginal = int(valUnits)
            c.unitsInherited = int(valUnits)
            c.group=g
            c.priceOriginal = int(valPrice)
            c.type = valType
            c.save()
            context2={'lastOffer':c}          #standing_offer=c
            print("New Offer:..................................................................................",c)
            print("price new offer:", c.priceOriginal)
            print("unitsAvailable new offer",c.unitsAvailable)
            if valType=="SELL": #then the matcher must be a buy
                offer_list2 = Offer.objects.filter(group=p.group)\
                    .exclude(player=p)\
                    .exclude(canceled=True)\
                    .filter(priceOriginal__gte=c.priceOriginal)\
                    .filter(type__iexact="BUY")\
                    .filter(cleared=False)
                offer_list = offer_list2.order_by('-priceOriginal','timeCreated')
                print("buys:",offer_list)
                print("buys:",offer_list.first())
            elif valType == "BUY":               #then the matcher must be a sell
                offer_list2 = Offer.objects.filter(group=p.group)\
                    .exclude(player=p)\
                    .exclude(canceled=True)\
                    .filter(priceOriginal__lte=c.priceOriginal)\
                    .filter(type__iexact='SELL')\
                    .filter(cleared=False)
                offer_list = offer_list2.order_by('priceOriginal','timeCreated')
                print("sells:",offer_list)
            else:
                raise ValueError('valType is neither SELL or BUY')
            #print("BEFORE first = offer_list.first()")
            first = offer_list.first()
            #print("AFTER first = offer_list.first()")
            #print("BEFORE first_player=first.player")
            if first:
                first_player=first.player
            else:
                first_player=None
            #print("AFTER first_player=first.player")
            #print("first counteroffer is:",first)

            while first is not None and c.unitsAvailable > first.unitsAvailable :
                print("greater!")
                print("first:",first)
                #1.clear the smaller, first
                clear_offer_smaller(first,c,first)
                # now we must split up the offer into two parts, the first of which is cleared, the second part is the
                # remaining units. This will be compared with other remaining offers (if any). If there are no other
                # offers, the second part becomes the standing offer with attr "updated" set to True.
                # a new offer is created, to carry the remaining units from the original offer
                #2.make copy for the larger, c into c2
                c2=copy_offer(c,p,first)
                #3.clear the larger, c (the part of the present offer that will be cleared)
                clear_offer_larger(first,c,first)
                #4. make transaction
                t = create_transaction(c, first)
                #5. set products
                setproducts(c,p,first,first_player)
                #print("before try, first",first)
                #6. set vouchers
                #set_voucher(p,first,first.unitsCleared)  # The vouchers are ticked
                set_voucher(p,first_player,first,c.unitsCleared)    # The vouchers are ticked

                offer_list3 = offer_list.exclude(cleared=True)   # update the list of remaining counter-offers
                print(offer_list3)
                c.save()
                c2.save()
                print("old c:",c)
                print("old c2:",c2)
                del c
                c=c2
                print("new c:",c)
                print("new c2:",c2)
                if offer_list3:
                    first=offer_list3.first() # get the update the list of remaining counter-offers
                else:
                    print("no more offers:",offer_list3)
                    first=None


            if first is not None and c.unitsAvailable < first.unitsAvailable:
                first_player=first.player
                print("smaller!")
                print(first)
                # now we must split up the counteroffer into two parts, the first of which is cleared, the second part is the
                # remaining units.

                #1.clear the smaller, c
                clear_offer_smaller(c,first,first)
                #2.make copy for the larger, first into f2
                f2=copy_offer(first,first_player,c)
                #print("after f2=copy_offer(first,first_player,c)")
                #3. clear the larger, first
                clear_offer_larger(c,first,first)
                #4. make transaction
                t = create_transaction(c, first)
                #5. set products
                setproducts(c,p,first,first_player)
                #calculate production costs or buyers values
                #6. set vouchers
                print("1st setvoucher call")
#                set_voucher(p,first,c.unitsCleared)    # The vouchers are ticked
                set_voucher(p,first_player,first,c.unitsCleared)    # The vouchers are ticked
                #print("After set_voucher(p,first,c.unitsCleared)")
                #print("After clear_c(c,first)  # clear c (as first.unitsA>c.unitsA)")
                first.save()
                f2.save()
                #print("f2.save()")

            elif first is not None and c.unitsAvailable == first.unitsAvailable:
                first_player=first.player
                print("now equal!")
                print(first)

                #1.clear the smaller, c
                clear_offer_smaller(c,first,first)
                #2.make copy for the larger - not necessary as equal

                #3.clear the larger, first
                clear_offer_larger(c,first,first)

                #4. make transaction
                t = create_transaction(c, first)

                #5. set products
                setproducts(c,p,first,first_player)
                #print("f2:  ",first)
                #print("1st setvoucher call")

                #6. set vouchers
                #def set_voucher(p,first_player,first,unitsCleared)
                set_voucher(p,first_player,first,c.unitsCleared)    # The vouchers are ticked

        else:
            if valUnits=='':
                messages.add_message(request, messages.INFO, 'fill out the number of units.')
            if valPrice=='':
                messages.add_message(request, messages.INFO, 'fill out the price per unit.')
            if valUnits=='0' or valPrice=='0':
                messages.add_message(request, messages.INFO, 'choose a number larger than zero.')
        #DEM:
        #print("BEFORE if id_in_group == 1:")
        Constants.setOffer_started=False
        #state.save()
        #if id_in_group == 1:
        if True:
            print("is me, thus render!")
            return render(request,'dAuction2/spot_market/my_standing_offer2.html', context = context2)
        else:
            print("is not me, no render! Is:",id_in_group)
            return request # DEM: must still be calculated context
    else:
        print("presently a set_offer procedure is running, so no others can be processed:",id_in_group)
        time.sleep(1)
        Constants.setOffer_started=False
        #state.save()
        return request
