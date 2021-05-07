""" Module that routes api requests """  # pylint: disable=too-many-lines
import hashlib
import pickle
from functools import wraps

import keras
import keras.backend.tensorflow_backend as tb

import requests
from flask import request, abort
from flask_restful import Resource

import utils
from myapp import api
from myapp.__init__ import db
from myapp.consts import Consts
from myapp.models import ProductType, Point, LSTM, Sale, User, Tag
from myapp.utils import Utils

# for python 3.6
from datetime import date, datetime, time
from backports.datetime_fromisoformat import MonkeyPatch
MonkeyPatch.patch_fromisoformat()

def json_type(product_type):
    """Function converts product_type object into dictionary
    :param product_type: (ProductType) Product Type object
    :return dict: dictionary containing converted Product Type
    """
    return {'id': product_type.id, 'name': product_type.name,
            'price': product_type.price,
            'seasonality': product_type.seasonality}


def create_type(query, user_token):
    """ Function creates Product Type from query.
        :param query: (dict) Example: { name:"milk",
                                        price:1000,
                                        seasonality: 0
                                      }
        :return ProductType: Product Type object
    """
    return ProductType(name=query['name'], price=query['price'],
                       seasonality=query['seasonality'], user_token=user_token)


def create_type_with_id(query, product_type_id, user_token):
    """ Function creates Product Type with id from query.
            :param query: (dict) Example: { name:"milk",
                                            price:1000,
                                            seasonality: 0,
                                          }
            :param product_type_id: (int)
            :return ProductType: Product Type object
        """
    return ProductType(
        id=product_type_id,
        name=query['name'],
        price=query['price'],
        seasonality=query['seasonality'],
        user_token=user_token)


def json_point(point):
    """ Function converts Point object into dictionary
        :param point: (Point) Point object
        :return dict: dictionary containing converted Point
        """
    return {'id': point.id, 'address': point.address, 'latitude': point.latitude,
            'logitude': point.longitude}  # , 'latitude':point.latitude, 'longitude': point.longitude}


def create_point(query, user_token):
    """ Function creates Point from query.
        :param query: (dict) Example: { address: "Moscow" }
        :return Point: Point object
    """
    return Point(address=query['address'], user_token=user_token)  # , latitude = query['latitude'], longitude = query['longitude'])


def create_point_with_id(query, point_id, user_token):
    """ Function creates Shop with id from query.
        :param query: (dict) Example: { address: "Moscow" }
        :param shop_id: (int)
        :return Shop: Shop object
    """
    return Point(id=point_id, address=query['address'], user_token=user_token)  # , latitude = query['latitude'], longitude = query['longitude'])


def json_lstm(lstm):
    """ Function converts LSTM object into dictionary
        :param lstm: (LSTM) LSTM object
        :return dict: dictionary containing converted LSTM
        """
    return {
        'id': lstm.id,
        'point_id': lstm.point_id,
        'product_type_id': lstm.product_type_id,
        'alpha': lstm.alpha,
        'beta': lstm.beta,
        'gamma': lstm.gamma,
        'prediction': lstm.prediction,
        'before_range': lstm.before_range,
        'lstm_pred': lstm.lstm_pred,
        'listForvector': lstm.listForvector,
        'realSpros': lstm.realSpros}


