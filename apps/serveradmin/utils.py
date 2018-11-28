
from apps.order.models import Order
from utils.exceptions import PubErrorCustom

def matchdata_get():
    match1 = list(Order.objects.raw(
        """
            SELECT t1.*,t3.mobile
            FROM `order` as t1
            INNER JOIN `matchpool` as t2 ON t1.ordercode = t2.ordercode
            INNER JOIN `user` as t3 ON t1.userid=t3.userid and t3.status='0'
            WHERE t2.trantype=0 and t2.flag=0 order by t1.amount
        """
    ))

    match2 = list(Order.objects.raw(
        """
            SELECT t1.*,t3.mobile
            FROM `order` as t1
            INNER JOIN `matchpool` as t2 ON t1.ordercode = t2.ordercode
            INNER JOIN `user` as t3 ON t1.userid=t3.userid and t3.status='0'
            WHERE t2.trantype=1 and t2.flag=0  and t1.umark=0 order by t1.amount
        """
    ))
    match1 = list(match1)
    match2 = list(match2)
    return {"match1":match1,'match2':match2}

def matchcheck(res):
    match1=res['match1']
    match2=res['match2']

    for item in match1:
        for item1 in match2:
            if item.userid == item1.userid:
                raise PubErrorCustom("用户[%s]不能匹配自己" % (item.username))

    sum1 = 0
    sum2 = 0
    mobiles=list()
    for item in match1:
        sum1 += item.amount
        mobiles.append(item.mobile)
    for item in match2:
        sum2 += item.amount
        mobiles.append(item.mobile)

    if sum1 != sum2:
        raise PubErrorCustom("金额不匹配！")

    if sum1 == 0 or sum2 == 0:
        raise PubErrorCustom('无匹配对象')

    return mobiles

def matchexchange(res):
    match1=res['match1']
    match2=res['match2']
    tgbz_obj = dict()
    jsbz_obj = dict()
    tgbz_split=dict()
    jsbz_split=dict()
    for item in match1:
        try:
            order=Order.objects.get(ordercode=item.ordercode)
        except Order.DoesNotExist:
            raise PubErrorCustom("订单号[%d]不存在!" % (item.ordercode))

        tgbz_obj[item.ordercode] ={
                'amount': item.amount,
                'obj': item,
                'install_obj': order
        }
        tgbz_split[item.ordercode]={'userid':item.userid,'username':item.username,'orders':[]}

    for item in match2:
        try:
            order=Order.objects.get(ordercode=item.ordercode)
        except Order.DoesNotExist:
            raise PubErrorCustom("订单号[%d]不存在!" % (item.ordercode))

        jsbz_obj[item.ordercode] ={
                'amount': item.amount,
                'obj': item,
                'install_obj': order
        }
        jsbz_split[item.ordercode] = {'userid':item.userid,'username':item.username,'orders':[]}

    return tgbz_obj,jsbz_obj,tgbz_split,jsbz_split

def match_install(install,install1,amount,t):

    install_res=Order()

    install_res.trantype=install.trantype
    install_res.subtrantype=install.subtrantype
    install_res.amount=amount
    install_res.userid=install.userid
    install_res.username=install.username
    install_res.userid_to=install1.userid
    install_res.username_to=install1.username
    install_res.ordercode_to=install1.ordercode
    install_res.status=1
    install_res.confirmtime=install.confirmtime
    install_res.matchtime = t
    install_res.createtime = install.createtime
    install_res.img = install.img
    install_res.umark = install.umark
    install_res.save()
    return install_res

