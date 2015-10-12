__author__ = 'SLVSTR'
# These functions are mature in the sense that I think they function well and probably wont change
# or correct them

from dAuction2.models import Player, Group, Offer, Transaction, Voucher,Constants,Constants2, SD
import random, string
from functools import reduce
from django.db.models import Avg,Sum
from bokeh.plotting import figure, output_file, show
#from bokeh.resources import CDN
from bokeh.embed import components
from dAuction2.functions import *


def none_to_zero(elt):
    # changes the value None to 0 (an integer)
    if not elt:
        return [0]
    else:
        return(elt)

def transpose_pad(sellPrice,buyPrice):
    # returns a nx2 matrix that is the transpose of [sellPrice,buyPrice]
    # sellPrice and buyPrice do not need to have the same length
    # therefore, if sellPrice is shorter than buyPrice: sellPrice is padded with 999999s until it has equal length
    # therefore, if buyPrice is shorter than sellPrice: buyPrice is padded with -1s until it has equal length
    # To avoid unnecessary long strings, I check if there is padding for the larger vector, and if so,
    # it is stripped
    # The correct padding takes up all the code lines here, the transposition is done in one line (the last one)

    diff= len(sellPrice) - len(buyPrice)
    if diff!=0:
        # if the two vectors are not of equal length, they have to be padded (or excess padding must be stripped)
        if diff < 0:                                # which one is the longest
            # buyPrice is the longest, so first try and strip buyPrice
            buyPrice = [aa for aa in buyPrice if aa !=-1]
            diff2= len(sellPrice) - len (buyPrice)
            if diff2 < 0:
                # check if buyPrice is still longer
                sellPrice.extend([(999999,999999,999999)]*abs(diff2))
                    # buyPrice is still longer, so sellPrice is padded
            else:
                raise ValueError('transposepad failed for diff<0')
        else:
            # sellPrice is the longest, so first try and strip sellPrice
            sellPrice = [aa for aa in sellPrice if aa != 999999]
            diff2= len(sellPrice) - len (buyPrice)
            if diff2 > 0:
                # check if sellPrice is still longer
                buyPrice.extend([(-1,-1,-1)]*abs(diff2))
                    # sellPrice is still longer, so sellPrice is padded
            else:
                raise ValueError('transposepad failed for diff>0')
    return(list(zip(*[sellPrice,buyPrice])))
        # the expression here does the transposition



def accumulator(zz):
    # I forgot what this does exactly, but I remember it is important for the market orders table
    qq=[]
    length=len(zz)
    prevCum=0
    if length==0:
        pass
    elif length==1:
        qq=zz
    elif length>1:
        for i in range(0,len(zz)-1):
            if zz[i][0] !=zz[i+1][0]:
                qq.append((zz[i][0],zz[i][2]-prevCum,zz[i][2]))
                prevCum=zz[i][2]
        qq.append((zz[i+1][0],zz[i+1][2]-prevCum,zz[i+1][2]))
    else:
        pass
    return qq


def doubley(x):
#  this function doubles a list with y coordinates for the graph. The doubling is done so that the graph
#  will have a step form.
    if x:
        qwy=[x for pair in zip(x,x) for x in pair]
        return qwy


def doublex(x):
    #  this function doubles a list with x coordinates for the graph. The doubling is done so that the graph
    #  will have a step form.
    if x:
        qwx=[x for pair in zip(x,x) for x in pair]
        qwx.insert(0,0)
        del qwx[-1]
        return qwx


def getGroup(group_id):
    # gets or creates the correct group object given the group number #group_id
    print("BEGIN getGroup(group_id):", group_id)
    g = Group.objects.get_or_create(group_id=group_id)[0]
    g.save()
    return g


def getPlayer(g, id_in_group):
    # gets or creates the correct player object given the player number #id_in_group
    p = Player.objects.get_or_create(group=g,id_in_group=id_in_group)[0]
    #p.money=10000
    p.save()
    return p

def myround(x, base=20):
    # how I want to round numbers. The function allows me to have different rounding rules
    return int(base * round(float(x)/base))


def cummulator(listt):
    # gets a list with cummulative values
        return reduce(lambda acc, listt: acc + [acc[-1] + listt], listt[1:], listt[:1])

