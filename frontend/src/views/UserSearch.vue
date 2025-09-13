<template>
  <div>
    <nav class="navbar navbar-expand navbar-light bg-light mb-4">
      <div class="container-fluid">
        <div class="mx-auto d-flex align-items-center">
          <router-link class="nav-link px-3" to="/user">Home</router-link>
          <router-link class="nav-link px-3" to="/user/search">Search</router-link>
          <router-link class="nav-link px-3" to="/user/summary">Summary</router-link>
          <a class="nav-link px-3" href="#" @click.prevent="logout">Logout</a>
        </div>
      </div>
    </nav>
    <div class="container mt-5">
      <h2 class="text-center mb-4">Search Parking Lot</h2>
      <form class="row g-3 justify-content-center mb-4" @submit.prevent="handleSearch">
        <div class="col-md-6">
          <input v-model="searchQuery" type="text" class="form-control" placeholder="Search Parking Lot by Location / Pincode" required />
        </div>
        <div class="col-auto">
          <button type="submit" class="btn btn-primary">Search</button>
        </div>
      </form>
      <div v-if="errorMsg" class="alert alert-danger" role="alert">
        {{ errorMsg }}
      </div>
      <div v-if="lots.length" style="max-height: 400px; overflow-y: auto;">
        <table class="table table-striped table-bordered">
          <thead class="table-light">
            <tr>
              <th>ID</th>
              <th>Address</th>
              <th>Price (per hour)</th>
              <th>Available Spots</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="lot in lots" :key="lot.id">
              <td>{{ lot.id }}</td>
              <td>{{ lot.address }}</td>
              <td>{{ lot.price }}</td>
              <td>{{ lot.available_spots }}</td>
              <td>
                <button v-if="lot.available_spots > 0" class="btn btn-success btn-sm" @click="openReserveModal(lot.id)">Book</button>
                <button v-else class="btn btn-secondary btn-sm" disabled>Full</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else-if="searched && !errorMsg" class="text-center text-muted">No lots found.</div>

      <!-- Reserve Modal -->
      <div v-if="showReserveModal" class="modal fade show d-block" tabindex="-1" style="background: rgba(0,0,0,0.5);">
        <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">Reserve Parking Spot</h5>
              <button type="button" class="btn-close" @click="closeReserveModal"></button>
            </div>
            <div class="modal-body">
              <form @submit.prevent="handleReserve">
                <div class="mb-3">
                  <label class="form-label">Lot ID</label>
                  <input type="text" class="form-control" :value="reserveLotId" readonly />
                </div>
                <div class="mb-3">
                  <label class="form-label">User ID</label>
                  <input type="text" class="form-control" :value="userId" readonly />
                </div>
                <div class="mb-3">
                  <label class="form-label">Vehicle No</label>
                  <input v-model="vehicleNo" type="text" class="form-control" required />
                </div>
                <div v-if="reserveError" class="alert alert-danger" role="alert">
                  {{ reserveError }}
                </div>
                <div class="modal-footer">
                  <button type="button" class="btn btn-secondary" @click="closeReserveModal">Cancel</button>
                  <button type="submit" class="btn btn-primary">Reserve</button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
      <!-- End Reserve Modal -->
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

export default {
  name: 'UserSearch',
  setup() {
    const router = useRouter()
    const searchQuery = ref("")
    const lots = ref([])
    const errorMsg = ref("")
    const searched = ref(false)

    // Reserve Modal State
    const showReserveModal = ref(false)
    const reserveLotId = ref(null)
    const userId = ref(localStorage.getItem('user_id') || '')
    const vehicleNo = ref("")
    const reserveError = ref("")

    const openReserveModal = (lotId) => {
      reserveLotId.value = lotId
      vehicleNo.value = ""
      reserveError.value = ""
      showReserveModal.value = true
    }

    const closeReserveModal = () => {
      showReserveModal.value = false
      reserveError.value = ""
      reserveLotId.value = null
      vehicleNo.value = ""
    }

    const logout = () => {
      localStorage.removeItem('token');
      localStorage.removeItem('role');
      localStorage.removeItem('user_id');
      router.push('/login');
    }

    const handleSearch = async () => {
      errorMsg.value = ""
      lots.value = []
      searched.value = false
      try {
        const token = localStorage.getItem('token')
        const response = await axios.get('http://127.0.0.1:5000/search_lots', {
          headers: { Authorization: `Bearer ${token}` },
          params: { search_query: searchQuery.value }
        })
        if (response.status === 200) {
          lots.value = response.data
          searched.value = true
        }
      } catch (err) {
        searched.value = true
        if (err.response && err.response.status === 400) {
          errorMsg.value = err.response.data.msg || 'Error searching for lots.'
        } else if (err.response && (err.response.status === 403 || err.response.status === 422)) {
          logout()
        } else {
          errorMsg.value = 'An unexpected error occurred.'
        }
      }
    }

    const handleReserve = async () => {
      reserveError.value = ""
      try {
        const token = localStorage.getItem('token')
        const response = await axios.post('http://127.0.0.1:5000/reserve', {
          lot_id: reserveLotId.value,
          vehicle_no: vehicleNo.value
        }, {
          headers: { Authorization: `Bearer ${token}` }
        })
        if (response.status === 201) {
          closeReserveModal()
          await handleSearch() // Refresh the lots after successful reservation
        }
      } catch (err) {
        if (err.response && (err.response.status === 400 || err.response.status === 404)) {
          reserveError.value = err.response.data.msg || 'Reservation failed.'
        } else if (err.response && (err.response.status === 403 || err.response.status === 422)) {
          logout()
        } else {
          reserveError.value = 'An unexpected error occurred.'
        }
      }
    }

    return {
      searchQuery, lots, errorMsg, searched, handleSearch, logout,
      showReserveModal, reserveLotId, userId, vehicleNo, reserveError,
      openReserveModal, closeReserveModal, handleReserve
    }
  }
}
</script> 