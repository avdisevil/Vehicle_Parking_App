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
      <h2 class="text-center mb-4">Recent Parking History</h2>
      <div v-if="errorMsg" class="alert alert-danger" role="alert">
        {{ errorMsg }}
      </div>
      <div v-if="reservations.length" style="max-height: 400px; overflow-y: auto;">
        <table class="table table-striped table-bordered">
          <thead class="table-light">
            <tr>
              <th>Reservation ID</th>
              <th>Location</th>
              <th>Vehicle No</th>
              <th>Parking Time</th>
              <th>Leaving Time</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="res in reservations" :key="res.reservation_id">
              <td>{{ res.reservation_id }}</td>
              <td>{{ res.prime_location }}</td>
              <td>{{ res.vehicle_no }}</td>
              <td>{{ formatDate(res.parking_time) }}</td>
              <td>{{ res.leaving_time ? formatDate(res.leaving_time) : '-' }}</td>
              <td>
                <button v-if="!res.leaving_time" class="btn btn-warning btn-sm" @click="openReleaseModal(res)">Release</button>
                <button v-else class="btn btn-success btn-sm" disabled>Checked Out</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else-if="!errorMsg" class="text-center text-muted">No reservations found.</div>

      <!-- Release Modal -->
      <div v-if="showReleaseModal" class="modal fade show d-block" tabindex="-1" style="background: rgba(0,0,0,0.5);">
        <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">Release Parking Spot</h5>
              <button type="button" class="btn-close" @click="closeReleaseModal"></button>
            </div>
            <div class="modal-body">
              <form @submit.prevent="handleRelease">
                <div class="mb-3">
                  <label class="form-label">Spot ID</label>
                  <input type="text" class="form-control" :value="releaseData.spot_id" readonly />
                </div>
                <div class="mb-3">
                  <label class="form-label">Vehicle No</label>
                  <input type="text" class="form-control" :value="releaseData.vehicle_no" readonly />
                </div>
                <div class="mb-3">
                  <label class="form-label">Parking Time</label>
                  <input type="text" class="form-control" :value="formatDate(releaseData.parking_time)" readonly />
                </div>
                <div class="mb-3">
                  <label class="form-label">Leaving Time</label>
                  <input type="text" class="form-control" :value="releaseData.leaving_time ? formatDate(releaseData.leaving_time) : '-'" readonly />
                </div>
                <div class="mb-3">
                  <label class="form-label">Cost</label>
                  <input type="text" class="form-control" :value="releaseData.cost !== undefined ? releaseData.cost : '-'" readonly />
                </div>
                <div v-if="releaseError" class="alert alert-danger" role="alert">
                  {{ releaseError }}
                </div>
                <div class="modal-footer">
                  <button type="button" class="btn btn-secondary" @click="closeReleaseModal">Cancel</button>
                  <button type="submit" class="btn btn-primary">Release</button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
      <!-- End Release Modal -->
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

export default {
  name: 'UserDashboard',
  setup() {
    const reservations = ref([])
    const errorMsg = ref("")
    const router = useRouter()

    // Release Modal State
    const showReleaseModal = ref(false)
    const releaseData = ref({})
    const releaseError = ref("")

    const openReleaseModal = (res) => {
      // Calculate leaving_time and cost in frontend
      const leavingTime = new Date().toISOString()
      let cost = '-'
      console.log(res)
      if (res.parking_time && res.price !== undefined) {
        const parkingTime = new Date(res.parking_time)
        const hours = Math.ceil((new Date(leavingTime) - parkingTime) / 3600000)
        cost = hours * res.price
        console.log(cost)
      }
      releaseData.value = {
        ...res,
        leaving_time: leavingTime,
        cost
      }
      releaseError.value = ''
      showReleaseModal.value = true
    }

    const closeReleaseModal = () => {
      showReleaseModal.value = false
      releaseError.value = ''
      releaseData.value = {}
    }

    const logout = () => {
      localStorage.removeItem('token');
      localStorage.removeItem('role');
      localStorage.removeItem('user_id');
      router.push('/login');
    }

    const fetchReservations = async () => {
      errorMsg.value = ""
      try {
        const token = localStorage.getItem('token')
        const response = await axios.get('http://127.0.0.1:5000/my_reservations', {
          headers: { Authorization: `Bearer ${token}` }
        })
        if (response.status === 200) {
          reservations.value = response.data
        }
      } catch (err) {
        if (err.response && err.response.status === 400) {
          errorMsg.value = err.response.data.msg || 'Error fetching reservations.'
        } else if (err.response && (err.response.status === 403 || err.response.status === 422)) {
          logout()
        } else {
          errorMsg.value = 'An unexpected error occurred.'
        }
      }
    }

    const handleRelease = async () => {
      releaseError.value = ''
      try {
        const token = localStorage.getItem('token')
        const response = await axios.post(`http://127.0.0.1:5000/release/${releaseData.value.reservation_id}`, {}, {
          headers: { Authorization: `Bearer ${token}` }
        })
        if (response.status === 200) {
          // Update cost and leaving_time in modal
          releaseData.value.cost = response.data.cost
          releaseData.value.leaving_time = new Date().toISOString()
          await fetchReservations()
          closeReleaseModal()
        }
      } catch (err) {
        if (err.response && err.response.status === 404) {
          releaseError.value = 'Reservation not found.'
        } else if (err.response && err.response.status === 400) {
          releaseError.value = err.response.data.msg || 'Reservation already released.'
        } else if (err.response && (err.response.status === 403 || err.response.status === 422)) {
          logout()
        } else if (err.response && err.response.status === 500) {
          releaseError.value = 'Release failed.'
        } else {
          releaseError.value = 'An unexpected error occurred.'
        }
      }
    }

    const formatDate = (dateStr) => {
      if (!dateStr) return ''
      const d = new Date(dateStr)
      return d.toLocaleString()
    }

    onMounted(fetchReservations)

    return {
      reservations, errorMsg, logout, formatDate,
      showReleaseModal, releaseData, releaseError, openReleaseModal, closeReleaseModal, handleRelease
    }
  }
}
</script>