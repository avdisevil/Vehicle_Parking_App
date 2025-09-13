// Use for scaling to larger application

import { createStore } from 'vuex'
import axios from 'axios'

const token = localStorage.getItem('token')
if (token) {
  axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
}

export default createStore({
  state: {
    token: token || '',
    role: localStorage.getItem('role') || '',
  },
  mutations: {
    setAuth(state, { token, role }) {
      state.token = token
      state.role = role
      localStorage.setItem('token', token)
      localStorage.setItem('role', role)

      // Apply token globally
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
    },
    logout(state) {
      state.token = ''
      state.role = ''
      localStorage.clear()

      // Remove token from Axios headers
      delete axios.defaults.headers.common['Authorization']
    },
  },
})
