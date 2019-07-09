import io
import json
import pickle
import datetime
import random
from decimal import Decimal

from flask import render_template, request, Response, jsonify, session
from flask_login import current_user, login_required
from sqlalchemy import and_, or_
from sqlalchemy.sql.operators import exists

from apps import db, csrf
from apps.seckill.models import Saleproduct, Category, Product, Ziku, Orderitem, Order
from apps.user.models import BlackUser, User
from libs.redis_manager import getcache, setcache, check_request_limit, queuesize, setqueue, update_stock, popqueue
from libs.valicode import get_pyletter, add_text_to_image
from libs.pay import *
from main import app

EXPIREMAXTIME = 6
REQUEST_LIMITMAX = 5


def get_hourlist(product_list):
    hour_list = []
    starthour = None
    if product_list:
        for product in product_list:
            if starthour != product.startdatetime.hour:
                starthour = product.startdatetime.hour
                endhour = int(starthour) + 1
                hours = {'starthour': starthour, 'endhour': endhour}
                hour_list.append(hours)
    return hour_list


@app.route('/')
def index():
    a = current_user

    category_key = 'category'
    category_list = getcache(category_key)
    if category_list:
        category_list = pickle.loads(category_list)
    elif category_list is None:
        category_list = Category.query.all()
        setcache(category_key, 60 * 60, pickle.dumps(category_list))

    product_list_key = 'product_list'
    product_list = getcache(product_list_key)
    if product_list:
        product_list = pickle.loads(product_list)
    elif product_list is None:
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)
        product_list = Saleproduct.query.filter(
            and_(Saleproduct.startdatetime >= today, Saleproduct.startdatetime < tomorrow)
        ).order_by(
            Saleproduct.startdatetime).filter_by(status=1).all()
        setcache(product_list_key, 60 * 60, pickle.dumps(product_list))

    # 构造时间段列表
    hour_list = get_hourlist(product_list)

    return render_template('seckill/index.html', product_list=product_list, hour_list=hour_list,
                           category_list=category_list)


# 分类
@app.route('/category')
def category():
    # /category/?cateid={{cate.id}}
    req = request.values
    cateid = req['cateid'] if 'cateid' in req else ''

    category_key = 'category'
    category_list = getcache(category_key)
    if category_list:
        category_list = pickle.loads(category_list)
    elif category_list is None:
        category_list = Category.query.all()
        setcache(category_key, 60 * 60, pickle.dumps(category_list))

    product_list_key = 'product_list'
    product_list = getcache(product_list_key)
    if product_list:
        product_list = pickle.loads(product_list)
    elif product_list is None:
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)
        product_list = Saleproduct.query.filter(
            and_(Saleproduct.startdatetime >= today, Saleproduct.startdatetime < tomorrow)
        ).order_by(
            Saleproduct.startdatetime).all()
        setcache(product_list_key, 60 * 60, pickle.dumps(product_list))

    product_cate = []
    for product in product_list:
        if product.category_id == int(cateid):
            product_cate.append(product)

    # 构造时间段列表
    hour_list = get_hourlist(product_list)

    return render_template('seckill/index.html', product_list=product_cate, hour_list=hour_list,
                           category_list=category_list)


