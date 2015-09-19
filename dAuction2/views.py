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


# Functions I use here:
def transpose_pad(sellPrice,buyPrice):
    # returns a nx2 matrix that is the transpose of [sellPrice,buyPrice]
    # sellPrice and buyPrice do not need to have the same length
    # therefore, if sellPrice is shorter than buyPrice: sellPrice is padded with 999999s until it has equal length
    # therefore, if buyPrice is shorter than sellPrice: buyPrice is padded with -1s until it has equal length
    # To avoid unnecessary long strings, I check if there is padding for the larger vector, and if so,
    #  it is stripped

    diff= len(sellPrice) - len(buyPrice)
    #print(diff)
    if diff!=0:
        if diff < 0:                                # which one is the longest
            buyPrice = [aa for aa in buyPrice if aa !=-1]     # buyPrice is the longest, so first try and strip buyPrice
            diff2= len(sellPrice) - len (buyPrice)                 # check if buyPrice is still longer
            if diff2 < 0:
                sellPrice.extend([(999999,999999,999999)]*abs(diff2))           # buyPrice is still longer, so sellPrice is padded
            else:
                raise ValueError('transposepad failed for diff<0')
        else:
            sellPrice = [aa for aa in sellPrice if aa != 999999]
            diff2= len(sellPrice) - len (buyPrice)
            if diff2 > 0:
                buyPrice.extend([(-1,-1,-1)]*abs(diff2))
            else:
                raise ValueError('transposepad failed for diff>0')
    return(list(zip(*[sellPrice,buyPrice])))


def accumulator(zz):
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
#  this function doubles a list with y coordinates for the graph. The doubling is done so that the graph will have
#  a step form.
    if x:
        qwy=[x for pair in zip(x,x) for x in pair]
        return qwy


def doublex(x):
#  this function doubles a list with x coordinates for the graph. The doubling is done so that the graph will have
#  a step form.
    if x:
        qwx=[x for pair in zip(x,x) for x in pair]
        qwx.insert(0,0)
        del qwx[-1]
        return qwx


def getGroup(group_id):
    print("BEGIN getGroup(group_id):", group_id)
    g = Group.objects.get_or_create(group_id=group_id)[0]
    g.save()
    return g


def getPlayer(g, id_in_group):
    p = Player.objects.get_or_create(group=g,id_in_group=id_in_group)[0]
    #p.money=10000
    p.save()
    return p

def myround(x, base=20):
    return int(base * round(float(x)/base))

def createPlayer(g, id_in_group,role):
    print("BEGIN createPlayer (g, id_in_group,role):",g, id_in_group,role)# DEM
    # create the main player - Producer
    # then in addition 4 more producers
    # and 5 retailers
    #print(Constants.understanding_1_correct)
    #Constants.understanding_1_correct="What???"
    #print(Constants.understanding_1_correct)
    r_average=10
    r_sd=20
    p_average=.01
    p_sd=.5
    r_start=1000
    r_max=60
    r_min=0

    p_max=30
    p_min=0

    p = Player.objects.get_or_create(group=g,id_in_group=id_in_group)[0]
    #c = Constants()
    print("CREATEPLAYER!!! for:",p)
    p.role=role
    p.money=10000
    print ("role",role)
    if role=="RE":
        p.name="value"
    p.save()
    value2=[]
    value2_cumm=[]
    valPR=0
    valRE=r_start
    if role=="PR":
        for i in range(35):
            #value2.append(int(max(0,round(random.gauss(p_average, p_sd),-1))))  #is good, but slow
            #valPR+=round(random.randint(p_min, p_max),-1)
            valPR+=abs(myround(random.gauss(i*i*i*p_average, (i*i*p_sd))))
            valPR=min(valPR,1200)
            value2.append(valPR)
            #value2.sort()
            #value2_cumm=reduce(lambda acc, value2: acc + [acc[-1] + value2], value2[1:], value2[:1])
            value2_cumm=cummulator(value2)
    elif role=="RE":
        for i in range(35):
            #value2.append(int(max(0,round(random.gauss(r_average, r_sd),-1))))  #is good, but slow
            #valRE=max(0,valRE - round(random.randint(r_min, r_max),-1))
            valRE=max(0,valRE - abs(myround(random.gauss(r_average, r_sd))))
            value2.append(valRE)
            #value2.append(int(max(0,round(random.randint(r_min, r_max),-1))))
            #value2.sort(reverse=True)
            #value2_cumm=reduce(lambda acc, value2: acc + [acc[-1] + value2], value2[1:], value2[:1])
            value2_cumm=cummulator(value2)
    #print(value2)
    #Voucher.objects.filter(player=p).delete()
    #Offer.objects.filter(player=p).delete()
    #Transaction.objects.filter(player=p).delete()

    for i in range(35):
        v = Voucher(idd=i+1,value_cum=value2_cumm[i],value=value2[i],player=p,group=p.group,role=role)
        v.save()
    print("END createPlayer (g, id_in_group,role):",g, id_in_group,role)# DEM
    return p