def median_value(queryset,term):
    # gets the median value of a #term in a #queryset
    if queryset:
        #print(" inside if", queryset)
        count = queryset.count()
        return queryset.values_list(term, flat=True).order_by(term)[int(round(count/2))]
    else:
        return(None)

def median_value10(queryset,term):
    # gets the median value of the last 10 observations of a #term in a #queryset
    if queryset:
        #print(" inside if", queryset)
        count = queryset.count()
        count2=min(count,10)
        id_include=max(1,count-10)
        return queryset.filter(id__gte=id_include).values_list(term, flat=True).order_by(term)[int(round(count2/2))]
    else:
        return(None)


def copy_offer(c,p, first):
    # creates a copy of the offer (real copy, not a damn second pointer to the same object).
    # This one will contain the remaining units
    # I think there is a standard Python command for this, but I somehow didnt manage to get it done
    print("BEGIN copy_offer(c,p, first):",c,p,first)
    c2 = Offer(player=p,group=c.group,parentId=c.id)
    c2.priceOriginal = c.priceOriginal
    c2.timeCreated=c.timeCreated
    c2.unitsOriginal=c.unitsOriginal
    c2.type=c.type
    c2.unitsInherited = c.unitsAvailable - first.unitsCleared
    c2.unitsAvailable = c.unitsAvailable - first.unitsCleared
    print("c2.unitsAvailable:",c2.unitsAvailable ,"c2.unitsInherited:",c2.unitsInherited )
    #c2.unitsCleared=0
    c2.updated=True
    c2.save()
    print("END copy_offer(c,p, first):",c,p,first)
    return c2


def decode(codename):
    # given the codename, the player is retrieved
    print("BEGIN decode")
    p = Player.objects.get_or_create(codename=codename)[0]
    g=p.group
    print("g, p",g,p)
    print("END decode")
    return g.group_id, p.id_in_group



def setproducts(c,p,first,first_player):
    # calculates the revenue for a sale or total cost for a buy
    # the revenue is then added to the trading result (the income from trading for a player)
    print("call setproducts")
    print("c.type:",c.type)
    if c.type=="SELL": # thus player p is selling and thus first is a buying offer
        c.product=first.priceCleared *first.unitsCleared
        first.product= -1 *first.priceCleared *first.unitsCleared
    else:
        c.product=-1 *first.priceCleared *first.unitsCleared
        first.product= first.priceCleared *first.unitsCleared
    p.trading_result+=c.product
    first_player.trading_result+=first.product
    c.save()
    first.save()
    p.save()
    first_player.save()
    print("END setproducts(c,p,first,first_player):",c,p,first,first_player)


def set_voucher(p,first_player,first,unitsCleared):
    # this writes the changes to the vouchers of players after they have made a transaction
    # For Producers (Retailers), vouchers are used as they sell (buy).
    # For Producers (Retailers), vouchers are released if they buy (sell).
    # If a Producer (Retailers) buys (sells) more than he has sold (bought) extra vouchers are created for him
    # #p is the player that is treated, #first_player is the best match (the first in the list)
    # #first is the offer of #first_player, #unitsCleared is the number of units in the transaction between
    # #p and #first_player


# first treat the vouchers of the present bidder (#p)
    print("BEGIN set_voucher(p,first,unitsCleared):",p,first,unitsCleared)
    tel_p=Voucher.objects.filter(player=p, used=True).count()
    tel_all_p=Voucher.objects.filter(player=p).count()
    negative_p=35-tel_all_p
        # negative_p gives the number of extra vouchers player #p has
        # (generally 0, but can be positive with speculation
    #print ("tel_p",tel_p)
    #print ("tel_all_p",tel_all_p)
    tel_f=Voucher.objects.filter(player=first_player, used=True).count()
    tel_all_f=Voucher.objects.filter(player=first_player).count()
    negative_f=35-tel_all_f
        # negative_f gives the number of extra vouchers player #first_player has
        # (generally 0, but can be positive with speculation

    # now, if p is a REtailer BUYing or a PRoducer SELLing, usual treatment - make units used
    # if p is a REtailer SELLing or a PRoducer BUYing, the reverese treatment - "unuse" units
    # if a PRoducer buys more goods than he has sold, he receives new production units with a cost of 0. These are on
    # the top of the list and filled out first
    # if a REtailer sells more goods than he has bought, he receives new value units with a value of 0.  These are on
    # the top of the list and filled out first

    if (p.role=="RE" and first.type=="SELL") or (p.role=="PR" and first.type=="BUY"):
        # thus p is a REtailer, and the counterparty sold, so REtailer p bought
        # or p is a PRoducer, and the counterparty bought, so PRoducer p sold
        # standard case
        print("standard case for p")
        #  treat the vouchers of the party (p)
        for i in range(tel_p+negative_p,unitsCleared+tel_p+negative_p):
            #print("vv=Voucher.objects.filter(player=p,idd=i+1)")
            vv=Voucher.objects.get(player=p,idd=i+1)
            #print("i+1",i+1)
            #print("vv:",vv)
            vv.price=first.priceCleared
            vv.used=True
            #print("if p.role==PR:") # Before this point, the procedure errors (silently) out! price->priceCleared
            vv.save()
        #print("BEFORE set_total_cost_value(p,vv.value_cum)")
        #print("p,vv.value_cum",p,vv.value_cum)
        set_total_cost_value(p,vv.value_cum)
        #print("AFTER set_total_cost_value(p,vv.value_cum)")

