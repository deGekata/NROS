"""
Module contains SQLAlchemy-based ORM
"""
from myapp import db


class Tag(db.Model):  # pylint: disable=too-few-public-methods
    """ Class that contains Tag"""
    id = db.Column(db.Integer, primary_key=True)
    minimum = db.Column(db.Integer)
    capacity = db.Column(db.Integer)
    user_token = db.Column(db.String, db.ForeignKey('user.token'))
    sell_price = db.Column(db.Integer)
    fullness = db.Column(db.Integer)
    point_id = db.Column(db.String, db.ForeignKey('point.id'))
    product_type_id = db.Column(db.String, db.ForeignKey('product_type.id'))


class ProductType(db.Model):  # pylint: disable=too-few-public-methods
    """ Class that contains Product Type. """
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String(100))
    price = db.Column(db.Integer)
    seasonality = db.Column(db.Integer)
    lstms = db.relationship('LSTM', backref='product_type', lazy='dynamic')
    user_token = db.Column(db.String, db.ForeignKey('user.token'))
    tags = db.relationship('Tag', backref='product_type', lazy='dynamic')


class Point(db.Model):  # pylint: disable=too-few-public-methods
    """ Class that contains RetailStore or Storage """
    id = db.Column(db.String, primary_key=True)
    address = db.Column(db.String(100))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    tags = db.relationship('Tag', backref='point', lazy='dynamic')
    lstms = db.relationship('LSTM', backref='point', lazy='dynamic')
    sales = db.relationship('Sale', backref='shop', lazy='dynamic')
    user_token = db.Column(db.String, db.ForeignKey('user.token'))


class User(db.Model):  # pylint: disable=too-few-public-methods
    """ Class that contains User."""
    id = db.Column(db.Integer, primary_key=True)
    moysklad_id = db.Column(db.String, unique=True)
    moysklad_login = db.Column(db.String)
    moysklad_password = db.Column(db.String)
    name = db.Column(db.String)
    password_hash = db.Column(db.String)
    email = db.Column(db.String)
    privilege_level = db.Column(db.Integer)
    token = db.Column(db.String, unique=True)
    sales = db.relationship("Sale", backref='user', lazy='dynamic')
    tags = db.relationship("Tag", backref='user', lazy='dynamic')
    points = db.relationship("Point", backref='user', lazy='dynamic')
    product_types = db.relationship(
        "ProductType", backref='user', lazy='dynamic')
    lstms = db.relationship("LSTM", backref='user', lazy='dynamic')


class Sale(db.Model):  # pylint: disable=too-few-public-methods
    """ Class that contains ProductItem Sale """
    id = db.Column(db.String, primary_key=True)
    date = db.Column(db.DateTime)
    point_id = db.Column(db.String, db.ForeignKey('point.id'))
    count = db.Column(db.Integer)
    product_type_id = db.Column(db.String, db.ForeignKey('product_type.id'))
    price = db.Column(db.Integer)
    user_token = db.Column(db.String, db.ForeignKey('user.token'))


class LSTM(db.Model):  # pylint: disable=too-few-public-methods
    """ Class that contains LSTM."""
    id = db.Column(db.Integer, primary_key=True)
    point_id = db.Column(db.String, db.ForeignKey('point.id'))
    product_type_id = db.Column(db.String, db.ForeignKey('product_type.id'))
    alpha = db.Column(db.Float)
    beta = db.Column(db.Float)
    gamma = db.Column(db.Float)
    model = db.Column(db.PickleType)
    scope = db.Column(db.PickleType)
    prediction = db.Column(db.Integer)
    before_range = db.Column(db.Integer)
    lstm_pred = db.Column(db.Integer)
    listForvector = db.Column(db.ARRAY(db.Integer))
    realSpros = db.Column(db.ARRAY(db.Integer))
    user_token = db.Column(db.String, db.ForeignKey('user.token'))