def create_lstm(query, user_token):
    """ Function creates LSTM from query.
        :param query: (dict) Example: { shop_id: 1,
                                        product_type_id: 1,
                                        alpha: 0.1,
                                        beta: 0.1,
                                        gamma: 0.1
                                      }
        :return LSTM: LSTM object
    """
    before_range = None
    slen = None
    model_id = None
    data = db.engine.execute(
        '''
    with dates as (
        select generate_series(
            (select min(date) from sale), (select max(date) from sale), '1 day'::interval
        ) as date
    )
    select
        dates.date,
        coalesce(sum(sale.count), 0)
        from dates
        left join sale
            on date_part('day', sale.date) = date_part('day', dates.date)
            and date_part('month', sale.date) = date_part('month', dates.date)
            and date_part('year', sale.date) = date_part('year', dates.date)
            and sale.point_id = '{0}'
            and sale.product_type_id = '{1}'
            and sale.user_token = '{2}'
        group by 1 order by 1 desc
    '''.format(query['point_id'], query['product_type_id'], user_token)).fetchall()  # and product_item.product_type_id = {1} and sale.product_item_id = product_item.id
    print(data)
    if len(data) >= 2:
        if keras.__version__ != '2.2.5':
            tb._SYMBOLIC_SCOPE.value = True

        model = LSTM.query.filter(LSTM.point_id == str(query['point_id']), LSTM.product_type_id == str(query['product_type_id']), LSTM.user_token == str(user_token)).first()  # +user_id
        if model is None:
            slen = int(ProductType.query.filter(ProductType.id == str(query['product_type_id'])).first().seasonality)  # ,ProductType.user_token == str(user_token)
        else:
            slen = int(model.product_type.seasonality)
            before_range = int(model.before_range)
            model_id = model.id
        if 'before_range' in query:
            if before_range != query['before_range']:
                model = None
                before_range = int(query['before_range'])
        alpha, beta, gamma, model, scaler, prediction, before_range, lstm_prediciton = utils.trainModelsAndPredict(
            data, before_range + 1, model, slen)  # +1
        step_g = 15

        if alpha == -1:
            steps = db.engine.execute(
                '''
            with dates as (
                select generate_series(
                    (select min(date) from sale), (select max(date) from sale), '1 day'::interval
                ) as date
            )
            select
                dates.date,
                coalesce(sum(sale.count), 0)
                from dates
                left join sale
                    on date_part('day', sale.date) = date_part('day', dates.date)
                    and date_part('month', sale.date) = date_part('month', dates.date)
                    and date_part('year', sale.date) = date_part('year', dates.date)
                    and sale.point_id = '{0}'
                    and sale.product_type_id = '{1}'
                    and sale.user_token = '{2}'
                group by 1 order by 1 desc limit {3}
            '''.format(query['point_id'], query['product_type_id'], user_token, step_g + 3 if step_g >= before_range else before_range + 3)).fetchall()
            cont_res = utils.predict_step(
                steps,
                before_range=before_range + 1,
                scaler=scaler,
                model=model)
            spros, list_forvector, real_spros = lstm_prediciton, cont_res[0], cont_res[1]
        else:
            steps = db.engine.execute('''
            with dates as (
                select generate_series(
                    (select min(date) from sale), (select max(date) from sale), '1 day'::interval
                ) as date
            )
            select
                dates.date,
                coalesce(sum(sale.count), 0)
                from dates
                left join sale
                    on date_part('day', sale.date) = date_part('day', dates.date)
                    and date_part('month', sale.date) = date_part('month', dates.date)
                    and date_part('year', sale.date) = date_part('year', dates.date)
                    and sale.point_id = '{0}'
                    and sale.product_type_id = '{1}'
                    and sale.user_token = '{2}'
                group by 1 order by 1 desc limit {3}
            '''.format(query['point_id'], query['product_type_id'], user_token, 367)).fetchall()
            res_r = utils.predictWinters(
                [row[1] for row in steps], alpha, beta, gamma, slen, step_g)
            spros, list_forvector, real_spros = prediction, res_r[0], res_r[1]

        # print(spros,listForvector,realSpros,before_range,lstm_prediciton,a,b,g)
        return LSTM(
            id=model_id,
            point_id=query['point_id'],
            product_type_id=query['product_type_id'],
            alpha=alpha,
            beta=beta,
            gamma=gamma,
            model=pickle.dumps(model),
            scope=pickle.dumps(scaler),
            prediction=prediction,
            lstm_pred=lstm_prediciton,
            before_range=before_range,
            listForvector=list_forvector,
            realSpros=real_spros,
            user_token=user_token)
    else:
        return ''

def create_lstm_with_id(query, lstm_id, user_token):
    """ Function creates LSTM with id from query.
        :param query: (dict) Example: { shop_id: 1,
                                        product_type_id: 1,
                                        alpha: 0.1,
                                        beta: 0.1,
                                        gamma: 0.1
                                      }
        :param lstm_id: (int)
        :return LSTM: LSTM object
    """
    before_range = None
    slen = None
    data = db.engine.execute('''
    with dates as (
        select generate_series(
            (select min(date) from sale), (select max(date) from sale), '1 day'::interval
        ) as date
    )
    select
        dates.date,
        coalesce(sum(sale.count), 0)
        from dates
        left join sale
            on date_part('day', sale.date) = date_part('day', dates.date)
            and date_part('month', sale.date) = date_part('month', dates.date)
            and date_part('year', sale.date) = date_part('year', dates.date)
            and sale.point_id = {0}
            and sale.product_type_id = {1}
            and sale.user_token = {2}
        group by 1 order by 1 desc
    '''.format(query['point_id'], query[
        'product_type_id'],user_token)).fetchall()  # and product_item.product_type_id = {1} and sale.product_item_id = product_item.id
    if len(data) >= 2:
        if keras.__version__ != '2.2.5':
            tb._SYMBOLIC_SCOPE.value = True

        model = LSTM.query.filter(LSTM.point_id == str(query['point_id']), LSTM.product_type_id == str(query['product_type_id']), LSTM.user_token == str(user_token)).first()  # +user_id
        if model is None:
            slen = int(ProductType.query.filter(ProductType.id == str(query['product_type_id'])).first().seasonality)  # ,ProductType.user_token == str(user_token)
        else:
            slen = int(model.product_type.seasonality)
            before_range = int(model.before_range)
            model_id = model.id
        if 'before_range' in query:
            if before_range != query['before_range']:
                model = None
                before_range = int(query['before_range'])
        alpha, beta, gamma, model, scaler, prediction, before_range, lstm_prediciton = utils.trainModelsAndPredict(
            data, before_range + 1, model, slen)  # +1
        step_g = 15

        if alpha == -1:
            steps = db.engine.execute('''
            with dates as (
                select generate_series(
                    (select min(date) from sale), (select max(date) from sale), '1 day'::interval
                ) as date
            )
            select
                dates.date,
                coalesce(sum(sale.count), 0)
                from dates
                left join sale
                    on date_part('day', sale.date) = date_part('day', dates.date)
                    and date_part('month', sale.date) = date_part('month', dates.date)
                    and date_part('year', sale.date) = date_part('year', dates.date)
                    and sale.point_id = {0}
                    and sale.product_type_id = {1}
                    and sale.user_token = {2}
                group by 1 order by 1 desc limit {3}
            '''.format(query['point_id'], query['product_type_id'], user_token,
                    step_g + 3 if step_g >= before_range else before_range + 3)).fetchall()
            cont_res = utils.predict_step(steps, before_range=before_range + 1, scaler=scaler, model=model)
            spros, list_forvector, real_spros = lstm_prediciton, cont_res[0], cont_res[1]
        else:
            steps = db.engine.execute('''
            with dates as (
                select generate_series(
                    (select min(date) from sale), (select max(date) from sale), '1 day'::interval
                ) as date
            )
            select
                dates.date,
                coalesce(sum(sale.count), 0)
                from dates
                left join sale
                    on date_part('day', sale.date) = date_part('day', dates.date)
                    and date_part('month', sale.date) = date_part('month', dates.date)
                    and date_part('year', sale.date) = date_part('year', dates.date)
                    and sale.point_id = {0}
                    and sale.product_type_id = {1}
                    and sale.user_token = {2}
                group by 1 order by 1 desc limit {3}
            '''.format(query['point_id'], query['product_type_id'],user_token, 367)).fetchall()
            res_r = utils.predictWinters([row[1] for row in steps], alpha, beta, gamma, slen, step_g)
            spros, list_forvector, real_spros = prediction, res_r[0], res_r[1]

        # print(spros,listForvector,realSpros)
        return LSTM(id=lstm_id, point_id=query['point_id'], product_type_id=query[
            'product_type_id'], alpha=alpha, beta=beta,
                    gamma=gamma, model=pickle.dumps(model), scope=pickle.dumps(scaler), prediction=prediction,
                    lstm_pred=lstm_prediciton, before_range=before_range,
                    listForvector=list_forvector, realSpros=real_spros, user_token=user_token)
    else:
        return ''

