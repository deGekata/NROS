import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import keras.layers as kl
import keras.models as km
from keras import backend as K
import numpy as np
from scipy.optimize import minimize
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error
import math
import random
import pickle


def trainModelsAndPredict(inData, before_range, model, slen=0):
    """
        function to train models and predict
    """
    data = pd.DataFrame(columns={'Quantity', 'date'})
    for sale in inData:
        data = data.append(
            {'Quantity': int(sale[1]), 'date': sale[0]}, ignore_index=True)
    data = data.set_index(['date'])
    if slen == 0:
        a, b, g = -1, -1, -1
        prediction = 0
    else:
        a, b, g = train(data, slen)
        prediction, _ = predictWinters(data.values, a, b, g, slen)
        prediction = prediction[0][0]
    model, scaler, before_range = trainLSTM(
        data, do_scale=True, epochs=100, batch=32, verbose=0, before_range=before_range, modelI=model)

    lstm_pred = int(predict_next_day(
        inData[-(before_range + 1):], before_range=before_range, scaler=scaler, model=model)[0][0])
    return a, b, g, model, scaler, int(prediction), before_range - 1, lstm_pred


class HoltWinters:
    """
        http://www.machinelearning.ru/wiki/index.php?title=Модель_Хольта-Уинтерса
    """
    def __init__(
            self,
            series,
            slen,
            alpha,
            beta,
            gamma,
            n_preds,
            scaling_factor=1.96):
        """
            This is a function
        """
        self.series = series
        self.slen = slen
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.n_preds = n_preds
        self.scaling_factor = scaling_factor

    def initial_trend(self):
        """
            https://habr.com/ru/company/ods/blog/327242/
        """
        sum = 0.0
        for i in range(self.slen):
            sum += float(self.series[i + self.slen] -
                         self.series[i]) / self.slen
        return sum / self.slen

    def initial_seasonal_components(self):
        """
            https://habr.com/ru/company/ods/blog/327242/
        """
        seasonals = {}
        season_averages = []

        n_seasons = int(len(self.series) / self.slen)

        for j in range(n_seasons):

            season_averages.append(
                sum(self.series[self.slen * j:self.slen * j + self.slen]) / float(self.slen))
        for i in range(self.slen):
            sum_of_vals_over_avg = 0.0
            for j in range(n_seasons):
                sum_of_vals_over_avg += self.series[self.slen *
                                                    j + i] - season_averages[j]
            seasonals[i] = sum_of_vals_over_avg / n_seasons
        return seasonals

    def triple_exponential_smoothing(self):
        """
           it traning for model
        """
        self.result = []
        self.Smooth = []
        self.Season = []
        self.Trend = []
        self.PredictedDeviation = []
        self.UpperBond = []
        self.LowerBond = []

        seasonals = self.initial_seasonal_components()

        for i in range(len(self.series) + self.n_preds):
            if i == 0:
                smooth = self.series[0]
                trend = self.initial_trend()
                self.result.append(self.series[0])
                self.Smooth.append(smooth)
                self.Trend.append(trend)
                self.Season.append(seasonals[i % self.slen])

                self.PredictedDeviation.append(0)

                self.UpperBond.append(self.result[0] +
                                      self.scaling_factor *
                                      self.PredictedDeviation[0])

                self.LowerBond.append(self.result[0] -
                                      self.scaling_factor *
                                      self.PredictedDeviation[0])

                continue
            if i >= len(self.series):
                m = i - len(self.series) + 1
                self.result.append((smooth + m * trend) +
                                   seasonals[i % self.slen])

                self.PredictedDeviation.append(
                    self.PredictedDeviation[-1] * 1.01)

            else:
                val = self.series[i]
                last_smooth, smooth = smooth, self.alpha * \
                    (val - seasonals[i % self.slen]) + (1 - self.alpha) * (smooth + trend)
                trend = self.beta * (smooth - last_smooth) + \
                    (1 - self.beta) * trend
                seasonals[i % self.slen] = self.gamma * \
                    (val - smooth) + (1 - self.gamma) * seasonals[i % self.slen]
                self.result.append(smooth + trend + seasonals[i % self.slen])

                self.PredictedDeviation.append(self.gamma * np.abs(self.series[i] - self.result[i])
                                               + (1 - self.gamma) * self.PredictedDeviation[-1])

            self.UpperBond.append(self.result[-1] +
                                  self.scaling_factor *
                                  self.PredictedDeviation[-1])

            self.LowerBond.append(self.result[-1] -
                                  self.scaling_factor *
                                  self.PredictedDeviation[-1])

            self.Smooth.append(smooth)
            self.Trend.append(trend)
            self.Season.append(seasonals[i % self.slen])


