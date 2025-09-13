<template>
  <div>
    <nav class="navbar navbar-expand navbar-light bg-light mb-4">
      <div class="container-fluid">
        <router-link class="navbar-brand" to="/admin">Admin</router-link>
        <div class="collapse navbar-collapse">
          <ul class="navbar-nav me-auto mb-2 mb-lg-0">
            <li class="nav-item">
              <router-link class="nav-link" to="/admin">Home</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/admin/users">Users</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/admin/search">Search</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/admin/summary">Summary</router-link>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="#" @click.prevent="logout">Logout</a>
            </li>
          </ul>
        </div>
      </div>
    </nav>
    <div class="container d-flex flex-column justify-content-center align-items-center vh-50">
      <h2 class="text-center">Admin Search</h2>
    </div>
    <div class="container mt-5">
      <form class="row g-3 justify-content-center mb-4" @submit.prevent="handleSearch">
        <div class="col-md-6">
          <input v-model="searchQuery" type="text" class="form-control" placeholder="Search Users by Name" required />
        </div>
        <div class="col-auto">
          <button type="submit" class="btn btn-primary">Search</button>
        </div>
      </form>
      <div v-if="errorMsg" class="alert alert-danger" role="alert">
        {{ errorMsg }}
      </div>
      <div v-if="users.length" style="max-height: 400px; overflow-y: auto;">
        <table class="table table-striped table-bordered">
          <thead class="table-light">
            <tr>
              <th>User ID</th>
              <th>Email</th>
              <th>Name</th>
              <th>Address</th>
              <th>Pincode</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in users" :key="user.id">
              <td>{{ user.id }}</td>
              <td>{{ user.email }}</td>
              <td>{{ user.full_name }}</td>
              <td>{{ user.address }}</td>
              <td>{{ user.pincode }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else-if="searched && !errorMsg" class="text-center text-muted">No users found.</div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

export default {
  name: 'AdminSearch',
  setup() {
    const router = useRouter()
    const searchQuery = ref("")
    const users = ref([])
    const errorMsg = ref("")
    const searched = ref(false)

    const logout = () => {
      localStorage.removeItem('token');
      localStorage.removeItem('role');
      localStorage.removeItem('user_id');
      router.push('/login');
    };
    
    const handleSearch = async () => {
      errorMsg.value = ""
      users.value = []
      searched.value = false
      try {
        const token = localStorage.getItem('token')
        const response = await axios.get('http://127.0.0.1:5000/admin/search', {
          headers: { Authorization: `Bearer ${token}` },
          params: { search_query: searchQuery.value }
        })
        if (response.status === 200) {
          users.value = response.data
          searched.value = true
        }
      } catch (err) {
        searched.value = true
        if (err.response && err.response.status === 400) {
          errorMsg.value = err.response.data.msg || 'Error searching for users.'
        } else if (err.response && (err.response.status === 403 || err.response.status === 422)) {
          logout()
        } else {
          errorMsg.value = 'An unexpected error occurred.'
        }
      }
    }
    return {
      searchQuery, users, errorMsg, searched, handleSearch, logout
    }
  }
}
</script> 