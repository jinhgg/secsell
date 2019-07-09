from datetime import datetime

from flask_login import UserMixin
from sqlalchemy import Column, DECIMAL, DateTime, ForeignKey, String
from sqlalchemy.dialects.mysql import INTEGER, LONGTEXT, TINYINT
from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash

from apps import db, login_manager
from apps.user.models import User


class Category(db.Model):
    __tablename__ = 'category'

    id = Column(INTEGER(11), primary_key=True)
    name = Column(String(200))
    slug = Column(String(200), nullable=False, unique=True)
    created = Column(DateTime)
    updated = Column(DateTime)
    status = Column(String(1), nullable=False, index=True)



class Supplier(db.Model):
    __tablename__ = 'supplier'

    id = Column(INTEGER(11), primary_key=True)
    name = Column(String(200))
    phone = Column(String(50))
    linkman = Column(String(200))
    desc = Column(String(800))
    kind = Column(String(2), nullable=False, index=True)
    brands = Column(String(50))
    image = Column(String(100), nullable=False)
    created = Column(DateTime)
    updated = Column(DateTime)
    status = Column(String(1), nullable=False, index=True)


class Ziku(db.Model):
    __tablename__ = 'ziku'

    id = Column(INTEGER(11), primary_key=True)
    qustion = Column(String(200))
    answer = Column(String(200))





class Order(db.Model):
    __tablename__ = 'order'

    id = Column(INTEGER(11), primary_key=True)
    name = Column(String(50), nullable=False)
    address = Column(String(250))
    email = Column(String(254))
    postal_code = Column(String(20))
    city = Column(String(100))
    mobile = Column(String(20))
    user_id = Column(INTEGER(11))
    created = Column(DateTime,default=datetime.now)
    updated = Column(DateTime,default=datetime.now)
    status = Column(String(1))
    amount = Column(DECIMAL(5, 2))
    coupon = Column(String(20))
    discount = Column(INTEGER(11))
    reply_dump = Column(String(500))
    reference_number = Column(String(20))


class Product(db.Model):
    __tablename__ = 'product'

    id = Column(INTEGER(11), primary_key=True)
    name = Column(String(200), nullable=False, unique=True)
    slug = Column(String(200), index=True)
    description = Column(LONGTEXT, nullable=False)
    productno = Column(String(200), index=True)
    image = Column(String(100), nullable=False)
    largeimage = Column(String(100), nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    saleprice = Column(DECIMAL(10, 2))
    stock = Column(INTEGER(10), nullable=False)
    available = Column(TINYINT(1), nullable=False)
    created = Column(DateTime)
    updated = Column(DateTime)
    remark = Column(String(400))
    category_id = Column(INTEGER(10), nullable=False, index=True)
    supplier_id = Column(INTEGER(10), index=True)



class Saleproduct(db.Model):
    __tablename__ = 'saleproducts'

    id = Column(INTEGER(11), primary_key=True)
    title = Column(String(200))
    status = Column(String(1))
    marketprice = Column(DECIMAL(10, 2), nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    startdatetime = Column(DateTime, nullable=False)
    enddatetime = Column(DateTime, nullable=False)
    stock_total = Column(INTEGER(11), nullable=False)
    remain_qty = Column(INTEGER(11), nullable=False)
    desc = Column(LONGTEXT, nullable=False)
    image = Column(String(100), nullable=False)
    protduct_id = Column(INTEGER(10), index=True)
    category_id = Column(INTEGER(10), index=True)



class Orderitem(db.Model):
    __tablename__ = 'orderitem'

    id = Column(INTEGER(11), primary_key=True)
    order_id = Column(INTEGER(10), nullable=False, index=True)
    user_id = Column(INTEGER(10), nullable=False, index=True)
    product_id = Column(INTEGER(10), nullable=False, index=True)
    price = Column(DECIMAL(10, 2), nullable=False)
    quantity = Column(INTEGER(10), nullable=False)