def timeseriesCVscore(x, data, slen):
    """
            This is a function
    """
    errors = []

    values = data.values.astype('float64')
    alpha, beta, gamma = x

    tscv = TimeSeriesSplit(n_splits=2)

    for train, test in tscv.split(values):

        model = HoltWinters(
            series=values[train],
            slen=slen,
            alpha=alpha,
            beta=beta,
            gamma=gamma,
            n_preds=len(test))
        model.triple_exponential_smoothing()

        predictions = model.result[-len(test):]
        actual = values[test]
        error = mean_squared_error(predictions, actual)
        errors.append(error)

    return np.mean(np.array(errors))


def train(data, slen):
    """
        This is a function
    """
    x = [0, 0, 0]

    opt = minimize(
        timeseriesCVscore, x0=x, args=(
            data, slen), method="TNC", bounds=(
            (0, 1), (0, 1), (0, 1)))

    alpha_final, beta_final, gamma_final = opt.x
    return alpha_final, beta_final, gamma_final


def transform_data_train(resC, before_range):
    """
        This is a function
    """
    resC = resC.reset_index()
    daily_data = resC.copy()
    resC.append = 0
    resC['prev_sales'] = resC['Quantity'].shift(1)
    resC = resC.dropna()
    resC['diff'] = (resC['Quantity'] - resC['prev_sales'])
    df_supervised = resC.drop(['prev_sales'], axis=1)
    for inc in range(1, before_range):
        field_name = 'lag_' + str(inc)
        df_supervised[field_name] = df_supervised['diff'].shift(inc)
    df_supervised = df_supervised.dropna().reset_index(drop=True)

    df_model = df_supervised.drop(['Quantity', 'date'], axis=1)

    return df_model


def scale_train(train_set, model):
    """
        This is a function
    """
    if model is None:
        scaler = MinMaxScaler(feature_range=(-1, 1))
        scaler = scaler.fit(train_set)
    else:
        scaler = pickle.loads(model.scope)
    train_set_scaled = scaler.transform(train_set)
    return train_set_scaled, scaler


def convertToTrain(train_set):
    """
        This is a function
    """
    train_set = train_set.reshape(train_set.shape[0], train_set.shape[1])
    X_train, y_train = train_set[:, 1:], train_set[:, 0:1]
    X_train = X_train.reshape(X_train.shape[0], 1, X_train.shape[1])
    return X_train, y_train


def compile_LSTM_model(shape, params={}):
    """
        This is a function
    """
    model = km.Sequential()
    if params != {}:
        pass
    else:
        model.add(kl.LSTM(20, input_shape=(shape[1], shape[2])))
        model.add(kl.Dropout(0.08))
        model.add(kl.Dense(1, activation="elu"))
        model.compile(loss='mean_squared_error', optimizer='adam')
    return model


def trainLSTM(
        data,
        modelI,
        do_scale=True,
        epochs=100,
        batch=32,
        verbose=0,
        before_range=5):
    """
        This is a function
    """
    train_set = transform_data_train(data, before_range).values
    if do_scale:
        train_set, scaler = scale_train(train_set, modelI)
    X_train, y_train = convertToTrain(
        train_set if do_scale else np.array(train_set))
    if modelI is None:
        model = compile_LSTM_model(X_train.shape)
    else:
        model = pickle.loads(modelI.model)

    model.fit(
        X_train,
        y_train,
        epochs=epochs,
        batch_size=batch,
        verbose=verbose,
        shuffle=False)
    if do_scale:
        return model, scaler, before_range
    return model, before_range


