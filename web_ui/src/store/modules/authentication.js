import axios from 'axios'

export const AUTH_SIGN_IN_REQUEST = "AUTH_SIGN_IN_REQUEST";
export const AUTH_SIGN_UP_REQUEST = "AUTH_SIGN_UP_REQUEST";
export const AUTH_LOGOUT = "AUTH_LOGOUT";

export const AUTH_SUCCESS = "AUTH_SUCCESS";
export const AUTH_ERROR = "AUTH_ERROR";

const state = {
    name: localStorage.getItem('name') || '',
    token: localStorage.getItem('token') || ''
};

const getters = {
    isAuthenticated: state => !!state.token,
    name: state => state.name
};

const mutations = {
    [AUTH_SUCCESS]: (state, {name, token}) => {
        state.name = name;
        state.token = token;
    },
    [AUTH_LOGOUT]: (state) => {
        state.name = '';
        state.token = '';
    },
};

const actions = {
    // eslint-disable-next-line no-unused-vars
    [AUTH_SIGN_IN_REQUEST]: ({commit, dispatch}, user) => {
        return new Promise((resolve, reject) => {
            axios.get('authentication', {
                params: {
                    "name": user.name,
                    "password": user.password
                }
            }).then(response => {
                let data = response.data;
                let success = data.is_success;

                if (success) {
                    let name = data.name;
                    let token = data.token;

                    localStorage.setItem('name', name);
                    localStorage.setItem('token', token);

                    axios.defaults.headers.common['Authorization'] = token;

                    commit(AUTH_SUCCESS, {name, token});
                }

                resolve(success);
            }).catch(err => {
                commit(AUTH_ERROR, err);
                localStorage.removeItem('name');
                localStorage.removeItem('token');
                reject(err)
            });
        })
    },

    // eslint-disable-next-line no-unused-vars
    [AUTH_SIGN_UP_REQUEST]: ({commit, dispatch}, user) => {
        return new Promise((resolve, reject) => {
            axios.post('authentication', {
                "name": user.name,
                "email": user.email,
                "password": user.password,
                "password_repeat": user.passwordRepeat
            }).then(response => {
                let data = response.data;
                let success = data.is_success;

                if (success) {
                    let name = data.name;
                    let token = data.token;

                    localStorage.setItem('name', name);
                    localStorage.setItem('token', token);

                    axios.defaults.headers.common['Authorization'] = token;

                    commit(AUTH_SUCCESS, {name, token});
                }

                resolve(response);
            }).catch(err => {
                commit(AUTH_ERROR, err);
                localStorage.removeItem('name');
                localStorage.removeItem('token');
                reject(err)
            });
        })
    },

    // eslint-disable-next-line no-unused-vars
    [AUTH_LOGOUT]: ({commit, dispatch}) => {
        // eslint-disable-next-line no-unused-vars
        return new Promise((resolve, reject) => {
            commit(AUTH_LOGOUT);

            localStorage.removeItem('name');
            localStorage.removeItem('token');

            delete axios.defaults.headers.common['Authorization'];
            resolve()
        })
    }
};

export default {
    namespace: true,
    state,
    getters,
    actions,
    mutations
}