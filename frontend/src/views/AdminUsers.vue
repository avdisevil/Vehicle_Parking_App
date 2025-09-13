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
    <div class="container mt-4">
      <h2 class="text-center mb-4">Admin Users</h2>
      <div v-if="errorMsg" class="alert alert-danger" role="alert">
        {{ errorMsg }}
      </div>
      <div v-if="users.length" style="max-height: 400px; overflow-y: auto;">
        <table class="table table-striped table-bordered">
          <thead class="table-light">
            <tr>
              <th>ID</th>
              <th>Full Name</th>
              <th>Email</th>
              <th>Address</th>
              <th>Pincode</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in users" :key="user.id">
              <td>{{ user.id }}</td>
              <td>{{ user.full_name }}</td>
              <td>{{ user.email }}</td>
              <td>{{ user.address }}</td>
              <td>{{ user.pincode }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else-if="!errorMsg" class="text-center text-muted">No users found.</div>
    </div>
  </div>
</template>

<script>
import { useRouter } from 'vue-router'
import { ref, onMounted } from 'vue'
import axios from 'axios'

export default {
  name: 'AdminUsers',
  setup() {
    const router = useRouter();
    const users = ref([])
    const errorMsg = ref("")

    const logout = () => {
      localStorage.removeItem('token');
      localStorage.removeItem('role');
      localStorage.removeItem('user_id');
      router.push('/login');
    };

    const fetchUsers = async () => {
      errorMsg.value = ""
      try {
        const token = localStorage.getItem('token')
        const response = await axios.get('http://127.0.0.1:5000/admin/registered_users', {
          headers: { Authorization: `Bearer ${token}` }
        })
        if (response.status === 200) {
          users.value = response.data
        }
      } catch (err) {
        if (err.response && err.response.status === 400) {
          errorMsg.value = err.response.data.msg || 'Error fetching users.'
        } else if (err.response && (err.response.status === 403 || err.response.status === 422)) {
          logout()
        } else {
          errorMsg.value = 'An unexpected error occurred.'
        }
      }
    }

    onMounted(fetchUsers)

    return { users, errorMsg, logout }
  }
}
</script> 