# treat the vouchers of the counterparty (#first_player)
        print("2nd... setvoucher call")

        #must check if it is standard case for first_player or not
        if (first_player.role=="RE" and first.type=="BUY") or (first_player.role=="PR" and first.type=="SELL"):
            # thus fp is a REtailer, and bought
            # or fp is a PRoducer, and sold
            # standard case
            print("standard case for first_player")

            for i in range(tel_f+negative_f,unitsCleared+tel_f+negative_f):
                vv2=Voucher.objects.get(player=first_player,idd=i+1)
                vv2.price=first.priceCleared
                vv2.used=True
                #print("if p.role==PR:")
                vv2.save()
            set_total_cost_value(first_player,vv2.value_cum)
            print("first_player,vv2.value_cum",first_player,vv2.value_cum)
        else:
            # thus first_player is a REtailer, and the counterparty bought, so REtailer first_player sold
            # or first_player is a PRoducer, and the counterparty sold, so PRoducer first_player bought
            # reversed case
            print("2nd setvoucher call")
            print("reversed case for for first_player")
            v=create_and_cut_vouchers(first_player,p,first,unitsCleared)
            set_total_cost_value(first_player,v.value_cum-v.value)
    else:
        # thus p i s a REtailer, and the counterparty bought, so REtailer p sold
        # or p is a PRoducer, and the counterparty sold, so PRoducer p bought
        # reversed case
        print("reversed case for p")
        v=create_and_cut_vouchers(p,p,first,unitsCleared)
        set_total_cost_value(p,v.value_cum-v.value)

        # second, treat the vouchers of the counterparty (first.player)
        print("2nd setvoucher call")
        #must check if it is standard case for first_player or not
        if (first_player.role=="RE" and first.type=="BUY") or (first_player.role=="PR" and first.type=="SELL"):
            # thus fp is a REtailer, and bought
            # or fp is a PRoducer, and sold
            # standard case
            print("standard case for first_player")

            for i in range(tel_f+negative_f,unitsCleared+tel_f+negative_f):
                vv2=Voucher.objects.get(player=first_player,idd=i+1)
                vv2.price=first.priceCleared
                vv2.used=True
                #print("if p.role==PR:")
                vv2.save()
            set_total_cost_value(first_player,vv2.value_cum)
            print("first_player,vv2.value_cum",first_player,vv2.value_cum)
        else:
            # thus first_player is a REtailer, and the counterparty bought, so REtailer first_player sold
            # or first_player is a PRoducer, and the counterparty sold, so PRoducer first_player bought
            # reversed case
            print("2nd setvoucher call")
            print("reversed case for for first_player")
            v=create_and_cut_vouchers(first_player,p,first,unitsCleared)
            set_total_cost_value(first_player,v.value_cum-v.value)
    print("END set_voucher(p,first,unitsCleared):",p,first,unitsCleared)