def json_sale(sale):
    """ Function converts Sale object into dictionary
        :param sale: (Sale) Sale object
        :return dict: dictionary containing converted Sale
    """
    return {
        'id': sale.id,
        'date': str(
            sale.date),
        'count': sale.count,
        'point_id': sale.point_id,
        'product_type_id': sale.product_type_id}


def create_sale(query, user_token):
    """ Function creates Sale from query.
        :param query: (dict) Example: { date: '2011-11-04 00:05:23',
                                        product_item_id: 10,
                                        shop_id: 20 }
        :return Sale: Sale object
    """
    return Sale(
        date=datetime.fromisoformat(
            query['date']),
        product_type_id=query['product_type_id'],
        point_id=query['point_id'],
        count=query['count'],
        user_token=user_token)


def create_sale_with_id(query, sale_id, user_token):
    """ Function creates Sale with id from query.
        :param query: (dict) Example: { date: '2011-11-04 00:05:23',
                                        product_item_id: 10,
                                        shop_id: 20 }
        :param sale_id: (int)
        :return Sale: Sale object
    """
    return Sale(
        id=sale_id,
        date=datetime.fromisoformat(
            query['date']),
        product_type_id=query['product_type_id'],
        point_id=query['point_id'],
        count=query['count'],
        user_token=user_token)


def json_prediction(prediction):
    """ Function converts Prediction into dictionary
        :param prediction: list[][]
        :return dict: dictionary containing converted prediction
    """
    return {
        'f1': prediction[0][0],
        'f2': prediction[0][1],
        'war_c': int(prediction[1][0]),
        'shop_c': int(prediction[1][1]),
        'war_id': Point.query.filter(Point.id == prediction[2][0]).first().address,
        'shop_id': Point.query.filter(Point.id == prediction[2][1]).first().address,
    }


def make_prediction(query, user_token):
    """ Function that creates prediction
        :param TODO
        :return list[][]: predictions list
    """
    if keras.__version__ != '2.2.5':
        tb._SYMBOLIC_SCOPE.value = True

    models = LSTM.query.filter(
        LSTM.product_type_id == query['product_type_id'],
        LSTM.user_token == user_token).all()  # пока всё
    if len(models) >= 2:
        full = []
        for i in models:
            shop = Tag.query.filter(
                Tag.user_token == user_token,
                Tag.point_id == i.point_id,
                Tag.product_type_id == query['product_type_id']).first()
            if shop is not None:
                full.append({'spros': i.lstm_pred if i.alpha == -1 else i.prediction,
                             # Point.query.filter(Point.id == i.point_id).first(),
                             'shop': shop,
                             'listForvector': i.listForvector, 'realSpros': i.realSpros})
        print(full)
        return utils.main_prediction(full)
    return ''


def create_user(name, email, password_hash, token, privilege_level=1):
    """ Function creates User from query.
        :param name: (string)
        :param email: (string)
        :param password_hash: (string)
        :param privilege_level: (int)
        :param token: (string)
    """
    return User(
        name=name,
        email=email,
        password_hash=password_hash,
        privilege_level=privilege_level,
        token=token)


def json_tag(tag):
    """ Function converts Tag object into dictionary
        :param tag: (Tag) Tag object
        :return dict: dictionary containing converted Tag
    """
    return {
        'id': tag.id,
        'minimum': tag.minimum,
        'capacity': tag.capacity,
        'fullness': tag.fullness,
        'sell_price': tag.sell_price,
        'user_token': tag.user_token}