def cummulator(listt):
        return reduce(lambda acc, listt: acc + [acc[-1] + listt], listt[1:], listt[:1])

def median_value(queryset,term):
    if queryset:
        #print(" inside if", queryset)
        count = queryset.count()
        return queryset.values_list(term, flat=True).order_by(term)[int(round(count/2))]
    else:
        return(None)

def median_value10(queryset,term):
    if queryset:
        #print(" inside if", queryset)
        count = queryset.count()
        count2=min(count,10)
        id_include=max(1,count-10)
        return queryset.filter(id__gte=id_include).values_list(term, flat=True).order_by(term)[int(round(count2/2))]
    else:
        return(None)


from django.db.models import Avg,Sum



def index_calculations(group_id, id_in_group):
    print("index calc called!")
    group_id=int(group_id)
    id_in_group=int(id_in_group)
    # we need to check if there are player objects already
    g=getGroup(group_id)
    p=getPlayer(g,id_in_group)



    # ToDo: distinguis between the groups in the queries
    trans_list2 = Transaction.objects.filter(group=p.group).order_by('-id')
    voucher_list = Voucher.objects.filter(player=p).order_by('idd')
    units_produced= int(Voucher.objects.filter(used=True).count()/2)


    # median price, average price, units traded,
    if trans_list2:
        #print("BEFORE median_price")

        count =min(10, trans_list2.count())
        lasttrans=trans_list2.first()
        max_id=lasttrans.id
        print("count",count)
        id_include=max(1,max_id-count)

        median_price= median_value(trans_list2,"price")
        median_price_last10transactions= median_value10(trans_list2,"price")
        #average_price2= trans_list2.aggregate(Avg('price'))
        #print("average_price2",average_price2)
        average_price=int(round(trans_list2.aggregate(Avg('price'))["price__avg"]))
        average_price_last10transactions=int(round(trans_list2.filter(id__gte=id_include).aggregate(Avg('price'))["price__avg"]))

        #print("id_include",id_include)
        #print("trans_list2.filter(id__gte=id_include)",trans_list2)
        ##print("average_price",trans_list2.aggregate(Avg('price')))
        #print("trans_list2.filter(id__gte=id_include)",trans_list2.filter(id__gte=id_include))
        #print("average_price_last10transactions",trans_list2.filter(id__gte=id_include).aggregate(Avg('price')))
        #units2= trans_list2.aggregate(Sum('units'))
        units=round(int(trans_list2.aggregate(Sum('units'))["units__sum"]))
        #print("AFTER  median_price")
        units=round(int(trans_list2.aggregate(Sum('units'))["units__sum"]))

    else:
        median_price= None
        median_price_last10transactions=None
        average_price_last10transactions=None
        average_price= None
        units=None





    #############################




    offer_listST3 = Offer.objects.filter(group=p.group).exclude(canceled=True)

    offer_listST2 = offer_listST3.filter(cleared=False)
    offer_listST = offer_listST2.order_by('-id')
    #offer_listST_inv = offer_listST2.order_by('id')[:135]
    sell_listST = offer_listST2.filter(type = "SELL").order_by('priceOriginal')
    sell_priceST=[entry for entry in sell_listST.values_list('priceOriginal',flat=True)]
    sell_priceSTdb=doubley(sell_priceST)

    sell_unitsST=[entry for entry in sell_listST.values_list('unitsAvailable',flat=True)]
    sell_cumST = reduce(lambda acc, sell_unitsST: acc + [acc[-1] + sell_unitsST], sell_unitsST[1:], sell_unitsST[:1])
    #sell_cumST = cummulator(sell_unitsST)    #

    sell_cumSTdb=doublex(sell_cumST)

    sell_tupST2=list(zip(sell_priceST,sell_unitsST,sell_cumST))
    sell_tupST=accumulator(sell_tupST2)

    if not sell_cumSTdb:
        sell_cumSTdb=[0]
    if not sell_priceSTdb:
        sell_priceSTdb=[0]

    buy_listST2 = offer_listST2.filter(type = "BUY")
    buy_listST = buy_listST2.order_by('-priceOriginal')

    buy_priceST=[entry for entry in buy_listST.values_list('priceOriginal',flat=True)]
    buy_priceSTdb=doubley(buy_priceST)

    buy_unitsST=[entry for entry in buy_listST.values_list('unitsAvailable',flat=True)]
    buy_cumST = reduce(lambda acc, buy_unitsST: acc + [acc[-1] + buy_unitsST], buy_unitsST[1:], buy_unitsST[:1])
    buy_cumSTdb=doublex(buy_cumST)
    buy_tup2ST=list(zip(buy_priceST,buy_unitsST,buy_cumST))
    buy_tupST=accumulator(buy_tup2ST)

    if not buy_priceSTdb:
        buy_priceSTdb=[0]
    if not buy_cumSTdb:
        buy_cumSTdb=[0]

    standing_marketST=transpose_pad(sell_tupST,buy_tupST)
    combo_offerST= transpose_pad(list(sell_listST), list(buy_listST))

    myOffers2= offer_listST3.filter(player=p).order_by('-id')

    myOffersCL= myOffers2.filter(cleared=True)
    myOffersCL_inv=myOffersCL.order_by('id')
    myOffersST= myOffers2.filter(cleared=False)
    lastOfferST = myOffersST.first()

    player_list = Player.objects.order_by('id')

    transactionList=Transaction.objects.filter(group=p.group).order_by('id')
    transaction_id=list([entry for entry in transactionList.values_list('id',flat=True)])
    transaction_price=doubley(list([entry for entry in transactionList.values_list('price',flat=True)]))
    transaction_bprice=doubley(list([entry for entry in transactionList.values_list('buyerPrice',flat=True)]))
    transaction_sprice=doubley(list([entry for entry in transactionList.values_list('sellerPrice',flat=True)]))
     #transaction_price=doubley(transaction_price2)
    transaction_units=[entry for entry in transactionList.values_list('units',flat=True)]
    transaction_units_cum2 = reduce(lambda acc, transaction_units: acc + [acc[-1] + transaction_units], transaction_units[1:], transaction_units[:1])
    transaction_units_cum=doublex(transaction_units_cum2)

    transaction_units=none_to_zero(transaction_units)
    transaction_units_cum=none_to_zero(transaction_units_cum)

    transaction_price=none_to_zero(transaction_price)
    transaction_bprice=none_to_zero(transaction_bprice)
    transaction_sprice=none_to_zero(transaction_sprice)




    if transaction_units_cum2:
        #print("transaction_units_cum2]",transaction_units_cum2)
        #print("transaction_units_cum2[-1]",transaction_units_cum2[-1])
        xsell_cumSTdb=[x+transaction_units_cum2[-1] for x in sell_cumSTdb]
        #xsell_priceST
    else:
        xsell_cumSTdb=sell_cumSTdb

    if transaction_units_cum2:
        #print("transaction_units_cum2]",transaction_units_cum2)
        #print("transaction_units_cum2[-1]",transaction_units_cum2[-1])
        xbuy_cumSTdb=[x+transaction_units_cum2[-1] for x in buy_cumSTdb]
        #xsell_priceST
    else:
        xbuy_cumSTdb=buy_cumSTdb

    print("Drawing the transactions figure")
    #Drawing the transactions figure
    pl = figure()
    pl.toolbar_location = None
    #pl.tools = None
    pl.min_border_left = 0
    pl.min_border_right = 10
    pl.min_border_top = 1
    pl.min_border_bottom = 0
    pl.background_fill = "white"
    pl.border_fill = 'whitesmoke'
    pl.plot_width=925
    pl.plot_height = 370
    pl.xaxis.axis_label = "Units"
    pl.yaxis.axis_label = "Price"
    pl.yaxis.axis_label_text_font_size="10pt"
    pl.xaxis.axis_label_text_font_size="10pt"
    pl.xaxis.axis_label_standoff = 1
    pl.yaxis.axis_label_standoff = 1
    pl.line(transaction_units_cum, transaction_price,color="black",line_width=4)
    pl.line(transaction_units_cum, transaction_bprice,color="blue",line_dash=[1, 3],line_width=2)
    pl.line(transaction_units_cum, transaction_sprice,color="red",line_dash=[1, 3],line_width=2)
    pl.line(xsell_cumSTdb,sell_priceSTdb,color="red",line_width=2)
    pl.line(xbuy_cumSTdb,buy_priceSTdb,color="blue",line_width=2)

    #print("transaction_units_cum, transaction_price",transaction_units_cum, transaction_price)
    #print("transaction_units_cum, transaction_bprice",transaction_units_cum, transaction_bprice)
    #print("transaction_units_cum, transaction_sprice",transaction_units_cum, transaction_sprice)
    #print("xsell_cumSTdb, sell_priceSTdb",xsell_cumSTdb, sell_priceSTdb)
    #print("xbuy_cumSTdb, buy_priceSTdb",xbuy_cumSTdb, buy_priceSTdb)

    #print("script, div " )
    script, div = components(pl)
    #print("script, div ",script, div )

    #print(Constants)
    if Constants.show_theory:
        Constants.script2, Constants.div2,Constants.sd_price_max,Constants.sd_price_min,Constants.sd_units=D_S_analysis()





    context2 =  {"Constants":Constants,"units_produced":units_produced,
                 "average_price_last10transactions":average_price_last10transactions,"median_price_last10transactions":median_price_last10transactions,
                 "units":units,"average_price":average_price,"median_price":median_price,"vouchers":voucher_list, "player":p,"group":g,"id_in_group": id_in_group,"group_id": group_id,
                 "script": script, "div": div
        ,'combo_offers': combo_offerST,'combo_offers2':standing_marketST, 'buy_offers': buy_listST
        ,'sell_offers': sell_listST,'myOffers': myOffersCL,'myOffers_inv':myOffersCL_inv,'myOffersST': myOffersST,'lastOffer': lastOfferST,'players': player_list
        ,'offers':offer_listST, 'transactions': trans_list2}
    return context2