def match_eq_handle(tgbz_obj,jsbz_obj,t,tgbz_split,jsbz_split):

    orderinstall=list()
    diff_orders=list()
    res=None
    res_to=None
    for ordercode in tgbz_obj:
        for ordercode_to in jsbz_obj:
            if tgbz_obj[ordercode]['amount'] == jsbz_obj[ordercode_to]['amount'] and jsbz_obj[ordercode_to]['obj'].ordercode not in diff_orders:

                if tgbz_obj[ordercode]['obj'].amount != tgbz_obj[ordercode]['amount']:
                    res=match_install(tgbz_obj[ordercode]['install_obj'], jsbz_obj[ordercode_to]['obj'], jsbz_obj[ordercode_to]['amount'],t)
                    tgbz_split[tgbz_obj[ordercode]['install_obj'].ordercode]['orders'].append(res.ordercode)

                if jsbz_obj[ordercode_to]['obj'].amount != jsbz_obj[ordercode_to]['amount']:
                    res_to=match_install(jsbz_obj[ordercode_to]['install_obj'], tgbz_obj[ordercode]['obj'], tgbz_obj[ordercode]['amount'],t)
                    jsbz_split[jsbz_obj[ordercode_to]['install_obj'].ordercode]['orders'].append(res_to.ordercode)

                if res and res_to:
                    res_to.ordercode_to = res.ordercode
                    res_to.save()
                    res.ordercode_to = res_to.ordercode
                    res.save()
                    res = None
                    res_to = None
                elif res:
                    jsbz_obj[ordercode_to]['install_obj'].userid_to=res.userid
                    jsbz_obj[ordercode_to]['install_obj'].username_to = res.username
                    jsbz_obj[ordercode_to]['install_obj'].ordercode_to = res.ordercode
                    jsbz_obj[ordercode_to]['install_obj'].matchtime = t
                    jsbz_obj[ordercode_to]['install_obj'].status = 1
                    orderinstall.append(jsbz_obj[ordercode_to]['install_obj'])
                    jsbz_obj[ordercode_to]['install_obj'].save()
                    res=None
                elif res_to:
                    tgbz_obj[ordercode]['install_obj'].userid_to = res_to.userid
                    tgbz_obj[ordercode]['install_obj'].username_to = res_to.username
                    tgbz_obj[ordercode]['install_obj'].ordercode_to = res_to.ordercode
                    tgbz_obj[ordercode]['install_obj'].status = 1
                    tgbz_obj[ordercode]['install_obj'].matchtime=t
                    orderinstall.append(tgbz_obj[ordercode]['install_obj'])
                    tgbz_obj[ordercode]['install_obj'].save()
                else:
                    tgbz_obj[ordercode]['install_obj'].userid_to = jsbz_obj[ordercode_to]['obj'].userid
                    tgbz_obj[ordercode]['install_obj'].username_to = jsbz_obj[ordercode_to]['obj'].username
                    tgbz_obj[ordercode]['install_obj'].ordercode_to = jsbz_obj[ordercode_to]['obj'].ordercode
                    tgbz_obj[ordercode]['install_obj'].status = 1
                    tgbz_obj[ordercode]['install_obj'].matchtime=t
                    orderinstall.append(tgbz_obj[ordercode]['install_obj'])
                    tgbz_obj[ordercode]['install_obj'].save()

                    jsbz_obj[ordercode_to]['install_obj'].userid_to=tgbz_obj[ordercode]['obj'].userid
                    jsbz_obj[ordercode_to]['install_obj'].username_to = tgbz_obj[ordercode]['obj'].username
                    jsbz_obj[ordercode_to]['install_obj'].ordercode_to = tgbz_obj[ordercode]['obj'].ordercode
                    jsbz_obj[ordercode_to]['install_obj'].matchtime = t
                    jsbz_obj[ordercode_to]['install_obj'].status = 1
                    orderinstall.append(jsbz_obj[ordercode_to]['install_obj'])
                    jsbz_obj[ordercode_to]['install_obj'].save()

                diff_orders.append(tgbz_obj[ordercode]['obj'].ordercode)
                diff_orders.append(jsbz_obj[ordercode_to]['obj'].ordercode)
                break

    r_tgbz_obj=dict()
    r_jsbz_obj=dict()
    for ordercode in tgbz_obj:
        if ordercode not in diff_orders:
            r_tgbz_obj[ordercode]={
                    'amount': tgbz_obj[ordercode]['amount'],
                    'obj': tgbz_obj[ordercode]['obj'],
                    'install_obj':tgbz_obj[ordercode]['install_obj']
                }

    for ordercode in jsbz_obj:
        if ordercode not in diff_orders:
            r_jsbz_obj[ordercode]={
                    'amount': jsbz_obj[ordercode]['amount'],
                    'obj': jsbz_obj[ordercode]['obj'],
                    'install_obj': jsbz_obj[ordercode]['install_obj']
                }
    return r_tgbz_obj,r_jsbz_obj,orderinstall,tgbz_split,jsbz_split