def create_tag(query, user_token):
    """ Function creates Tag from query.
        :param query: (dict) Example: {
                                          "minimum": 10,
                                          "capacity": 200
                                          "fullness": 10
                                      }
        :return Tag: Tag object
    """
    return Tag(
        minimum=query['minimum'],
        capacity=query['capacity'],
        fullness=query['fullness'],
        sell_price=query['sell_price'],
        user_token=user_token,
        point_id=query['point_id'],
        product_type_id=query['product_type_id'])


def create_tag_with_id(query, tag_id, user_token):
    """ Function creates Tag with id from query.
        :param query: (dict) Example: {
                                          "minimum": 10,
                                          "capacity": 50,
                                          "fullness": 10
                                      }
        :param tag_id: (int)
        :return Tag: Tag object
    """
    return Tag(
        id=tag_id,
        minimum=query['minimum'],
        capacity=query['capacity'],
        fullness=query['fullness'],
        sell_price=query['sell_price'],
        user_token=user_token,
        point_id=query['point_id'],
        product_type_id=query['product_type_id'])


def require_authentication(func):
    """ Annotation requires token

        @require_api_token
        def sample_method(user):
            return {"Hey, " + user.name + ", you are authenticated!"}

    """

    @wraps(func)
    def check_token(*args, **kwargs):
        user = None

        if 'Authorization' not in request.headers:
            invalid_token = True
        else:
            token = request.headers['Authorization']
            user = User.query.filter(User.token == token).first()
            invalid_token = user is None

        if invalid_token:
            return {"message": "Invalid token."}, 999

        return func(*args, **kwargs, user=user)

    return check_token


class ListProductTypesApi(Resource):
    """ Class that gets all Product Types or creates new """

    @staticmethod
    @require_authentication
    def get(user):
        """ Method used to get list of all Product Types
            :return: list[ProductType]
        """

        product_types = ProductType.query.filter(ProductType.user_token == user.token).all()
        return {'product_types': [json_type(product_type) for product_type in product_types]}, 200

    @staticmethod
    @require_authentication
    def post(user):
        """ Create new Product Type
            Example product type post query:
            {
                "count": 0,
                "name": "Salt",
                "price": 10,
                "seasonality": 0
            }
            :return: jsonifyed ProductType
        """
        if not request.json:
            abort(400, "No data")
        product_type = create_type(request.json, user.token)
        db.session.add(product_type)
        db.session.commit()
        return {'product_type': json_type(product_type)}, 201


class ProductTypesApi(Resource):
    """ Class that gets/updates/deletes Product Type by id """

    @staticmethod
    def get(product_type_id):
        """ Get Product Type by id
            :param product_type_id: (int)
            :return ProductType: Product Type object
        """
        product_type = ProductType.query.get_or_404(product_type_id)
        return {'product_type': json_type(product_type)}, 200

    @staticmethod
    def delete(product_type_id):
        """ Deletes Product Type by id
            :param product_type_id: (int)
            :return: empty html
        """
        product_type = ProductType.query.get_or_404(product_type_id)
        db.session.delete(product_type)
        db.session.commit()
        return "", 200

    @staticmethod
    @require_authentication
    def put(product_type_id, user):
        """ Update/Create Product Type by id
            :param product_type_id: (int)
            :return: ProductType: Product Type object
        """
        if not request.json:
            abort(400, "No data")
        product_type = ProductType.query.get_or_404(product_type_id)
        if request.json['name'] is not None:
            product_type.name=request.json['name']
        if request.json['price'] is not None:
            product_type.price=request.json['price']
        if request.json['seasonality'] is not None:
            product_type.seasonality=request.json['seasonality']
        db.session.add(product_type)
        db.session.commit()
        return {'product_type': json_type(product_type)}, 201


class ListPointsApi(Resource):
    """ Class that gets all Shops or creates new """

    @staticmethod
    @require_authentication
    def get(user):
        """ Method used to get list of all Shops
            :return: list[Shop]
        """
        points = Point.query.filter(Point.user_token == user.token).all()
        return {'points': [json_point(points) for points in points]}, 200

    @staticmethod
    @require_authentication
    def post(user):
        """ Create new Shop
            Example shop post query:
            {
                "address": "Moscow"
            }
            :return: jsonifyed Shop
        """
        if not request.json:
            abort(400, "No data")
        point = create_point(request.json, user.token)
        db.session.add(point)
        db.session.commit()
        return {'point': json_point(point)}, 200


class PointApi(Resource):
    """ Class that gets/updates/deletes Point by id """

    @staticmethod
    def get(point_id):
        """ Get Shop by id
            :param shop_id: (int)
            :return Shop: Shop object
        """
        point = Point.query.get_or_404(point_id)
        return {'shop': json_point(point)}, 200

    @staticmethod
    def delete(point_id):
        """ Deletes Shop by id
            :param shop_id: (int)
            :return: empty html
        """
        point = Point.query.get_or_404(point_id)
        db.session.delete(point)
        db.session.commit()
        return "", 200

    @staticmethod
    @require_authentication
    def put(point_id, user):
        """ Update/Create Shop by id
            :param shop_id: (int)
            :return: Shop: Shop object
        """
        if not request.json:
            abort(400, "No data")
        point = Point.query.get_or_404(point_id)
        if request.json['latitude'] is not None:
            point.latitude=request.json['latitude']
        if request.json['longitude'] is not None:
            point.longitude=request.json['longitude']
        if request.json['address'] is not None:
            point.address=request.json['address']
        db.session.add(point)
        db.session.commit()
        return {'point': json_point(point)}, 201


