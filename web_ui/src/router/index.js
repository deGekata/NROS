import Home from "../views/Home.vue";
import Dashboard from "../views/Dashboard.vue";
import Vue from "vue";
import VueRouter from "vue-router";

import store from '../store' // your vuex store

Vue.use(VueRouter);

// eslint-disable-next-line no-unused-vars
// use it only for pages don't require authentication
const ifNotAuthenticated = (to, from, next) => {
    if (!store.getters.isAuthenticated) {
        next();
        return
    }
    next('/dashboard')
};

// eslint-disable-next-line no-unused-vars
// use it only for pages that require authentication
const ifAuthenticated = (to, from, next) => {
    if (store.getters.isAuthenticated) {
        next();
        return
    }
    next('/')
};

const routes = [
    {
        path: "/",
        name: "Home",
        component: Home,
        beforeEnter: ifNotAuthenticated
    },
    {
        path: "/dashboard",
        name: "Dashboard",
        component: Dashboard,
        beforeEnter: ifAuthenticated
    },
    {
        path: "/about",
        name: "About",
        component: () => import("../views/About.vue"),
        beforeEnter: ifAuthenticated
    },
    {
        path: "/charts",
        name: "Charts",
        component: () => import("../views/Charts.vue"),
        beforeEnter: ifAuthenticated
    },
    {
        path: "/orders",
        name: "Orders",
        //component: () => import("../views/Orders.vue"),
        beforeEnter: ifAuthenticated
    },
    {
        path: "/settings",
        name: "Settings",
        component: () => import("../views/Settings.vue"),
        beforeEnter: ifAuthenticated
    },
    {
        path: "/help",
        name: "Help",
        //component: () => import("../views/Help.vue")
    },
    {
        path: "/map",
        name: "Map",
        component: () => import("../views/Map.vue"),
        beforeEnter: ifAuthenticated
    },
    {
        path: "/data_checker",
        redirect: 'data_checker/types',
        name: "DataChecker",
        beforeEnter: ifAuthenticated
    },
    {
        path: "/data_checker/types",
        name: "DataChecker",
        component: () => import("../views/Types.vue"),
        beforeEnter: ifAuthenticated
    },
    {
        path: "/data_checker/items",
        name: "DataChecker",
        component: () => import("../views/Items.vue"),
        beforeEnter: ifAuthenticated
    },
    {
        path: "/data_checker/groups",
        name: "DataChecker",
        component: () => import("../views/Groups.vue"),
        beforeEnter: ifAuthenticated
    },
    {
        path: "/data_checker/locations",
        name: "DataChecker",
        component: () => import("../views/Locations.vue"),
        beforeEnter: ifAuthenticated
    },
];

const router = new VueRouter({
    mode: "history",
    base: process.env.BASE_URL,
    routes
});

export default router;