def none_to_zero(elt):
    if not elt:
        return [0]
    else:
        return(elt)

###########################################################
# "real" views


def initialize(request, group_id, id_in_group):
    # DEM
    # create the main player - Producer
    # then in addition 4 more producers
    # and 5 retailers
    #state = Constants2.objects.get_or_create(id=1)[0]
    #print ("state",state)
    if not Constants.init_started:
        Constants.init_started=True
        print ("Constants.init_started",Constants.init_started)
        #state.save()
        Voucher.objects.all().delete()
        Transaction.objects.all().delete()
        Offer.objects.all().delete()
        Player.objects.all().delete()
        Group.objects.all().delete()
        group_id=int(group_id)
        id_in_group=int(id_in_group)
        # we need to check if there are player objects already
        g=getGroup(group_id)
        for i in range(1,Constants.PR_number+1):
            createPlayer(g,i,"PR") # 5 producers, with index i={1,2}
        for i in range(Constants.PR_number+1,Constants.PR_number+Constants.RE_number+1):
            createPlayer(g,i,"RE") # 2 retailers, with index i={3,4}
            print("Drawing the theoretical prediction")

        Constants.script2, Constants.div2,Constants.sd_price_max,Constants.sd_price_min,Constants.sd_units=D_S_analysis()
    #what?

    else:
        print("ERROR: Why is initialize called a second time???")
    return HttpResponseRedirect(reverse('index',args=(group_id,id_in_group)))

