__author__ = 'MSIS'


from dAuction2.models import Player, Group, Offer, Transaction, Voucher,Constants,Constants2, SD
import random, string
from functools import reduce
from django.db.models import Avg,Sum
from bokeh.plotting import figure, output_file, show
#from bokeh.resources import CDN
from bokeh.embed import components

from dAuction2.functions_mature import *


def createPlayer(g, id_in_group,role):
    print("BEGIN createPlayer (g, id_in_group,role):",g, id_in_group,role)# DEM
    # create a player in group #g (object), with #number id_in_group (an integer) and
    # with role #role (#role=="PR" for PRoducer or #role=="RE" for REtailer)
    # Values for the #vouchers are assigned (they are the cost of producing for Producers
    # and the earnings for Retailers).
    # The marginal values are random with, for Retailers, average #r_average and standard deviation
    # r_sd and, for Producers, average #p_average and standard deviation
    # p_sd


    r_average=10
    r_sd=20
    r_start=1000
    r_max=60
    r_min=0

    p_average=.01
    p_sd=.5
    p_max=30
    p_min=0

    p = Player.objects.get_or_create(group=g,id_in_group=id_in_group)[0]
        # creates a player or retrieves him
    #print("CREATEPLAYER!!! for:",p)
    p.codename = ''.join([random.choice(string.ascii_uppercase) for n in range(1)] +[random.choice(string.digits) for n in range(1)])
    p.codeurl=Constants.baseurl+p.codename
        # creates the codename and the url for the player to use

    p.role=role
    print ("role",role)
        # assigns the role for the player
    p.money=10000
        # assigns some starting money to a player - NOT USED YET

    if role=="RE":
        p.name="value"
        # else it is by default "cost" - this is used for printing on the page in the templates
    p.save()
    value2=[]
    value2_cumm=[]
    valPR=0
    valRE=r_start
    random.seed()
    if role=="PR":
        for i in range(35):
            valPR+=abs(myround(random.gauss(i*i*i*p_average, (i*i*p_sd))))
            valPR=min(valPR,1200)
            value2.append(valPR)
                # creates a list with marginal values. The values are strictly increasing and convex
                # with a maximum of 1200. This construction avoids needing to sort.
            value2_cumm=cummulator(value2)
                # #value2_cumm has the cummulative valuesof value2
    elif role=="RE":
        for i in range(35):
            #value2.append(int(max(0,round(random.gauss(r_average, r_sd),-1))))  #is good, but slow
            #valRE=max(0,valRE - round(random.randint(r_min, r_max),-1))
            valRE=max(0,valRE - abs(myround(random.gauss(r_average, r_sd))))
            value2.append(valRE)
                # creates a list with marginal values. The values are strictly increasing and convex
                # with a maximum of 1200. This construction avoids needing to sort.
            value2_cumm=cummulator(value2)
                # #value2_cumm has the cummulative valuesof value2

    for i in range(35):
        v = Voucher(idd=i+1,value_cum=value2_cumm[i],value=value2[i],player=p,group=p.group,role=role)
        v.save()
        # only here all the vouchers are created, using the values put in the variables #value2 and #value2_cumm
    print("END createPlayer (g, id_in_group,role):",g, id_in_group,role)# DEM
    return p


def index_calculations(group_idd, id_in_group):
    # In this procedure all the calculations are done that are necessary to now the state of the auction
    # how many transactions have been done, how many offers are out.
    # Note: NO offers are cleared in this procedure.

    print("BEGIN index_calculations")
    group_id=int(group_idd)
    id_in_group=int(id_in_group)
    # we need to check if there are player objects already
    g=getGroup(1)
    p=getPlayer(g,id_in_group)
    # ToDo: distinguis between the groups in the queries
    trans_list2 = Transaction.objects.filter(group=p.group).order_by('-id')
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

        print("id_include",id_include)
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


    player_list = Player.objects.filter(id_in_group__lt=99).order_by('id')

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




    voucher_list = Voucher.objects.filter(player=p).order_by('idd')
    print("voucher_list ",voucher_list )
    myOffers2= offer_listST3.filter(player=p).order_by('-id')

    myOffersCL= myOffers2.filter(cleared=True)
    myOffersCL_inv=myOffersCL.order_by('id')
    myOffersST= myOffers2.filter(cleared=False)
    lastOfferST = myOffersST.first()



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

    print("transaction_units_cum, transaction_price",transaction_units_cum, transaction_price)
    print("transaction_units_cum, transaction_bprice",transaction_units_cum, transaction_bprice)
    print("transaction_units_cum, transaction_sprice",transaction_units_cum, transaction_sprice)
    print("xsell_cumSTdb, sell_priceSTdb",xsell_cumSTdb, sell_priceSTdb)
    print("xbuy_cumSTdb, buy_priceSTdb",xbuy_cumSTdb, buy_priceSTdb)

    print("script, div " )
    script, div = components(pl)
    #print("script, div ",script, div )

    print(Constants)
    if Constants.show_theory:
        Constants.script2, Constants.div2,Constants.sd_price_max,Constants.sd_price_min,Constants.sd_units=D_S_analysis()


    print("context2")


    context2 =  {"Constants":Constants,"player_list":player_list,"units_produced":units_produced,
                 "average_price_last10transactions":average_price_last10transactions,"median_price_last10transactions":median_price_last10transactions,
                 "units":units,"average_price":average_price,"median_price":median_price,"vouchers":voucher_list, "player":p,"group":g,"id_in_group": id_in_group,"group_id": group_id,
                 "script": script, "div": div
        ,'combo_offers': combo_offerST,'combo_offers2':standing_marketST, 'buy_offers': buy_listST
        ,'sell_offers': sell_listST,'myOffers': myOffersCL,'myOffers_inv':myOffersCL_inv,'myOffersST': myOffersST,'lastOffer': lastOfferST,'players': player_list
        ,'offers':offer_listST, 'transactions': trans_list2}
    print("END index_calculations")
    return context2


def D_S_analysis():
    # calculate D-S analyzis
    # ONLY NEEDS TO BE DONE ONCE - SHOULD BE MOVED SOMEWHERE
    print("def D_S_analysis()  CALLED ........................................................")
    #g=getGroup(group_id)
    #p=getPlayer(g, id_in_group)
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
#        relevantVouchers=Voucher.objects.filter(player=p).filter(idd__gt=0).filter(value__lte=price_max)
#        Constants.my_cost_th = relevantVouchers.aggregate(Sum('value'))["value__sum"]
#        Constants.my_profit_th=relevantVouchers.last().idd * price_max - Constants.my_cost_th
#        print("Constants.my_profit_th",Constants.my_profit_th)
#        print("Constants.my_cost_th",Constants.my_cost_th)
#        print("price_max",price_max)
#        Constants.my_score= round((p.profit / Constants.my_profit_th) * 100)
        #############################



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