class ListLSTMsApi(Resource):
    """ Class that gets all LSTMs or creates new """

    @staticmethod
    @require_authentication
    def get(user):
        """ Method used to get list of all LSTMs
            :return: list[LSTM]
        """
        lstms = LSTM.query.filter(LSTM.user_token == user.token).all()
        return {'LSTMs': [json_lstm(lstm) for lstm in lstms]}, 200

    @staticmethod
    @require_authentication
    def post(user):
        """ Create new LSTM
            Example LSTM post query:
            {
                "shop_id": 1,
                "product_type_id": 1
                "alpha": 0.1,
                "beta": 0.1,
                "gamma": 0.1
            }
            :return: jsonifyed LSTM
        """
        if not request.json:
            abort(400, "No data")
        lstm = create_lstm(request.json, user.token)
        if lstm == '':
            return lstm, 409
        if lstm.id is not None:
            db.session.delete(LSTM.query.get_or_404(lstm.id))
            db.session.commit()
        db.session.add(lstm)
        db.session.commit()
        return {'lstm': json_lstm(lstm)}, 200

class TrainAllLSTMS(Resource):
    """ Class for training all LSTMs """

    @staticmethod
    @require_authentication
    def post(user):
        """ Method used to train all LSTMs """
        if (not request.json) or (request.json['product_type_id'] is None):
            abort(400, "No data")
        lstms = []
        for point in Point.query.filter(Point.user_token == user.token):
            lstm = create_lstm({'point_id': point.id, 'before_range': 2, 'product_type_id': request.json['product_type_id']}, user.token)
            if lstm != 409:
                if lstm.id is not None:
                    db.session.delete(LSTM.query.get_or_404(lstm.id))
                    db.session.commit()
                lstms.append(lstm)
                db.session.add(lstm)
                db.session.commit()
                
        return {'LSTMs': [json_lstm(lstm) for lstm in lstms]}, 200

class LSTMApi(Resource):
    """ Class that gets/updates/deletes LSTM by id """

    @staticmethod
    def get(lstm_id):
        """ Get LSTM by id
            :param lstm_id: (int)
            :return LSTM: LSTM object
        """
        lstm = LSTM.query.get_or_404(lstm_id)
        return {'lstm': json_lstm(lstm)}, 200

    @staticmethod
    def delete(lstm_id):
        """ Deletes LSTM by id
            :param lstm_id: (int)
            :return: empty html
        """
        lstm = LSTM.query.get_or_404(lstm_id)
        db.session.delete(lstm)
        db.session.commit()
        return "", 200

    @staticmethod
    @require_authentication
    def put(lstm_id, user):
        """ Update/Create LSTM by id
            :param lstm_id: (int)
            :return: LSTM: LSTM object
        """
        if not request.json:
            abort(400, "No data")
        lstm = LSTM.query.get_or_404(lstm_id)
        if request.json['before_range'] is not None:
            lstm.before_range=request.json['before_range']
        db.session.add(lstm)
        db.session.commit()
        return {'lstm': json_lstm(lstm)}, 201


class ListSalesApi(Resource):
    """ Class that gets all Sales or creates new """

    @staticmethod
    @require_authentication
    def get(user):
        """ Method used to get list of all Sales
            :return: list[Sale]
        """
        sales = Sale.query.filter(Sale.user_token == user.token).all()
        return {'sales': [json_sale(sales) for sales in sales]}, 200

    @staticmethod
    @require_authentication
    def post(user):
        """ Create new Sale
            Example sale post query:
            {
                "date": "2011-11-04 00:05:23",
                "product_item_id": 10,
                "shop_id": 20
            }
            :return: jsonifyed Sale
        """
        if not request.json:
            abort(400, "No data")
        sale = create_sale(request.json, user.token)
        db.session.add(sale)
        db.session.commit()
        print(sale)
        return {'sale': json_sale(sale)}, 200


class SaleApi(Resource):
    """ Class that gets/updates/deletes Sale by id """

    @staticmethod
    def get(sale_id):
        """ Get Sale by id
            :param sale_id: (int)
            :return Sale: Sale object
        """
        sale = Sale.query.get_or_404(sale_id)
        return {'sale': json_sale(sale)}, 200

    @staticmethod
    def delete(sale_id):
        """ Deletes Sale by id
            :param sale_id: (int)
            :return: empty html
        """
        sale = Sale.query.get_or_404(sale_id)
        db.session.delete(sale)
        db.session.commit()
        return "", 200

    @staticmethod
    @require_authentication
    def put(sale_id, user):
        """ Update/Create Sale by id
            :param sale_id: (int)
            :return: Sale: Sale object
        """
        if not request.json:
            abort(400, "No data")
        sale = Sale.query.get_or_404(sale_id)
        if request.json['date'] is not None:
            sale.date=request.json['date']
        if request.json['price'] is not None:
            sale.price=request.json['price']
        if request.json['count'] is not None:
            sale.count=request.json['count']
        db.session.add(sale)
        db.session.commit()
        return {'sale': json_sale(sale)}, 201