def match_core_handle_ex(tgbz_obj,jsbz_obj,t,tgbz_split,jsbz_split):
    tgbz=list()
    jsbz=list()
    orderinstall=list()
    diff_orders = list()

    for item  in tgbz_obj:
        tgbz.append(tgbz_obj[item])
    for item in jsbz_obj:
        jsbz.append(jsbz_obj[item])

    res=None
    res_to=None

    index=0
    while True:
        tgbz_obj = tgbz[index] if len(tgbz) - 1 >= index else None
        jsbz_obj = jsbz[index] if len(jsbz) - 1 >= index else None
        index+=1

        if not tgbz_obj or not jsbz_obj:
            break

        amount1 = tgbz_obj['amount']
        amount2 = jsbz_obj['amount']

        amount=amount1-amount2
        if amount<0:
            amount=amount*-1
            if tgbz_obj['obj'].amount != tgbz_obj['amount']:
                res = match_install(tgbz_obj['install_obj'], jsbz_obj['obj'], tgbz_obj['amount'], t)
                tgbz_split[tgbz_obj['install_obj'].ordercode]['orders'].append(res.ordercode)

            if jsbz_obj['obj'].amount != jsbz_obj['amount']:
                res_to = match_install(jsbz_obj['install_obj'], tgbz_obj['obj'], amount1, t)
                jsbz_split[jsbz_obj['install_obj'].ordercode]['orders'].append(res_to.ordercode)

            if res_to and res:
                res_to.ordercode_to=res.ordercode
                res_to.save()
                res.ordercode_to=res_to.ordercode
                res.save()
                res=None
                res_to=None
            elif res_to:
                tgbz_obj['install_obj'].userid_to = res_to.userid
                tgbz_obj['install_obj'].username_to = res_to.username
                tgbz_obj['install_obj'].ordercode_to = res_to.ordercode
                tgbz_obj['install_obj'].matchtime = t
                tgbz_obj['install_obj'].status = 1
                orderinstall.append(tgbz_obj['install_obj'])
                tgbz_obj['install_obj'].save()
                res_to = None

            elif res:
                jsbz_obj['install_obj'].userid_to = res.userid
                jsbz_obj['install_obj'].username_to = res.username
                jsbz_obj['install_obj'].ordercode_to = res.ordercode
                jsbz_obj['install_obj'].status = 1
                jsbz_obj['install_obj'].matchtime = t
                jsbz_obj['install_obj'].amount = amount1
                orderinstall.append(jsbz_obj['install_obj'])
                jsbz_obj['install_obj'].save()
                res = None

                jsbz_split[jsbz_obj['install_obj'].ordercode]['orders'].append(jsbz_obj['install_obj'].ordercode)
            else:
                tgbz_obj['install_obj'].userid_to = jsbz_obj['install_obj'].userid
                tgbz_obj['install_obj'].username_to = jsbz_obj['install_obj'].username
                tgbz_obj['install_obj'].ordercode_to = jsbz_obj['install_obj'].ordercode
                tgbz_obj['install_obj'].matchtime = t
                tgbz_obj['install_obj'].status = 1
                orderinstall.append(tgbz_obj['install_obj'])
                tgbz_obj['install_obj'].save()

                jsbz_obj['install_obj'].userid_to = tgbz_obj['install_obj'].userid
                jsbz_obj['install_obj'].username_to = tgbz_obj['install_obj'].username
                jsbz_obj['install_obj'].ordercode_to = tgbz_obj['install_obj'].ordercode
                jsbz_obj['install_obj'].status = 1
                jsbz_obj['install_obj'].matchtime = t
                jsbz_obj['install_obj'].amount = amount1
                orderinstall.append(jsbz_obj['install_obj'])
                jsbz_obj['install_obj'].save()

                jsbz_split[jsbz_obj['install_obj'].ordercode]['orders'].append(jsbz_obj['install_obj'].ordercode)

            jsbz_obj['amount'] = amount

            diff_orders.append(tgbz_obj['obj'].ordercode)
        else:
            if tgbz_obj['obj'].amount != tgbz_obj['amount']:
                res = match_install(tgbz_obj['install_obj'], jsbz_obj['obj'], amount2, t)
                tgbz_split[tgbz_obj['install_obj'].ordercode]['orders'].append(res.ordercode)

            if jsbz_obj['obj'].amount != jsbz_obj['amount']:
                res_to = match_install(jsbz_obj['install_obj'], tgbz_obj['obj'], jsbz_obj['amount'], t)
                jsbz_split[jsbz_obj['install_obj'].ordercode]['orders'].append(res_to.ordercode)


            if res_to and res:
                res_to.ordercode_to = res.ordercode
                res_to.save()
                res.ordercode_to = res_to.ordercode
                res.save()
                res = None
                res_to = None
            elif res_to:
                tgbz_obj['install_obj'].userid_to = res_to.userid
                tgbz_obj['install_obj'].username_to = res_to.username
                tgbz_obj['install_obj'].ordercode_to = res_to.ordercode
                tgbz_obj['install_obj'].matchtime = t
                tgbz_obj['install_obj'].status = 1
                tgbz_obj['install_obj'].amount = amount2
                orderinstall.append(tgbz_obj['install_obj'])
                tgbz_obj['install_obj'].save()
                res_to = None

                tgbz_split[tgbz_obj['install_obj'].ordercode]['orders'].append(tgbz_obj['install_obj'].ordercode)
            elif res:
                jsbz_obj['install_obj'].userid_to = res.userid
                jsbz_obj['install_obj'].username_to = res.username
                jsbz_obj['install_obj'].ordercode_to = res.ordercode
                jsbz_obj['install_obj'].status = 1
                jsbz_obj['install_obj'].matchtime = t
                orderinstall.append(jsbz_obj['install_obj'])
                jsbz_obj['install_obj'].save()
                res = None

            else:
                tgbz_obj['install_obj'].userid_to = jsbz_obj['install_obj'].userid
                tgbz_obj['install_obj'].username_to = jsbz_obj['install_obj'].username
                tgbz_obj['install_obj'].ordercode_to = jsbz_obj['install_obj'].ordercode
                tgbz_obj['install_obj'].matchtime = t
                tgbz_obj['install_obj'].status = 1
                tgbz_obj['install_obj'].amount = amount2
                orderinstall.append(tgbz_obj['install_obj'])
                tgbz_obj['install_obj'].save()

                tgbz_split[tgbz_obj['install_obj'].ordercode]['orders'].append(tgbz_obj['install_obj'].ordercode)

                jsbz_obj['install_obj'].userid_to = tgbz_obj['install_obj'].userid
                jsbz_obj['install_obj'].username_to = tgbz_obj['install_obj'].username
                jsbz_obj['install_obj'].ordercode_to = tgbz_obj['install_obj'].ordercode
                jsbz_obj['install_obj'].status = 1
                jsbz_obj['install_obj'].matchtime = t
                orderinstall.append(jsbz_obj['install_obj'])
                jsbz_obj['install_obj'].save()

            tgbz_obj['amount'] = amount

            diff_orders.append(jsbz_obj['obj'].ordercode)

    r_tgbz_obj=dict()
    r_jsbz_obj=dict()
    for item in tgbz:
        if item['obj'].ordercode not in diff_orders :
            r_tgbz_obj[item['obj'].ordercode]={
                'amount': item['amount'],
                'obj': item['obj'],
                'install_obj':item['install_obj']
            }
    for item in jsbz:
        if item['obj'].ordercode not in diff_orders:
            r_jsbz_obj[item['obj'].ordercode]={
                'amount': item['amount'],
                'obj': item['obj'],
                'install_obj': item['install_obj']
            }
    return r_tgbz_obj,r_jsbz_obj,orderinstall,tgbz_split,jsbz_split