# 商品详情页显示
@app.route('/detail')
def detail():
    # 初始化标识是否开始秒杀，是否过期失效均为False
    isbegin = False
    isexpire = False
    hasstockqty = True

    req = request.values
    product_id = req['product_id'] if 'product_id' in req else ''
    product_key = 'product_{}'.format(product_id)
    product_detail = getcache(product_key)
    if product_detail:
        product_detail = pickle.loads(product_detail)
    elif product_detail is None:
        product_detail = Saleproduct.query.filter_by(id=product_id).first()
        setcache(product_key, 60 * 10, pickle.dumps(product_detail))

    stock_key = 'stock_{}'.format(product_id)
    stock_qty = getcache(stock_key)
    if stock_qty is None:
        stock_qty = product_detail.stock_total
        setcache(stock_key, 60 * 10, stock_qty)
        hasstockqty = True if int(stock_qty) > 0 else False
    else:
        stock_qty = int(stock_qty.decode())
        if stock_qty > 0:
            hasstockqty = True
        else:
            hasstockqty = False

    # 检查秒杀时间
    nowtime = datetime.datetime.now()
    # 开始时间
    startdatetime = product_detail.startdatetime
    # 结束时间
    enddatetime = product_detail.enddatetime

    diffstarttime = nowtime - startdatetime
    # 失效期
    expiretime = nowtime.hour - enddatetime.hour
    # if datetime.strptime(product_detail[0].startdatetime, "%Y-%m-%d %H:%M:%S")>nowtime:
    if diffstarttime.days >= 0 and expiretime <= EXPIREMAXTIME:
        isbegin = True  # 开始
    elif diffstarttime.days < 0:
        isbegin = False  # 还未开始
    elif expiretime > EXPIREMAXTIME:  # 超过6小时间失效
        isexpire = True  # 过期

    return render_template('seckill/productdetail.html', product_detail=product_detail, stock_qty=stock_qty,
                           isbegin=isbegin, isexpire=isexpire, hasstockqty=hasstockqty)


@app.route('/set_check')
@login_required
def set_check():
    # 附机从Ziku取出一问题和答案，如无答案，则产生答案，并保存到数据库及redis缓存中
    totalcount = Ziku.query.filter().count()
    i = random.randint(1, totalcount)
    ziku = Ziku.query.filter_by(id=i).first()
    if ziku:
        answer = ziku.answer
        if not answer:
            answer = get_pyletter(ziku.qustion)
            ziku.answer = answer
            ziku.save()

        session['answer'] = answer
        # python2.7
        # mstream = StringIO.StringIO()
        # python3.5
        mstream = io.BytesIO()
        txt = ziku.qustion + '拼音首字母是'
        img = add_text_to_image(txt)
        img.save(mstream, "png")
    return Response(response=mstream.getvalue(), status=200, mimetype='image/png')


# 实时库存
@app.route('/getstock', methods=['POST'])
@login_required
def getstock():
    req = json.loads(request.data)
    product_id = req['product_id'] if 'product_id' in req else ''
    stock_key = 'stock_{}'.format(product_id)
    stock_qty = getcache(stock_key)
    if stock_qty:
        if int(stock_qty) > 0:
            hasstockqty = True
        else:
            hasstockqty = False
    else:
        stock_qty = 0
        hasstockqty = False
    return jsonify({"hasstockqty": hasstockqty, "stock_qty": int(stock_qty)})


@app.route('/search')
def search():
    req = request.values
    searchq = req['searchq'] if 'searchq' in req else ''
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    # 分类数据
    category_list = Category.query.all()
    if searchq:
        searchq = '%' + searchq + '%'
        product_list = Saleproduct.query.filter(Saleproduct.title.like(searchq)).filter(
            and_(Saleproduct.startdatetime >= today, Saleproduct.startdatetime < tomorrow)
        ).order_by(
            Saleproduct.startdatetime).filter_by(status=1).all()
        # product_list = Saleproduct.query.filter(
        #     and_(Saleproduct.title.containts(searchq), Saleproduct.startdatetime >= today,
        #          Saleproduct.startdatetime < tomorrow)).order_by(
        #     Saleproduct.startdatetime).filter_by(status=1).all()
    else:
        product_list = Saleproduct.query.filter(
            and_(Saleproduct.startdatetime >= today, Saleproduct.startdatetime < tomorrow)
        ).order_by(
            Saleproduct.startdatetime).filter_by(status=1).all()
    # 构造时间段列表
    hour_list = get_hourlist(product_list)
    # if product_list:
    #     hour_list = []
    #     starthour = 0
    #     for product in product_list:
    #         if starthour != product.startdatetime.hour:
    #             starthour = product.startdatetime.hour
    #             endhour = int(starthour) + 1
    #             hours = {'starthour': starthour, 'endhour': endhour}
    #             hour_list.append(hours)
    return render_template('seckill/index.html', hour_list=hour_list, product_list=product_list,
                           category_list=category_list)