def predictWinters(
        data,
        alpha_final,
        beta_final,
        gamma_final,
        slen,
        n_preds=1,
        scaling_factor=2.5):
    """
        This is a function
    """
    model = HoltWinters(
        data,
        slen=slen,
        alpha=alpha_final,
        beta=beta_final,
        gamma=gamma_final,
        n_preds=n_preds,
        scaling_factor=scaling_factor)
    model.triple_exponential_smoothing()
    return [model.result[-n_preds:], data[-n_preds:]]


class Population:
    """
        This is a class
    """
    def __init__(self):
        """
            This is a function
        """
        self.population = []
        self.fronts = []

    def __len__(self):
        """
            This is a function
        """
        return len(self.population)

    def __iter__(self):
        """
            This is a function
        """
        return self.population.__iter__()

    def extend(self, new_individuals):
        """
            This is a function
        """
        self.population.extend(new_individuals)

    def append(self, new_individual):
        """
            This is a function
        """
        self.population.append(new_individual)


class Individual(object):
    """
        This is a class
    """
    def __init__(self):
        """
            This is a function
        """
        self.rank = None
        self.crowding_distance = None
        self.domination_count = None
        self.dominated_solutions = None
        self.features = None
        self.objectives = None

    def __eq__(self, other):
        """
            This is a function
        """
        if isinstance(self, other.__class__):
            return self.features == other.features
        return False

    def dominates(self, other_individual):
        """
            This is a function
        """
        and_condition = True
        or_condition = False
        for first, second in zip(self.objectives, other_individual.objectives):
            and_condition = and_condition and first <= second
            or_condition = or_condition or first < second
        return (and_condition and or_condition)


class Problem:
    """
        This is a class
    """
    def __init__(
            self,
            objectives,
            num_of_variables,
            variables_range,
            extend_vars=0,
            expand=True,
            same_range=False):
        """
            This is a function
        """
        self.num_of_objectives = len(objectives)
        self.num_of_variables = num_of_variables
        self.objectives = objectives
        self.expand = expand
        self.variables_range = []
        if same_range:
            for _ in range(num_of_variables):
                self.variables_range.append(variables_range[0])
        else:
            self.variables_range = variables_range
        self.extend_vars = extend_vars

    def generate_individual(self, mag, sklad, ftrs):
        """
            This is a function
        """
        individual = Individual()
        individual.features = ftrs
        individual.features.append(sklad)
        individual.features.append(mag)
        return individual

    def calculate_objectives(self, individual):
        """
            This is a function
        """
        if self.expand:
            individual.objectives = [f(*individual.features)
                                     for f in self.objectives]
        else:
            individual.objectives = [f(individual.features)
                                     for f in self.objectives]


