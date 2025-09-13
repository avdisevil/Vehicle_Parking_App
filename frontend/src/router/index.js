import { createRouter, createWebHistory } from 'vue-router';
import Home from '../views/Home.vue';
import Login from '../views/Login.vue';
import Register from '../views/Register.vue';
import AdminDashboard from '../views/AdminDashboard.vue'
import UserDashboard from '../views/UserDashboard.vue'
import ErrorPage from '../views/Error.vue'
import AdminUsers from '../views/AdminUsers.vue'
import AdminSearch from '../views/AdminSearch.vue'
import AdminSummary from '../views/AdminSummary.vue'
import UserSummary from '../views/UserSummary.vue'
import UserSearch from '../views/UserSearch.vue'

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/login', name: 'Login', component: Login },
  { path: '/register', name: 'Register', component: Register },
  { path: '/admin', name: 'AdminDashboard', component: AdminDashboard },
  { path: '/admin/users', name: 'AdminUsers', component: AdminUsers },
  { path: '/admin/search', name: 'AdminSearch', component: AdminSearch },
  { path: '/admin/summary', name: 'AdminSummary', component: AdminSummary },
  { path: '/error', name: 'ErrorPage', component: ErrorPage },
  { path: '/user', name: 'UserDashboard', component: UserDashboard },
  { path: '/user/summary', name: 'UserSummary', component: UserSummary },
  { path: '/user/search', name: 'UserSearch', component: UserSearch },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