def D_S_analysis():
    # calculate D-S analyzis
    # ONLY NEEDS TO BE DONE ONCE - SHOULD BE MOVED SOMEWHERE
    print("def D_S_analysis()  CALLED ........................................................")
    g=getGroup(1)
    p=getPlayer(g,1)
    if True:
        DS_cost = Voucher.objects.filter(idd__gt=0).filter(role="PR").order_by('value')
        DS_value = Voucher.objects.filter(idd__gt=0).filter(role="RE").order_by('-value')
        DS_cost_list=[entry for entry in DS_cost.values_list('value',flat=True)]
        DS_value_list=[entry for entry in DS_value.values_list('value',flat=True)]
        print("DS_cost_list",DS_cost_list)
        #print("DS_value_list",DS_value_list)
        #n = 1
        #DS_cost_x=[]
        #for elem in DS_cost_list:
        #    DS_cost_x.append(n)
        #    n += 1
        #n=1
        #DS_cost_x=[]
        DS_cost_x=range(1,len(DS_cost_list)+1)

        #DS_value_x=[]
        #for elem in DS_value_list:
        #    DS_value_x.append(n)
        #    n += 1
        DS_value_x=range(1,len(DS_value_list)+1)
        #DS_cost_x=[x+1 for x in DS_cost_list]
        #DS_value_x=[x+1 for x in DS_value_list]
        #print("DS_cost_x",DS_cost_x)
        #print("DS_value_x",DS_value_x)
        DS_cost_x_db=doublex(DS_cost_x)
        DS_value_x_db=doublex(DS_value_x)
        DS_cost_list_db=doubley(DS_cost_list)
        DS_value_list_db=doubley(DS_value_list)


        DS_net= [x - y for x, y in zip(DS_value_list,DS_cost_list)]
        DS_index=[i for i,x in enumerate(DS_net) if x<0][0]-1  #gets the indexes for when x<0

        print("DS_net",DS_net)
        #print("DS_net_abs",DS_index)
        price_max = DS_value_list[DS_index]
        price_min = DS_cost_list[DS_index]

        #############################
        relevantVouchers=Voucher.objects.filter(player=p).filter(idd__gt=0).filter(value__lte=price_max)
        Constants.my_cost_th = relevantVouchers.aggregate(Sum('value'))["value__sum"]

        Constants.my_profit_th=relevantVouchers.last().idd * price_max - Constants.my_cost_th
        print("Constants.my_profit_th",Constants.my_profit_th)
        print("Constants.my_cost_th",Constants.my_cost_th)
        print("price_max",price_max)

        Constants.my_score= round((p.profit / Constants.my_profit_th) * 100)
        #DS_PR_net= [x - y for x, y in zip(DS_value_list,DS_cost_list)]
        #DS_index=[i for i,x in enumerate(DS_net) if x<0][0]-1  #gets the indexes for when x<0

        #print("price between ",DS_cost_list[DS_index]," and ",DS_value_list[DS_index])
        DS_index_x=[DS_index,DS_index]
        DS_index_y=[0,price_max]
        price_max_x=[0,DS_index]
        price_max_y=[price_max,price_max]
        price_min_x=[0,DS_index]
        price_min_y=[price_min,price_min]
        # calculate D-S analyzis END

        #Drawing the theoretical prediction
        pl2 = figure()
        pl2.toolbar_location = None
        #pl2.tools = None
        pl2.min_border_left = 0
        pl2.min_border_right = 10
        pl2.min_border_top = 1
        pl2.min_border_bottom = 0
        pl2.border_fill = 'orange'
        pl2.background_fill = "whitesmoke"
        pl2.plot_width=925
        pl2.plot_height = 270
        pl2.xaxis.axis_label = "Units"
        pl2.yaxis.axis_label = "Price"
        pl2.yaxis.axis_label_text_font_size="10pt"
        pl2.xaxis.axis_label_text_font_size="10pt"
        pl2.xaxis.axis_label_standoff = 1
        pl2.yaxis.axis_label_standoff = 1
        #pl2.line(transaction_units_cum, transaction_price,color="black",line_width=4)
        #pl2.line(transaction_units_cum, transaction_bprice,color="blue",line_dash=[1, 3],line_width=2)
        #pl2.line(transaction_units_cum, transaction_sprice,color="red",line_dash=[1, 3],line_width=2)
        print("DS_cost_x,DS_cost_list",DS_cost_x,len(DS_cost_list))
        pl2.line(DS_cost_x_db,DS_cost_list_db,color="red",line_width=2)
        pl2.line(DS_value_x_db,DS_value_list_db,color="blue",line_width=2)
        print(DS_value_x)
        pl2.line(DS_index_x,DS_index_y,color="black",line_width=2)

        pl2.line(price_max_x,price_max_y,color="blue",line_width=2)
        pl2.line(price_min_x,price_min_y,color="red",line_width=2)
        Constants.script2, Constants.div2 = components(pl2)

        #sd= SD.objects.get_or_create(id=1)[0]
        Constants.sd_price_max=price_max
        Constants.sd_price_min=price_min
        Constants.sd_units=DS_index
        #sd.save()
        return(Constants.script2, Constants.div2,Constants.sd_price_max,Constants.sd_price_min,Constants.sd_units)