class NSGA2Utils:
    """
        This is a class
    """
    def __init__(
            self,
            problem,
            mutation_probability,
            crossover_probability,
            num_of_individuals=100,
            num_of_tour_particips=2,
            tournament_prob=0.9,
            crossover_param=2,
            mutation_param=5):
        """
            This is a function
        """
        self.problem = problem
        self.num_of_individuals = num_of_individuals
        self.num_of_tour_particips = num_of_tour_particips
        self.tournament_prob = tournament_prob
        self.crossover_param = crossover_param
        self.mutation_param = mutation_param

        self.mutation_probability = mutation_probability
        self.crossover_probability = crossover_probability

    def create_initial_population(self):
        """
            This is a function
        """
        population = Population()
        for _ in range(self.num_of_individuals):
            for i in range(len(self.problem.extend_vars)):
                for j in range(i + 1, len(self.problem.extend_vars)):
                    individual = self.problem.generate_individual(
                        self.problem.extend_vars[i], self.problem.extend_vars[j], [
                            random.randint(
                                *x) for x in self.problem.variables_range])
                    self.problem.calculate_objectives(individual)
                    population.append(individual)
        return population

    def fast_nondominated_sort(self, population):
        """
            This is a function
        """
        population.fronts = [[]]
        for individual in population:
            individual.domination_count = 0
            individual.dominated_solutions = []
            for other_individual in population:
                if individual.dominates(other_individual):
                    individual.dominated_solutions.append(other_individual)
                elif other_individual.dominates(individual):
                    individual.domination_count += 1
            if individual.domination_count == 0:
                individual.rank = 0
                population.fronts[0].append(individual)
        i = 0
        while len(population.fronts[i]) > 0:
            temp = []
            for individual in population.fronts[i]:
                for other_individual in individual.dominated_solutions:
                    other_individual.domination_count -= 1
                    if other_individual.domination_count == 0:
                        other_individual.rank = i + 1
                        temp.append(other_individual)
            i = i + 1
            population.fronts.append(temp)

    def calculate_crowding_distance(self, front):
        """
            This is a function
        """
        if len(front) > 0:
            solutions_num = len(front)
            for individual in front:
                individual.crowding_distance = 0

            for m in range(len(front[0].objectives)):
                front.sort(key=lambda individual: individual.objectives[m])
                front[0].crowding_distance = 10**9
                front[solutions_num - 1].crowding_distance = 10**9
                m_values = [individual.objectives[m] for individual in front]
                scale = max(m_values) - min(m_values)
                if scale == 0:
                    scale = 1
                for i in range(1, solutions_num - 1):
                    front[i].crowding_distance += (
                        front[i + 1].objectives[m] - front[i - 1].objectives[m]) / scale

    def crowding_operator(self, individual, other_individual):
        """
            This is a function
        """
        if (individual.rank < other_individual.rank) or ((individual.rank == other_individual.rank) and (
                individual.crowding_distance > other_individual.crowding_distance)):
            return 1
        else:
            return -1

    def create_children(self, population):
        """
            This is a function
        """
        children = []
        while len(children) < len(population):
            parent1 = self.__tournament(population)
            parent2 = parent1
            while parent1 == parent2:
                parent2 = self.__tournament(population)
            child1, child2 = self.__crossover(parent1, parent2)
            self.__mutate(child1)
            self.__mutate(child2)
            self.problem.calculate_objectives(child1)
            self.problem.calculate_objectives(child2)
            children.append(child1)
            children.append(child2)

        return children

    def __crossover(self, individual1, individual2):
        """
            This is a function
        """
        rnd1 = random.choice(self.problem.extend_vars)
        rnd2 = random.choice(self.problem.extend_vars)
        while rnd1 == rnd2:
            rnd2 = random.choice(self.problem.extend_vars)
        child1 = self.problem.generate_individual(
            rnd1, rnd2, [random.randint(*x) for x in self.problem.variables_range])

        rnd1 = random.choice(self.problem.extend_vars)
        rnd2 = random.choice(self.problem.extend_vars)
        while rnd1 == rnd2:
            rnd2 = random.choice(self.problem.extend_vars)
        child2 = self.problem.generate_individual(
            rnd1, rnd2, [random.randint(*x) for x in self.problem.variables_range])

        num_of_features = 2
        genes_indexes = range(num_of_features)
        for i in genes_indexes:
            beta = self.__get_beta()
            x1 = (individual1.features[i] + individual2.features[i]) / 2
            x2 = abs((individual1.features[i] - individual2.features[i]) / 2)
            child1.features[i] = x1 + beta * x2
            child2.features[i] = x1 - beta * x2
        return child1, child2

    def __get_beta(self):
        """
            This is a function
        """
        u = random.random()
        if u <= 0.5:
            return (2 * u)**(1 / (self.crossover_param + 1))
        return (2 * (1 - u))**(-1 / (self.crossover_param + 1))

    def __mutate(self, child):
        """
            This is a function
        """
        num_of_features = 2
        for gene in range(num_of_features):
            u, delta = self.__get_delta()
            if u < 0.5:
                child.features[gene] += delta * \
                    (child.features[gene] - self.problem.variables_range[gene][0])
            else:
                child.features[gene] += delta * \
                    (self.problem.variables_range[gene][1] - child.features[gene])
            if child.features[gene] < self.problem.variables_range[gene][0]:
                child.features[gene] = self.problem.variables_range[gene][0]
            elif child.features[gene] > self.problem.variables_range[gene][1]:
                child.features[gene] = self.problem.variables_range[gene][1]

    def __get_delta(self):
        """
            This is a function
        """
        u = random.random()
        if u < 0.5:
            return u, (2 * u)**(1 / (self.mutation_param + 1)) - 1
        return u, 1 - (2 * (1 - u))**(1 / (self.mutation_param + 1))

    def __tournament(self, population):
        """
            This is a function
        """
        participants = random.sample(
            population.population,
            self.num_of_tour_particips)
        best = None
        for participant in participants:
            if best is None or (
                self.crowding_operator(
                    participant,
                    best) == 1 and self.__choose_with_prob(
                    self.tournament_prob)):
                best = participant
        return best

    def __choose_with_prob(self, prob):
        if random.random() <= prob:
            return True
        return False