def match_core_handle(tgbz_obj,jsbz_obj,t,tgbz_split,jsbz_split):
    install_order = list()

    while len(tgbz_obj) and len(jsbz_obj):
        tgbz_obj, jsbz_obj, tmp_install ,tgbz_split,jsbz_split = match_eq_handle(tgbz_obj, jsbz_obj, t,tgbz_split,jsbz_split)
        for item in tmp_install:
            install_order.append(item)

        tgbz_obj, jsbz_obj, tmp_install ,tgbz_split,jsbz_split = match_core_handle_ex(tgbz_obj, jsbz_obj, t,tgbz_split,jsbz_split)
        for item in tmp_install:
            install_order.append(item)

    if len(tgbz_obj) or len(jsbz_obj):
        raise PubErrorCustom("系统错误!")

    return install_order,tgbz_split,jsbz_split

def match_split(tgbz_split,jsbz_split):
    from apps.order.models import Tranlist
    for ordercode in tgbz_split:
        if len(tgbz_split[ordercode]['orders'])>0:
            tranname = '订单拆分['
            for item in tgbz_split[ordercode]['orders']:
                tranname += "%s," % str(item)
            tranname += ']'
            Tranlist.objects.create(**{
                'trantype': 24,
                'tranname': tranname,
                'userid': tgbz_split[ordercode]['userid'],
                'username': tgbz_split[ordercode]['username'],
                'ordercode': ordercode
            })
    for ordercode in jsbz_split:
        if len(jsbz_split[ordercode]['orders'])>0:
            tranname = '订单拆分['
            for item in jsbz_split[ordercode]['orders']:
                tranname += "%s," % str(item)
            tranname += ']'
            Tranlist.objects.create(**{
                'trantype': 24,
                'tranname': tranname,
                'userid': jsbz_split[ordercode]['userid'],
                'username': jsbz_split[ordercode]['username'],
                'ordercode': ordercode
            })

def match_upd_db(install_orders):
    for item in install_orders:
        item.save()

def match_smssend(mobile_list):
    if mobile_list and len(mobile_list):
        from apps.public.utils import smssend
        smssend(mobile=list(set(mobile_list)), flag=1)