def index(request, group_id, id_in_group):
    print("index called")
    if Constants.stop:
        return request
    context2=index_calculations(group_id, id_in_group)
    context = RequestContext(request, context2)
    return render_to_response('dAuction2/index.html', context_instance = context)


def all_transactions(request,group_id, id_in_group):
    context2=index_calculations(group_id, id_in_group)
    #print("all_trans called!")
    return render(request, 'dAuction2/all_transactions.html', context=context2)


def all_standing_market_offers(request,group_id, id_in_group):
    #print("all_stand called!")
    #print("Connected player group id is:", group_id,)
    #print("Connected player id in group is:", id_in_group,)
    return render(request,'dAuction2/all_standing_market_offers.html',context = context2)


def my_standing_offer(request,group_id, id_in_group):
    context2=index_calculations(group_id, id_in_group)
    #print("my_stand 3333333333333333333333333333!")
    return render(request,'dAuction2/my_standing_offer.html',context= context2)


def refresh(request,group_id, id_in_group):
    context2=index_calculations(group_id, id_in_group)  # index_calculations calculates the up-to-date state

    print("refresh!")
    return render(request,'dAuction2/content_refresh.html',context= context2)

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
    return render(request,'dAuction2/my_standing_offer.html')


def copy_offer(c,p, first):
    # creates a copy of the offer. This one will contain the remaining units
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