class Evolution:
    """
        This is a class
    """
    def __init__(
            self,
            problem,
            num_of_generations=1000,
            num_of_individuals=100,
            num_of_tour_particips=2,
            tournament_prob=0.9,
            crossover_param=2,
            mutation_param=5,
            mutation_probability=0.5,
            crossover_probability=0.5):
        """
            This is a function
        """
        self.utils = NSGA2Utils(
            problem,
            mutation_probability,
            crossover_probability,
            num_of_individuals,
            num_of_tour_particips,
            tournament_prob,
            crossover_param,
            mutation_param)
        self.population = None
        self.num_of_generations = num_of_generations
        self.on_generation_finished = []
        self.num_of_individuals = num_of_individuals

    def evolve(self):
        """
            This is a function
        """
        self.population = self.utils.create_initial_population()
        self.utils.fast_nondominated_sort(self.population)
        for front in self.population.fronts:
            self.utils.calculate_crowding_distance(front)
        children = self.utils.create_children(self.population)
        returned_population = None
        for i in range(self.num_of_generations):
            self.population.extend(children)
            self.utils.fast_nondominated_sort(self.population)
            new_population = Population()
            front_num = 0

            while len(new_population) + \
                    len(self.population.fronts[front_num]) <= self.num_of_individuals:
                self.utils.calculate_crowding_distance(
                    self.population.fronts[front_num])
                new_population.extend(self.population.fronts[front_num])
                front_num += 1
            self.utils.calculate_crowding_distance(
                self.population.fronts[front_num])
            self.population.fronts[front_num].sort(
                key=lambda individual: individual.crowding_distance, reverse=True)
            new_population.extend(
                self.population.fronts[front_num][0:self.num_of_individuals - len(new_population)])
            returned_population = self.population
            self.population = new_population
            self.utils.fast_nondominated_sort(self.population)
            for front in self.population.fronts:
                self.utils.calculate_crowding_distance(front)
            children = self.utils.create_children(self.population)
        return returned_population.fronts[0]


def pretransorm_pred_data(resC, before_range):
    """
            This is a function
    """
    data = pd.DataFrame(columns={'Quantity', 'date'})
    for i in resC:
        data = data.append({'Quantity': i[1], 'date': i[0]}, ignore_index=True)
    resC = data.reset_index()
    daily_data = resC.copy()
    resC.append = 0
    resC['prev_sales'] = resC['Quantity'].shift(-1)
    resC['diff'] = (resC['Quantity'] - resC['prev_sales'])

    df_supervised = resC.drop(['prev_sales'], axis=1)

    for inc in range(1, before_range):
        field_name = 'lag_' + str(inc)
        df_supervised[field_name] = df_supervised['diff'].shift(-inc)
    df_supervised = df_supervised.dropna().reset_index(drop=True)
    df_model = df_supervised.drop(['Quantity', 'date', 'index'], axis=1)
    return df_model, daily_data.loc[0, 'Quantity']