@app.route('/secaddcart', methods=['POST'])
@login_required
def secaddcart():
    '''
    1、验证码检查
    2、检查黑名单
    3、从缓存中取秒杀商品信息
    4、检查提交时间是否在有效时间内
    5、防刷，一分钟内不能超过5次请求
    6、检查队列大小超过库存数，则直接将访问转移
    7、秒杀修改库存
    8、生成订单、修改数据库库存
    '''
    resp = {"status": 200, "msg": '生成订单', "orderid": -1}
    req = request.values
    product_id = req['product_id'] if 'product_id' in req else ''
    quantity = req['amount'] if 'amount' in req else ''
    answer = req['answer'] if 'answer' in req else ''
    posttime = datetime.datetime.now()
    user_id = int(current_user.id)
    isjoin = Orderitem.query.filter(and_(Orderitem.product_id == product_id, Orderitem.user_id == user_id)).first()

    if isjoin:
        resp['msg'] = '已参与！不能再参加'
        resp['status'] = 300
        return jsonify(resp)

    if answer.upper() != session['answer'].upper():
        resp['msg'] = '验证码不正确'
        resp['status'] = 300
        return jsonify(resp)

    check_blackuser = BlackUser.query.filter_by(user_id=user_id).first()
    if check_blackuser:
        resp['msg'] = '系统忙！请重试'
        resp['status'] = 300
        return jsonify(resp)

    # 从缓存中取秒杀商品信息
    procut_key = 'procut_{}'.format(product_id)
    product_detail = getcache(procut_key)
    if product_detail:
        # 对取出的值进行转化，pickle.loads取出值 对象化
        product_detail = pickle.loads(product_detail)
    elif product_detail is None:
        # 如无值，从数据库取值
        product_detail = Saleproduct.query.filter_by(id=product_id).first()
        # pickle.dumps将list对象序列化后保存到redis缓存
        product_detail_to = pickle.dumps(product_detail)
        setcache(procut_key, 60 * 5, product_detail_to)

    # 检查提交时间是否在有效时间内
    # 开始时间
    startdatetime = product_detail.startdatetime
    # 结束时间
    enddatetime = product_detail.enddatetime
    diffstarttime = posttime - startdatetime
    diffendtime = enddatetime - posttime
    expiretime = posttime.hour - enddatetime.hour
    # 时间验证，提交的时间必须在开始时间和6小时之内
    if not diffstarttime.days >= 0 and expiretime < EXPIREMAXTIME:
        resp['msg'] = '时间不正确'
        resp['status'] = 300
        return jsonify(resp)

    # 防刷，一分钟内不能超过5次请求
    ua_key = 'user_{}'.format(user_id)
    if not check_request_limit(ua_key, REQUEST_LIMITMAX):
        resp['msg'] = '请求次数超过{}次'.format(REQUEST_LIMITMAX)
        resp['status'] = 300
        return jsonify(resp)

    # 保存秒杀商品库存key
    key_stock = 'stock_{}'.format(product_id)
    # 定义队列key：queue_procut_key = queue_product_2
    queue_procut_key = 'queue_' + procut_key
    # 取出当时缓存库存
    stock_qty = int(getcache(key_stock))

    if stock_qty is None:
        resp['msg'] = '请刷新页面再重试！'
        resp['status'] = 300
        return jsonify(resp)

    # 检查队列大小，如不符合，则不进队列
    total_quesize = queuesize(queue_procut_key)
    # 假如检查队列大小超过库存数，则直接将访问转移
    if total_quesize > 2 * stock_qty:
        resp['msg'] = '系统忙！请重试'
        resp['status'] = 300
        return jsonify(resp)

    # 入队列排队
    setqueue(queue_procut_key, user_id)
    price = product_detail.price
    if not update_stock(key_stock, product_id, user_id, quantity, price):
        resp['msg'] = '库存不足'
        resp['status'] = 300
        popqueue(queue_procut_key)
        print(resp['msg'], user_id)
        return jsonify(resp)

    popqueue(queue_procut_key)

    amount = Decimal(int(quantity) * price)
    profile = User.query.filter_by(id=user_id).first()
    product = Saleproduct.query.filter_by(id=product_id).first()

    order = Order()
    order.user_id = user_id
    order.status = '2'
    order.amount = amount
    order.name = product.title
    order.email = profile.email
    order.mobile = profile.email
    order.address = '南京市江宁区'
    db.session.add(order)
    db.session.flush()

    orderitem = Orderitem()
    orderitem.order_id = order.id
    orderitem.product_id = product_id
    orderitem.price = price
    orderitem.quantity = quantity
    db.session.add(orderitem)

    # 更改库存
    stock_qty = getcache(key_stock)
    product.stock_total = stock_qty
    db.session.add(product)
    db.session.commit()

    resp['msg'] = '生成订单'
    resp['status'] = 200
    resp['orderid'] = order.id
    return jsonify(resp)