class PredictApi(Resource):
    """ Class that make predictions """

    @staticmethod
    @require_authentication
    def post(user):
        print("a"*10, request.json)
        """ Method used to get list of all Sales
            :return: list[Sale]
        """
        predictions = make_prediction(request.json, user.token)
        if predictions == '':
            return predictions, 409
        print(predictions)
        return {'target_id': request.json['product_type_id'] ,'predictions': [json_prediction(prediction) for prediction in predictions]}, 200


class ListTagsApi(Resource):
    """ Class that gets all Tags or creates new """

    @staticmethod
    @require_authentication
    def get(user):
        """ Method used to get list of all Tags
            :return: list[Tag]
        """

        tags = Tag.query.filter(Tag.user_token == user.token).all()
        return {'tags': [json_tag(tag) for tag in tags]}, 200

    @staticmethod
    @require_authentication
    def post(user):
        """ Create new Tag
            Example tag post query:
            {
                "minimum": 10,
                "capacity": 200
            }
            :return: jsonifyed Tag
        """
        if not request.json:
            abort(400, "No data")
        tag = create_tag(request.json, user.token)
        db.session.add(tag)
        db.session.commit()
        return {'tag': json_tag(tag)}, 201

    @staticmethod
    @require_authentication
    def put(user):
        """ Update/Create Tag by id
            :param tag_id: (int)
            :return: Tag: Tag object
        """
        if not request.json:
            abort(400, "No data")
        tag = Tag.query.filter(Tag.point_id == request.json['point_id'], Tag.product_type_id == request.json['product_type_id'], Tag.user_token == user.token).first()
        if tag is None:
            abort(404, "Not found")
        if request.json['minimum'] is not None:
            tag.minimum=request.json['minimum']
        if request.json['capacity'] is not None:
            tag.capacity=request.json['capacity']
        if request.json['sell_price'] is not None:
            tag.sell_price=request.json['sell_price']
        if request.json['fullness'] is not None:
            tag.fullness=request.json['fullness']
        db.session.add(tag)
        db.session.commit()
        return {'tag': json_tag(tag)}, 201


class TagsApi(Resource):
    """ Class that gets/updates/deletes Tags by id """

    @staticmethod
    def get(tag_id):
        """ Get Tags by id
            :param tag_id: (int)
            :return Tags: Tag object
        """
        tag = Tag.query.get_or_404(tag_id)
        return {'tag': json_tag(tag)}, 200

    @staticmethod
    def delete(tag_id):
        """ Deletes Tag by id
            :param tag_id: (int)
            :return: empty html
        """
        tag = Tag.query.get_or_404(tag_id)
        db.session.delete(tag)
        db.session.commit()
        return "", 200

    @staticmethod
    @require_authentication
    def put(tag_id, user):
        """ Update/Create Tag by id
            :param tag_id: (int)
            :return: Tag: Tag object
        """
        if not request.json:
            abort(400, "No data")
        tag = Tag.query.get_or_404(tag_id)
        if request.json['minimum'] is not None:
            tag.minimum=request.json['minimum']
        if request.json['capacity'] is not None:
            tag.capacity=request.json['capacity']
        if request.json['sell_price'] is not None:
            tag.sell_price=request.json['sell_price']
        if request.json['fullness'] is not None:
            tag.fullness=request.json['fullness']
        db.session.add(tag)
        db.session.commit()
        return {'tag': json_tag(tag)}, 201


class AuthenticationApi(Resource):
    """ Class that allows to authenticate (sign in && sign up) """

    @staticmethod
    def get():
        """ Method used to sign in
            Example of query:
            {
                "name": "Tester",
                "password": "qwerty123",
                "remember": "true"
            }
            :return: list[]
        """

        name = request.args.get('name')
        password = request.args.get('password')
        password_hash = hashlib.md5(
            password.encode() +
            Consts.PASSWORD_SALT).hexdigest()

        user = User.query.filter(User.name == name,
                                 User.password_hash == password_hash).first()

        if user is not None:
            return {'is_success': True, 'name': user.name, 'token': user.token}

        return {'is_success': False}

    @staticmethod
    def post():
        """ Method used to sign up
            Example of query:
            {
                "name": "Tester",
                "password": "qwerty123",
                "email": "tester@ya.ru"
            }
            :return: list[]
        """

        request_json = request.json

        if not request_json:
            return abort(400, "No data")

        errors = []

        name = request_json["name"]
        email = request_json["email"]
        password = request_json["password"]
        password_repeat = request_json["password_repeat"]

        if len(name) < 5 or len(name) > 12:
            errors.append(
                'Name must be greater than 5 chars and less than 12 chars')

        if db.session.query(
                User.query.filter(
                    User.name == name).exists()).scalar():
            errors.append('Name is already taken')

        if not Utils.is_email_valid(email):
            errors.append('Email is invalid')

        if len(password) < 6:
            errors.append('Password must be greater than 6 chars')

        if password != password_repeat:
            errors.append('Password repeat is invalid')

        if len(errors) > 0:
            return {'is_success': False, "error": errors[0]}

        password_hash = hashlib.md5(
            password.encode() +
            Consts.PASSWORD_SALT).hexdigest()
        privilege_level = 1
        token = hashlib.sha256(
            (name + Utils.random_string(10)).encode()).hexdigest()

        user = create_user(name, email, password_hash, token, privilege_level)
        db.session.add(user)
        db.session.commit()

        return {'is_success': True, 'name': name, 'token': token}