def pretransorm_test_data(stepGL, before_range):
    """
        This is a function
    """
    data = pd.DataFrame(columns={'Quantity', 'date'})
    for sale in stepGL:
        data = data.append(
            {'Quantity': sale[1], 'date': sale[0]}, ignore_index=True)
    daily_data = data.copy()
    resC = data.reset_index()
    resC.append = 0
    resC['prev_sales'] = resC['Quantity'].shift(-1)
    resC = resC.dropna()
    resC['diff'] = (resC['Quantity'] - resC['prev_sales'])
    df_supervised = resC.drop(['prev_sales'], axis=1)
    for inc in range(1, before_range):
        field_name = 'lag_' + str(inc)
        df_supervised[field_name] = df_supervised['diff'].shift(-inc)
    df_supervised = df_supervised.dropna().reset_index(drop=True)
    step = df_supervised.drop(['Quantity', 'date', 'index'], axis=1)
    return daily_data.loc[0, 'Quantity'], step, data.loc[len(
        data) - len(step):, 'Quantity']


def convertToPred(pred_set):
    """
        This is a function
    """
    pred_set = pred_set.reshape(pred_set.shape[0], pred_set.shape[1])
    X_test = pred_set[:]
    X_test = X_test.reshape(X_test.shape[0], 1, X_test.shape[1])
    return X_test


def convertToTest(test_set):
    """
        This is a function
    """
    test_set = test_set.reshape(test_set.shape[0], test_set.shape[1])
    X_test = test_set[:, 1:]
    X_test = X_test.reshape(X_test.shape[0], 1, X_test.shape[1])
    return X_test


def convertToTrain(train_set):
    """
        This is a function
    """
    train_set = train_set.reshape(train_set.shape[0], train_set.shape[1])
    X_train, y_train = train_set[:, 1:], train_set[:, 0:1]
    X_train = X_train.reshape(X_train.shape[0], 1, X_train.shape[1])
    return X_train, y_train


def shift(resC, before_range):
    """
        This is a function
    """
    resC.loc[len(resC)] = 0
    resC = resC.dropna()

    for inc in range(1, before_range - 1):
        field_name = 'lag_' + str(inc)
        resC[field_name] = resC['diff'].shift(inc)

    resC = resC.dropna().reset_index(drop=True)
    return resC


def predict_next(X_test, model, batch):
    """
        This is a function
    """
    test_set = [[[X_test[0][0][1:]]]]
    diff = model.predict(test_set, batch_size=batch)

    return np.concatenate((diff.ravel(), X_test[0][0][1:].ravel()), axis=None)


def get_quantity(last_quantity, only_lag):
    """
        This is a function
    """
    quantity = []
    for i in only_lag:
        last_quantity = last_quantity + i
        quantity.append(last_quantity)
    return quantity


def predict_next_day(
        data,
        scaler,
        model,
        predict_range=1,
        do_scale=True,
        batch=32,
        before_range=5):
    """
        This is a function
    """
    only_lag, last_quantity = pretransorm_pred_data(data, before_range)
    pred_set = only_lag.values
    if do_scale:
        pred_set = scaler.transform(pred_set)
    X_pred = convertToPred(pred_set if do_scale else np.array(pred_set))
    if predict_range == 1:
        res = predict_next(X_pred, model, batch)
        if do_scale:
            res = scaler.inverse_transform([res])[0]
        only_lag = res
        quantity = get_quantity(last_quantity, [only_lag[0]])
    K.clear_session()
    return [quantity]


def predict_step(
        step,
        scaler,
        model,
        predict_range=1,
        do_scale=True,
        batch=32,
        before_range=5):
    """
        This is a function
    """
    last_quantity, step, stepQ = pretransorm_test_data(step, before_range)
    test_set = step.values
    if do_scale:
        test_set = scaler.transform(test_set)
    X_test = convertToTest(test_set if do_scale else np.array(test_set))
    prediction = model.predict(X_test, batch_size=batch)
    prediciton = prediction.ravel()
    res = []
    for j in range(len(prediction)):
        rng = [0 for i in range(before_range)]
        rng[-1] = prediction[j].tolist()[0]
        res.append(rng)
    if do_scale:
        for i in range(len(res)):
            res[i] = scaler.inverse_transform([res[i]])[0][-1]
    else:
        res = prediciton.ravel().tolist()
    test_quantity = get_quantity(int(stepQ.values[-1]), res)
    K.clear_session()
    return [test_quantity, stepQ.values]