@app.route('/paychoice/')
@login_required
def paychoice():
    req = request.values
    order_id = req['order_id'] if 'order_id' in req else ''
    order = Order.query.filter_by(id=order_id).first()
    return render_template('pay/pay.html', order=order)


@app.route('/paying', methods=['POST'])
@login_required
def paying():
    resp = {'result': "", 'msg': "", 'url': ''}
    req = request.values
    try:
        order_id = req['order_id'] if 'order_id' in req else ''
        pay_type = int(req['pay_type'] if 'pay_type' in req else '')
        pay_amount = Decimal(req['pay_amount'] if 'pay_amount' in req else '')
    except ValueError:
        resp['result'] = "failed"
        resp['msg'] = "参数错误，请求支付失败"
        return jsonify(resp)

    result_src = ""
    order = Order.query.filter_by(id=order_id).first()
    realpayamount = order.amount

    # 判断支付金额是否一致
    if pay_amount != realpayamount or pay_amount <= 0:
        resp['result'] = "failed"
        resp['msg'] = "参数错误，请求支付失败"
        return jsonify(resp)

    user_id = current_user.id
    # subject = '秒杀商品:' + order.get_productname[0]
    subject = '秒杀商品:'
    if order.status != '2':
        resp['result'] = "failed"
        resp['msg'] = "参数错误，请求支付失败"
        return jsonify(resp)

    try:
        if pay_type == 1:
            # 微信支付
            # result_src = paying_for_weixin_pay(request,order_id,user_id ,realpayamount)

            r = p.QRPay(out_trade_no=order_id, total_fee=TOTAL_FEE, body=BODY, attach=order.name)
            result_src = r.qrcode
            # result_src = paying_code_weixin_pay(order_id, user_id)
            print('result_src is: ', result_src)
            url = "/wxpaying?order_id=" + str(r.payjs_order_id) + "&amount=" + str(
                realpayamount) + "&result_src=" + result_src
            resp['result'] = "success"
            resp['msg'] = "请求微信支付页面成功!"
            resp['url'] = url

            return jsonify(resp)

        elif pay_type == 2:
            # 支付宝即时到帐支付
            url = alipay_trade_page_pay(order_id, subject, realpayamount)
            return JsonResponse({'result': "success", 'msg': u"请求支付宝支付页面成功!", 'url': url})
    except Exception as e:
        logger.info(e)
        return JsonResponse({'result': "failed", 'msg': u"订单信息异常,不能支付!", 'url': ''})