class IntegrateUserApi(Resource):
    """ Class that integrates user with moysklad.ru """

    @staticmethod
    @require_authentication
    def post(user):
        """ Method that integrates user with moysklad.ru
            Example of query:
            {
                "moysklad_password": "1231231",
                "moysklad_login": "abc@def"
            }
            :return: list[]
        """
        if not request.json:
            return abort(400, "No data")
        request_json = request.json
        user.moysklad_login = request_json['moysklad_login']
        user.moysklad_password = request_json['moysklad_password']
        response = requests.get(
            'https://online.moysklad.ru/api/remap/1.1/entity/move?expand=positions',
            auth=requests.auth.HTTPBasicAuth(
                user.moysklad_login,
                user.moysklad_password))
        user.moysklad_id = response.json()['rows'][0]['accountId']
        db.session.add(user)
        db.session.commit()
        return {'is_success': True}


class IntegrateApi(Resource):
    """ Class that imports data from moysklad.ru """

    @staticmethod
    @require_authentication
    def delete(user):
        """ Function that deletes all user data importet from moysklad """
        for sale in Sale.query.filter(Sale.user_token == user.token).all():
            db.session.delete(sale)
        for tag in Tag.query.filter(Tag.user_token == user.token).all():
            db.session.delete(tag)
        for product_type in ProductType.query.filter(ProductType.user_token == user.token).all():
            for lstm in product_type.lstms:
                db.session.delete(lstm)
            db.session.delete(product_type)
        for point in Point.query.filter(Point.user_token == user.token).all():
            for lstm in point.lstms:
                db.session.delete(lstm)
            db.session.delete(point)
        db.session.commit()

    @staticmethod
    @require_authentication
    def post(user):

        """ Method that imports all data from moysklad.ru """
        response = requests.get(
            'https://online.moysklad.ru/api/remap/1.1/entity/product?limit=100',
            auth=requests.auth.HTTPBasicAuth(
                user.moysklad_login,
                user.moysklad_password))
        for item in response.json()['rows']:
            product_type_id = item['id']
            name = item['name']
            price = item['salePrices'][0]['value']
            product_type = ProductType.query.filter(
                ProductType.id == product_type_id, ProductType.user_token == user.token).first()
            if product_type is None:
                product_type = ProductType(
                    id=product_type_id,
                    name=name,
                    user_token=user.token,
                    price=price,
                    seasonality=0)
                db.session.add(product_type)
            else:
                product_type.name = name
                product_type.price = price
                # product_type.id = product_type_id
        db.session.commit()

        #     print(i.id)
        response = requests.get(
            'https://online.moysklad.ru/api/remap/1.1/entity/store?limit=100',
            auth=requests.auth.HTTPBasicAuth(
                user.moysklad_login,
                user.moysklad_password))
        for item in response.json()['rows']:
            point_id = item['id']
            address = item['address']
            point = Point.query.filter(
                Point.id == point_id,
                Point.user_token == user.token).first()
            if point is None:
                params = {'format': 'json', 'apikey': '7c0fb672-2b23-4786-b6b4-588422f61f4c', 'geocode': address}
                longitude, latitude = map(float,
                                          requests.get('https://geocode-maps.yandex.ru/1.x/', params=params).json()['response']['GeoObjectCollection']['featureMember'][
                                              0]['GeoObject']['Point']['pos'].split())
                point = Point(
                    id=point_id,
                    longitude=longitude,
                    latitude=latitude,
                    address=address,
                    user_token=user.token  # ,
                    # longitude=0,latitude=0
                )
                db.session.add(point)
            else:
                point.address = address
                params = {'format': 'json', 'apikey': '7c0fb672-2b23-4786-b6b4-588422f61f4c', 'geocode': address}
                longitude, latitude = map(float,
                                          requests.get('https://geocode-maps.yandex.ru/1.x/', params=params).json()['response']['GeoObjectCollection']['featureMember'][
                                              0]['GeoObject']['Point']['pos'].split())
                point.longitude = longitude
                point.latitude = latitude
                db.session.add(point)
                # point.id = point_id
                # point.user_token = user.token
            db.session.commit()

        # db.session.commit()
        response = requests.get(
            'https://online.moysklad.ru/api/remap/1.1/report/stock/bystore?limit=100',
            auth=requests.auth.HTTPBasicAuth(
                user.moysklad_login,
                user.moysklad_password))
        # point_ids = set()

        product_type_ids = [0 for i in range(len(ProductType.query.filter(ProductType.user_token == user.token).all()))]
        point_ids = [0 for i in range(len(Point.query.filter(Point.user_token == user.token).all()))]
        final = [[0 for j in range(len(product_type_ids))] for i in range(len(point_ids))]
        for product_index, item in enumerate(response.json()['rows']):
            for point_index, store_item in enumerate(item['stockByStore']):
                point_id = store_item['meta']['href'].split('/')[-1]
                product_type_id = item['meta']['href'].split(
                    '/')[-1].split('?')[0]

                product_type = ProductType.query.get(product_type_id)
                point = Point.query.get(point_id)
                sell_price = product_type.price
                tag = Tag.query.filter(
                    Tag.point_id == point_id,
                    Tag.product_type_id == product_type_id,
                    Tag.user_token == user.token).first()
                # print(tag)
                model = LSTM.query.filter(LSTM.point_id == point_id, LSTM.product_type_id == product_type_id, LSTM.user_token == user.token).first()
                # print(tag)
                if tag is None:
                    # print('in none')
                    tag = Tag(
                        point_id=point_id,
                        sell_price=sell_price,
                        product_type_id=product_type_id,
                        minimum=0,
                        capacity=1000,
                        fullness=store_item['stock'],
                        user_token=user.token)
                    db.session.add(tag)
                    final[point_index][product_index] = {
                        'product_type_id': product_type_id,
                        'name': product_type.name,
                        'price': product_type.price,
                        'seasonality': product_type.seasonality,
                        'point_id': point_id,
                        'sell_price': sell_price,
                        'latitude': point.latitude,
                        'longitude': point.longitude,
                        'address': point.address, 'fullness': store_item['stock'],
                        'capacity': 1000, 'minimum': 0,
                        'lstm': model is not None,
                        'before_range': model.before_range if model is not None else 0
                    }
                else:
                    tag.sell_price = sell_price
                    tag.fullness = store_item['stock']
                    final[point_index][product_index] = {
                        'product_type_id': product_type_id,
                        'name': product_type.name,
                        'price': product_type.price,
                        'seasonality': product_type.seasonality,
                        'sell_price': sell_price,
                        'fullness': store_item['stock'],
                        'capacity': tag.capacity, 'minimum': tag.minimum,
                        'lstm': model is not None,
                        'before_range': model.before_range if model is not None else 0,
                        'latitude': point.latitude,
                        'longitude': point.longitude,
                        'address': point.address,
                        'point_id': point_id
                    }
        db.session.commit()
        final_result = []
        for point_index in range(len(final)):
            final_result.append({
                'point_id': final[point_index][0]['point_id'],
                'address': final[point_index][0]['address'],
                'latitude': final[point_index][0]['latitude'],
                'longitude': final[point_index][0]['longitude'],
                'product_types': []
            })
            for type_index in range(len(product_type_ids)):
                final_result[point_index]['product_types'].append(final[point_index][type_index])
            print(final_result[-1], '\n', 'shop')

        shops_list = set()
        response = requests.get(
            'https://online.moysklad.ru/api/remap/1.1/entity/retaildemand?expand=positions.demandposition,positions.assortment.product,store&limit=100',
            auth=requests.auth.HTTPBasicAuth(
                user.moysklad_login,
                user.moysklad_password))
        for item in response.json()['rows']:
            date = datetime.fromisoformat(item['moment'])
            point_id = item['store']['id']
            shops_list.add(point_id)
            for position in item['positions']['rows']:
                sale_id = position['id']
                count = position['quantity']
                product_type_id = position['assortment']['id']
                price = position['price']
                sale = Sale.query.filter(
                    Sale.id == sale_id,
                    Sale.user_token == user.token).first()
                if sale is None:
                    sale = Sale(
                        id=sale_id,
                        date=date,
                        point_id=point_id,
                        count=count,
                        product_type_id=product_type_id,
                        price=price,
                        user_token=user.token)
                    db.session.add(sale)
                else:
                    sale.price = price
                    sale.count = count
                    sale.date = date
        db.session.commit()
        # если мыразличаем склады и магазины то код дальше не нужен
        response = requests.get(
            'https://online.moysklad.ru/api/remap/1.1/entity/move?expand=positions&limit=100',
            auth=requests.auth.HTTPBasicAuth(
                user.moysklad_login,
                user.moysklad_password))
        for item in response.json()['rows']:
            point_id = item['sourceStore']['meta']['href'].split('/')[-1]
            if point_id not in shops_list:
                sale_id = item['id']
                date = datetime.fromisoformat(item['moment'])
                for position in item['positions']['rows']:
                    count = position['quantity']
                    product_type_id = position['assortment']['id']
                    price = position['price']
                    sale = Sale.query.filter(
                        Sale.id == sale_id, Sale.user_token == user.token).first()
                    if sale is None:
                        sale = Sale(
                            id=sale_id,
                            date=date,
                            point_id=point_id,
                            count=count,
                            product_type_id=product_type_id,
                            price=price,
                            user_token=user.token)
                        db.session.add(sale)
                    else:
                        sale.price = price
                        sale.count = count
                        sale.date = date
        db.session.commit()
        return {'result': final_result}, 200


api.add_resource(IntegrateApi, '/api/user/integrate')
api.add_resource(IntegrateUserApi, '/api/authentication/integrate')
api.add_resource(AuthenticationApi, '/api/authentication')
api.add_resource(ProductTypesApi, '/api/product_types/<product_type_id>')
api.add_resource(PointApi, '/api/points/<point_id>')
api.add_resource(LSTMApi, '/api/lstms/<lstm_id>')
api.add_resource(SaleApi, '/api/sales/<sale_id>')
api.add_resource(TagsApi, '/api/tags/<tag_id>')
api.add_resource(ListProductTypesApi, '/api/product_types')
api.add_resource(ListPointsApi, '/api/points')
api.add_resource(ListLSTMsApi, '/api/lstms')
api.add_resource(ListSalesApi, '/api/sales')
api.add_resource(PredictApi, '/api/predict')
api.add_resource(ListTagsApi, '/api/tags')
api.add_resource(TrainAllLSTMS, '/api/train_all')