def setproducts(c,p,first,first_player):
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


def set_offer(request,group_id, id_in_group,valUnits,valPrice,valType):
    # a player makes an offer. The offer is first created and then checked against the existing offers and matched and cleared if
    # possible
    if Constants.stop:
        return request
    #state = Constants2.objects.get_or_create(id=1)[0]
    #print("state.setOffer_started", state.setOffer_started)
    #print ("state",state)
    if not Constants.setOffer_started:
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
        if id_in_group == 1:
            print("is me, thus render!")
            return render(request,'dAuction2/my_standing_offer2.html', context = context2)
        else:
            print("is not me, no render! Is:",id_in_group)
            return request # DEM: must still be calculated context
    else:
        print("presently a set_offer procedure is running, so no others can be processed:",id_in_group)
        time.sleep(1)
        Constants.setOffer_started=False
        #state.save()
        return request

def set_voucher(p,first_player,first,unitsCleared):
    # first treat the vouchers of the present bidder (p)
    print("BEGIN set_voucher(p,first,unitsCleared):",p,first,unitsCleared)
    #first_player=first.player
    tel_p=Voucher.objects.filter(player=p, used=True).count()
    tel_all_p=Voucher.objects.filter(player=p).count()
    negative_p=35-tel_all_p
    #print ("tel_p",tel_p)
    #print ("tel_all_p",tel_all_p)
    tel_f=Voucher.objects.filter(player=first_player, used=True).count()
    tel_all_f=Voucher.objects.filter(player=first_player).count()
    negative_f=35-tel_all_f

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

        #  treat the vouchers of the counterparty (first.player)
        print("2nd... setvoucher call")
        #ToDo
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
# this creates a transaction. "larger" is the offer with the larger price, "smaller" with the smaller price.
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