def create_and_cut_vouchers(player_to_set,p,first,unitsCleared):
    # if a producers buys units, the used vouchers must be freed for re-use. If the producer buys more units
    # than he sold previously, extra vouchers are made for him.
    # if a retailer sells units, the used vouchers must be freed for re-use. If the retailer sells more units
    # than he bought previously, extra vouchers are made for him.
    print("BEGIN create_and_cut_vouchers(player_to_set,p,first,unitsCleared):",player_to_set,p,first,unitsCleared)
    tel_p=Voucher.objects.filter(player=player_to_set, used=True).count()
    tel_all_p=Voucher.objects.filter(player=player_to_set).count()
    negative_p=35-tel_all_p
    unitsCleared2=unitsCleared
    if tel_p-unitsCleared<0:
        for i in reversed(range(tel_p-unitsCleared+negative_p,negative_p)):
            print("reversed(range (tel_p-unitsCleared,tel_p))",reversed(range (tel_p-unitsCleared,tel_p)))
            v = Voucher(idd=i+1,value_cum=0,value=0,player=player_to_set,group=p.group,role=player_to_set.role)
            print("i",i)
            v.save()
        unitsCleared2=tel_p

    for i in reversed(range (tel_p-unitsCleared2+negative_p,tel_p+negative_p)):
        v=Voucher.objects.get(player=player_to_set,idd=i+1)
        v.price=first.priceCleared
        v.used=False
        v.save()
    print("END create_and_cut_vouchers(player_to_set,p,first,unitsCleared):",player_to_set,p,first,unitsCleared)
    return v #returns the last treated voucher


def set_total_cost_value(p,value_cum):
    # p is a player
    # vv is a voucher
    print("BEGIN set_total_cost_value(p,value_cum):",p,value_cum)
    if p.role=="PR":
        p.total_cost= value_cum
        p.profit=p.trading_result-p.total_cost
    else:
        p.total_values= value_cum
        p.profit=p.trading_result+p.total_values
    p.save()
    print("END set_total_cost_value(p,value_cum):",p,value_cum)


def clear_offer_smaller(smaller,larger,first):
    # procedure sets the values correctly after a transaction
    # remember that if my offer reacts to a standing offer (an offer that was made earlier than mine),
    # then the transaction price is determined by the offer price of that standing order. If my offer
    # was standing and a new offer matched to mine, then the transaction price is set by my offer price
    print("BEGIN clear_offer_smaller(smaller,larger,first):",smaller,larger,first)
    smaller.cleared=True
    smaller.counterOffer_id=larger.id
    #print("c.unitsAvailable=",c.unitsAvailable,"first.unitsAvailable=", first.unitsAvailable)
    smaller.unitsCleared=smaller.unitsAvailable+0 # smaller is always cleared first
    smaller.priceCleared=first.priceOriginal
    smaller.unitsAvailable=0  # this is the part of the original offer that is cleared
    smaller.save()
    print("END clear_offer_smaller(smaller,larger,first):",smaller,larger,first)


def clear_offer_larger(smaller,larger,first):
    # procedure sets the values correctly after a transaction
    # remember that if my offer reacts to a standing offer (an offer that was made earlier than mine),
    # then the transaction price is determined by the offer price of that standing order. If my offer
    # was standing and a new offer matched to mine, then the transaction price is set by my offer price

    print("BEGIN clear_offer_larger(smaller,larger,first):",smaller,larger,first)
    larger.cleared=True
    larger.counterOffer_id=smaller.id
    #print("c.unitsAvailable=",c.unitsAvailable,"first.unitsAvailable=", first.unitsAvailable)
    larger.unitsCleared=smaller.unitsCleared+0 # smaller is always cleared first, and thus unitsAvailable has not been set to zero
    larger.priceCleared=first.priceOriginal
    larger.unitsAvailable=0  # this is the part of the original offer that is cleared
    larger.save()
    print("END clear_offer_larger(smaller,larger,first):",smaller,larger,first)


def create_transaction(c,first):
    # this creates a transaction. #c is the present offer, #first is the best standing offer with which it can
    # be matched first (first in the list of possible matches)
    print("BEGIN create_transaction(c,first):",c,first)
    t = Transaction()
    t.group=c.group
    if c.type == "SELL":
        t.sellerOffer = c
        t.sellerPrice= c.priceOriginal
        t.buyerOffer = first
        t.buyerPrice= first.priceOriginal
    else:
        t.sellerOffer = first
        t.sellerPrice= first.priceOriginal
        t.buyerOffer = c
        t.buyerPrice= c.priceOriginal
    t.units = min(first.unitsCleared, c.unitsCleared)
    t.price = first.priceOriginal
    #print("now saving t")
    t.save()
    print("END create_transaction(c,first):",c,first)
    return(t)