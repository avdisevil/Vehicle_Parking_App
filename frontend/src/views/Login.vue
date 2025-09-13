<template>
  <div class="container d-flex flex-column justify-content-center align-items-center vh-100">
    <router-link to="/" class="mb-4 w-100 d-flex justify-content-center">
      <button class="btn btn-secondary">Home</button>
    </router-link>
    <div class="w-100" style="max-width: 400px;">
      <h2 class="mb-4 text-center">Login</h2>
    <form @submit.prevent="handleLogin">
        <div class="mb-3">
          <input type="email" class="form-control" v-model="email" placeholder="Email" required />
        </div>
        <div class="mb-3">
          <input type="password" class="form-control" v-model="password" placeholder="Password" required />
        </div>
        <button type="submit" class="btn btn-success w-100">Login</button>
    </form>
      <div v-if="errorMsg" class="alert alert-danger mt-3" role="alert">
        {{ errorMsg }}
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import { useRouter } from 'vue-router'
import { ref } from 'vue'

export default {
  name: 'Login',
  setup() {
    const router = useRouter()
    const email = ref('')
    const password = ref('')
    const errorMsg = ref("")

    const handleLogin = async () => {
      errorMsg.value = "";
      try {
        const response = await axios.post('http://127.0.0.1:5000/login', {
          email: email.value,
          password: password.value,
        })
        if (response.status === 200) {
        const { access_token, role, user_id } = response.data
        localStorage.setItem('token', access_token)
        localStorage.setItem('role', role)
        localStorage.setItem('user_id', user_id)
        if (role === 'admin') {
          router.push('/admin')
        } else if (role === 'user') {
          router.push('/user')
          }
        }
      } catch (err) {
        if (err.response && err.response.status === 401) {
          errorMsg.value = err.response.data.msg || 'Invalid credentials.'
        } else if (err.response && err.response.status === 422) {
          router.push('/login');
        } else {
          errorMsg.value = 'An unexpected error occurred.'
        }
      }
    }

    return {
      email,
      password,
      handleLogin,
      errorMsg
    }
  },
}
</script>