#
# # 微信支付,生成支付二维码 ,模式二,先生成预支付单,根据返回的code_url生成二维码
# def paying_code_weixin_pay(orderid, user_id):
#     """
#     微信支付,生成支付二维码
#     :param orderid:
#     :param user_id:
#     :return:    """
#
#     # 定义变量
#     result_src = ""  # 存储路径
#     newresult_src = ""  # 访问的路径
#     try:
#         # 生成预支付单
#         str_url = getcode_url(orderid)
#         # app_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#         # media_path = os.path.join(app_path, 'media')
#         media_path = settings.MEDIA_ROOT
#         if str_url:
#             img = qrcode.make(str_url)
#             curDateTime = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
#             randNum = random.randint(1000, 9999)
#             mch_vno = curDateTime + str(randNum) + str(orderid)
#             # path = settings.MEDIA_ROOT + 'qrcode'
#             path = os.path.join(media_path, 'qrcode')
#             logger.info(path)
#             if not os.path.exists(path):
#                 os.makedirs(path)
#             result_src = os.path.join(path, mch_vno + ".png")
#             logger.info(result_src)
#             # newresult_src = settings.MEDIA_URL + os.path.join('qrcode', mch_vno + ".png")
#             newresult_src = os.path.join(settings.MEDIA_URL, os.path.join('qrcode', mch_vno + ".png"))
#             img.save(result_src)
#         else:
#             return u'订单不存在'
#     except Exception as e:
#         logger.info(e)
#     return newresult_src
#
#
# # 微信支付,生成预支付单,并返回code_url
# def getcode_url(orderid):
#     try:
#         unifiedorder_pub = UnifiedOrder_pub()
#
#         corder = Order.objects.get(id=int(orderid))
#         total_fee = 0
#         if corder:
#             total_fee = corder.amount * 100  # 实际支付金额,微信需以整数,单位为分
#             # body = corder.get_productname[0]
#             body = 'seckill'
#             if len(body) > 127:
#                 body = body[0:127]
#
#             unifiedorder_pub.setParameter("body", body)
#             out_trade_no = create_TradeId(orderid)
#             unifiedorder_pub.setParameter("out_trade_no", out_trade_no)
#             unifiedorder_pub.setParameter("detail", body)
#             # unifiedorder_pub.setParameter("total_fee", str(total_fee))
#             unifiedorder_pub.setParameter("total_fee", "1")
#             unifiedorder_pub.setParameter("trade_type", "NATIVE")
#             # 生成预支付单
#             prepay_id, url = unifiedorder_pub.getPrepayId()
#             # print url
#             if url:
#                 return url
#     except Exception as e:
#         logger.info(e)
#         return False
#
#
# 微信支付,显示支付二维码页面
@app.route('/wxpaying/')
@login_required
def paying_for_weixin_pay():
    """
    微信支付,生成支付二维码
    :param orderid:
    :param user_id:
    :return:    """

    # 定义变量
    result_src = ""  # 存储路径
    newresult_src = ""  # 访问的路径
    resp = {'result': "success", 'msg': "", 'url': ''}
    req = request.values
    try:
        resp_kwd = {
            "order_id": int(req['order_id']) if 'order_id' in req else '',
            "newresult_src": req['result_src'] if 'result_src' in req else '',
            "pay_amount": req['amount'] if 'amount' in req else '',
            "orderid": req['order_id'] if 'order_id' in req else '',
            "buy_title": '秒杀商品:'
        }

    # newresult_src = settings.MEDIA_URL + result_src

    except Exception as e:
        print(e)
        # logger.info(e)

    # return newresult_src
    return render_template('pay/wxpay.html', **resp_kwd)


@app.route('/pay_check')
@login_required
def pay_check():
    resp = {'status': "200", 'msg': "已支付",'type':'1'}
    req = request.values
    order_id = req['order_id'] if 'order_id' in req else ''
    s = p.check_status(payjs_order_id=order_id)

    if s and s.paid:
        return jsonify(resp)

    resp['status'] = '400'
    resp['msg'] = '未支付'
    return jsonify(resp)


@app.route('/paysuccessed/')
@login_required
def paysuccess():
    resp = {'status': "200", 'msg': "已支付"}
    req = request.values
    order_id = req['order_id'] if 'order_id' in req else ''
    s = p.check_status(payjs_order_id=order_id)
    msg = s.attach
    return render_template('pay/payordersuccess.html',msg=msg, order_id=order_id)

@app.route('/orderlist')
@login_required
def orderlist():
    orderlist = Order.query.filter_by(user_id=current_user.id).all()
    return render_template('orders/orderlist.html',orderlist=orderlist)

@app.route('/ceshi', methods=['get', 'post'])
@csrf.exempt
def ceshi():
    # Settings.query.filter_by(db.exists().where(Settings.guildid==guildid)).one()
    # session['ceshi'] = ceshi
    #
    # print(session['ceshi'])
    # check_blackuser = BlackUser.query.filter_by(user_id=1).first()
    print("进入了回调函数")
    return '123'