ALPHA = 0.5


def funcE(X):
    """
        This is a function
    """
    res = 0
    for i in X:
        res += (i / len(X))
    return res


def CheckSendCount(sendCount, minOstat, capacity, pred, zapoln):
    """
        This is a function
    """
    c1 = sendCount >= 0
    upperSendCount = minOstat + ALPHA * (capacity - minOstat) + pred - zapoln
    lowerSendCount = minOstat + pred - zapoln
    c2 = sendCount <= upperSendCount and sendCount >= lowerSendCount
    return c1 and c2


def CheckZakupkaCount(ZNSC, minOstat, capacity, predSum, zapoln):
    """
        This is a function
    """
    c1 = ZNSC >= 0
    upperZNSC = minOstat + ALPHA * (capacity - minOstat) + predSum - zapoln
    lowerZNSC = minOstat + predSum - zapoln
    c2 = ZNSC <= upperZNSC and ZNSC >= lowerZNSC
    return c1 and c2


def funcEMin(X):
    """
        This is a function
    """
    res = 0
    for i in X:
        res += (i / len(X))
    return res


def f1_1(sendCount, point):
    """
        This is a function
    """
    res = 0
    spros = point['spros']
    if CheckSendCount(
            sendCount,
            point['shop'].minimum,
            point['shop'].capacity,
            spros,
            point['shop'].fullness):
        res = point['shop'].sell_price * \
            min(spros, (point['shop'].fullness + sendCount))
    return res


def f2_1(sendCount, point):
    """
        This is a function
    """
    res = 0
    spros, listForvector, realSpros = point['spros'], point['listForvector'], point['realSpros']
    if CheckSendCount(
            sendCount,
            point['shop'].minimum,
            point['shop'].capacity,
            spros,
            point['shop'].fullness):
        RNDVector = [
            (listForvector[gg] -
             realSpros[gg]) /
            realSpros[gg] if realSpros[gg] != 0 else 0 for gg in range(
                len(realSpros))]
        res += (-1 * funcE(np.minimum([0], [sendCount + point['shop'].fullness - (1 + randomVector) * spros - point['shop'].minimum for randomVector in RNDVector]))) + (
            funcE(np.maximum([0], [sendCount + point['shop'].fullness - (1 + randomVector) * spros - point['shop'].capacity for randomVector in RNDVector])))
    return res


def f2_2(send):
    """
        This is a function
    """
    res = 0
    skladSumCount = 0
    predSum = 0
    spros = send[3]['spros']
    if CheckSendCount(
            send[1],
            send[3]['shop'].minimum,
            send[3]['shop'].capacity,
            spros,
            send[3]['shop'].fullness):
        skladSumCount += send[1]
        predSum += spros
    if CheckZakupkaCount(
            send[0],
            send[2]['shop'].minimum,
            send[2]['shop'].capacity,
            predSum,
            send[2]['shop'].fullness):
        res = -min(0, (send[2]['shop'].fullness + send[0] - skladSumCount - send[2]['shop'].minimum)) + \
            max(0, (send[2]['shop'].fullness + send[0] - skladSumCount - send[2]['shop'].capacity))

    return res


def f2(send):
    """
        This is a function
    """
    res = f2_2(send) + f2_1(send[1], send[2])
    return res


def f1(send):
    """
        This is a function
    """
    res = f1_1(send[1], send[2])
    return -res


def main_prediction(full):
    """
        This is a function
    """
    problem = Problem(
        num_of_variables=2, objectives=[
            f1, f2], variables_range=[
            (0, 1000), (0, 1000)], expand=False, extend_vars=full)
    evo = Evolution(
        problem,
        mutation_param=8,
        num_of_generations=100,
        num_of_individuals=100,
        tournament_prob=0.8,
        crossover_param=9,
        crossover_probability=0.9,
        mutation_probability=0.25)
    func = [[i.objectives, i.features[:2], [
        j['shop'].point_id for j in i.features[2:]]] for i in evo.evolve()]
    return func