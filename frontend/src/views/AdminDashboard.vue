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
    <div class="container">
      <h2 class="text-center mb-4">Parking Lots</h2>
      <div v-if="errorMsg" class="alert alert-danger" role="alert">
        {{ errorMsg }}
      </div>
      <div class="row">
        <div v-for="lot in lots" :key="lot.id" class="col-md-4 mb-4">
          <div class="card h-100">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-center mb-2">
                <span><strong>{{ lot.prime_location }}</strong></span>
                <span class="badge bg-info">{{ lot.price }} ₹/hr</span>
              </div>
              <div class="mb-2 text-success">
                <span>Total Spots: {{ lot.total_spots }}</span>
              </div>
              <div class="d-flex flex-wrap" style="gap: 6px;">
                <span
                  v-for="(n, idx) in lot.total_spots"
                  :key="idx"
                  class="badge"
                  :class="(lot.total_spots - lot.available_spots) > idx ? 'bg-danger' : 'bg-success'"
                  style="cursor:pointer;"
                  @click="openSpotModal(idx+1, lot.id)"
                >
                  {{ (lot.total_spots - lot.available_spots) > idx ? 'O' : 'A' }}
                </span>
              </div>
              <div class="mt-2 d-flex justify-content-end" style="gap: 8px;">
                <button class="btn btn-sm btn-primary" @click="openEditLot(lot)">Edit</button>
                <button class="btn btn-sm btn-danger" @click="openDeleteLot(lot)">Delete</button>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="d-flex justify-content-center mt-4">
        <button class="btn btn-info btn-lg" @click="showAddLot = true">+ Add Lot</button>
      </div>

      <!-- Add Lot Modal -->
      <div v-if="showAddLot" class="modal fade show d-block" tabindex="-1" style="background: rgba(0,0,0,0.5);">
        <div class="modal-dialog modal-lg modal-dialog-centered">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">New Parking Lot</h5>
              <button type="button" class="btn-close" @click="closeAddLot"></button>
            </div>
            <div class="modal-body">
              <form @submit.prevent="handleAddLot">
                <div class="mb-3">
                  <label class="form-label">Prime Location</label>
                  <input v-model="newLot.prime_location" type="text" class="form-control" required />
                </div>
                <div class="mb-3">
                  <label class="form-label">Address</label>
                  <input v-model="newLot.address" type="text" class="form-control" required />
                </div>
                <div class="mb-3">
                  <label class="form-label">Pincode</label>
                  <input v-model="newLot.pincode" type="text" class="form-control" required />
                </div>
                <div class="mb-3">
                  <label class="form-label">Price (per hour)</label>
                  <input v-model.number="newLot.price" type="number" class="form-control" required min="1" />
                </div>
                <div class="mb-3">
                  <label class="form-label">Maximum Spots</label>
                  <input v-model.number="newLot.total_spots" type="number" class="form-control" required min="1" />
                </div>
                <div v-if="addLotError" class="alert alert-danger" role="alert">
                  {{ addLotError }}
                </div>
                <div class="modal-footer">
                  <button type="button" class="btn btn-secondary" @click="closeAddLot">Cancel</button>
                  <button type="submit" class="btn btn-primary">Add</button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
      <!-- End Add Lot Modal -->

      <!-- Edit Lot Modal -->
      <div v-if="showEditLot" class="modal fade show d-block" tabindex="-1" style="background: rgba(0,0,0,0.5);">
        <div class="modal-dialog modal-lg modal-dialog-centered">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">Edit Parking Lot</h5>
              <button type="button" class="btn-close" @click="closeEditLot"></button>
            </div>
            <div class="modal-body">
              <form @submit.prevent="handleEditLot">
                <div class="mb-3">
                  <label class="form-label">Prime Location</label>
                  <input v-model="editLot.prime_location" type="text" class="form-control" required />
                </div>
                <div class="mb-3">
                  <label class="form-label">Address</label>
                  <input v-model="editLot.address" type="text" class="form-control" required />
                </div>
                <div class="mb-3">
                  <label class="form-label">Pincode</label>
                  <input v-model="editLot.pincode" type="text" class="form-control" required />
                </div>
                <div class="mb-3">
                  <label class="form-label">Price (per hour)</label>
                  <input v-model.number="editLot.price" type="number" class="form-control" required min="1" />
                </div>
                <div class="mb-3">
                  <label class="form-label">Maximum Spots</label>
                  <input v-model.number="editLot.total_spots" type="number" class="form-control" readonly />
                </div>
                <div v-if="editLotError" class="alert alert-danger" role="alert">
                  {{ editLotError }}
                </div>
                <div class="modal-footer">
                  <button type="button" class="btn btn-secondary" @click="closeEditLot">Cancel</button>
                  <button type="submit" class="btn btn-primary">Update</button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
      <!-- End Edit Lot Modal -->

      <!-- Delete Lot Modal -->
      <div v-if="showDeleteLot" class="modal fade show d-block" tabindex="-1" style="background: rgba(0,0,0,0.5);">
        <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">Delete Parking Lot</h5>
              <button type="button" class="btn-close" @click="closeDeleteLot"></button>
            </div>
            <div class="modal-body">
              <p>Are you sure you want to delete Parking#{{ deleteLot.id }}?</p>
              <div v-if="deleteLotError" class="alert alert-danger" role="alert">
                {{ deleteLotError }}
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" @click="closeDeleteLot">Cancel</button>
              <button type="button" class="btn btn-danger" @click="handleDeleteLot">Confirm</button>
            </div>
          </div>
        </div>
      </div>
      <!-- End Delete Lot Modal -->

      <!-- Spot Details Modal -->
      <div v-if="showSpotModal" class="modal fade show d-block" tabindex="-1" style="background: rgba(0,0,0,0.5);">
        <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">Spot Details</h5>
              <button type="button" class="btn-close" @click="closeSpotModal"></button>
            </div>
            <div class="modal-body">
              <div v-if="spotModalLoading" class="text-center mb-2">
                <span class="spinner-border"></span>
              </div>
              <div v-if="spotModalError" class="alert alert-danger" role="alert">
                {{ spotModalError }}
              </div>
              <div v-if="!spotModalLoading && !spotModalError">
                <div class="mb-2"><strong>Spot ID:</strong> {{ spotDetails.spot_id }}</div>
                <div class="mb-2"><strong>Status:</strong> {{ spotDetails.status }}</div>
                <div v-if="spotDetails.reservation">
                  <div class="mb-2"><strong>Vehicle Number:</strong> {{ spotDetails.reservation.vehicle_no || '-' }}</div>
                  <div class="mb-2"><strong>Parking Time:</strong> {{ spotDetails.reservation.parking_time }}</div>
                  <div class="mb-2"><strong>Reservation ID:</strong> {{ spotDetails.reservation.reservation_id }}</div>
                </div>
                <div v-else>
                  <div class="mb-2"><strong>Vehicle Number:</strong> -</div>
                  <div class="mb-2"><strong>Parking Time:</strong> -</div>
                  <div class="mb-2"><strong>Reservation ID:</strong> -</div>
                </div>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-danger" :disabled="spotDetails.status !== 'A'" @click="handleDeleteSpot">Delete</button>
              <button type="button" class="btn btn-secondary" @click="closeSpotModal">Cancel</button>
            </div>
          </div>
        </div>
      </div>
      <!-- End Spot Details Modal -->
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

export default {
  name: 'AdminDashboard',
  setup() {
    const lots = ref([])
    const errorMsg = ref("")
    const router = useRouter()

    // Add Lot Modal State
    const showAddLot = ref(false)
    const addLotError = ref("")
    const newLot = ref({
      prime_location: '',
      address: '',
      pincode: '',
      price: '',
      total_spots: ''
    })

    // Edit Lot Modal State
    const showEditLot = ref(false)
    const editLotError = ref("")
    const editLot = ref({
      id: null,
      prime_location: '',
      address: '',
      pincode: '',
      price: '',
      total_spots: ''
    })

    const openEditLot = (lot) => {
      editLot.value = { ...lot }
      showEditLot.value = true
      editLotError.value = ''
    }

    const closeEditLot = () => {
      showEditLot.value = false
      editLotError.value = ''
      editLot.value = {
        id: null,
        prime_location: '',
        address: '',
        pincode: '',
        price: '',
        total_spots: ''
      }
    }

    const closeAddLot = () => {
      showAddLot.value = false
      addLotError.value = ''
      newLot.value = {
        prime_location: '',
        address: '',
        pincode: '',
        price: '',
        total_spots: ''
      }
    }

    // Delete Lot Modal State
    const showDeleteLot = ref(false)
    const deleteLotError = ref("")
    const deleteLot = ref({ id: null })

    const openDeleteLot = (lot) => {
      deleteLot.value = { ...lot }
      showDeleteLot.value = true
      deleteLotError.value = ''
    }

    const closeDeleteLot = () => {
      showDeleteLot.value = false
      deleteLotError.value = ''
      deleteLot.value = { id: null }
    }

    // Spot Modal State
    const showSpotModal = ref(false)
    const spotModalError = ref("")
    const spotModalLoading = ref(false)
    const spotDetails = ref({
      spot_id: '',
      lot_id: '',
      status: '',
      reservation: null
    })
    const selectedLotId = ref(null)
    const selectedSpotNo = ref(null)

    // Spot Modal Handlers
    const openSpotModal = async (spotNo, lotId) => {
      spotModalError.value = ''
      spotModalLoading.value = true
      showSpotModal.value = true
      spotDetails.value = { spot_id: '', lot_id: '', status: '', reservation: null }
      selectedLotId.value = lotId
      selectedSpotNo.value = spotNo
      try {
        const token = localStorage.getItem('token')
        const response = await axios.get(`http://127.0.0.1:5000/admin/spot/${spotNo}/${lotId}`, {
          headers: { Authorization: `Bearer ${token}` }
        })
        if (response.status === 200) {
          spotDetails.value = response.data
        }
      } catch (err) {
        if (err.response && err.response.status === 403) {
          localStorage.removeItem('token');
          localStorage.removeItem('role');
          localStorage.removeItem('user_id');
          router.push('/login');
        } else if (err.response && [400,404,500].includes(err.response.status)) {
          spotModalError.value = err.response.data.msg || 'Error loading spot details.'
        } else {
          spotModalError.value = 'An unexpected error occurred.'
        }
      } finally {
        spotModalLoading.value = false
      }
    }

    const closeSpotModal = () => {
      showSpotModal.value = false
      spotModalError.value = ''
      spotDetails.value = { spot_id: '', lot_id: '', status: '', reservation: null }
      selectedLotId.value = null
      selectedSpotNo.value = null
    }

    const logout = () => {
      localStorage.removeItem('token');
      localStorage.removeItem('role');
      localStorage.removeItem('user_id');
      router.push('/login');
    }

    const fetchLots = async () => {
      errorMsg.value = ""
      try {
        const token = localStorage.getItem('token')
        const response = await axios.get('http://127.0.0.1:5000/admin/parking_lots', {
          headers: { Authorization: `Bearer ${token}` }
        })
        if (response.status === 200) {
          lots.value = response.data
        }
      } catch (err) {
        if (err.response && err.response.status === 400) {
          errorMsg.value = err.response.data.msg || 'Error loading parking lots.'
        } else if (err.response && err.response.status === 403) {
          logout()
        } else if (err.response && err.response.status === 422) {
          logout()
        } else {
          errorMsg.value = 'An unexpected error occurred.'
        }
      }
    }

    const handleAddLot = async () => {
      addLotError.value = ''
      try {
        const token = localStorage.getItem('token')
        const response = await axios.post('http://127.0.0.1:5000/admin/parking_lot', newLot.value, {
          headers: { Authorization: `Bearer ${token}` }
        })
        if (response.status === 201) {
          closeAddLot()
          await fetchLots()
        }
      } catch (err) {
        if (err.response && err.response.status === 400) {
          addLotError.value = err.response.data.msg || 'Error creating parking lot.'
        } else if (err.response && err.response.status === 403) {
          logout()
        } else {
          addLotError.value = 'An unexpected error occurred.'
        }
      }
    }

    const handleEditLot = async () => {
      editLotError.value = ''
      try {
        const token = localStorage.getItem('token')
        const response = await axios.put(`http://127.0.0.1:5000/admin/parking_lot/${editLot.value.id}`, editLot.value, {
          headers: { Authorization: `Bearer ${token}` }
        })
        if (response.status === 200) {
          closeEditLot()
          await fetchLots()
        }
      } catch (err) {
        if (err.response && err.response.status === 400) {
          editLotError.value = err.response.data.msg || 'Error updating parking lot.'
        } else if (err.response && err.response.status === 403) {
          logout()
        } else if (err.response && err.response.status === 404) {
          editLotError.value = 'Lot not found.'
        } else {
          editLotError.value = 'An unexpected error occurred.'
        }
      }
    }

    const handleDeleteLot = async () => {
      deleteLotError.value = ''
      try {
        const token = localStorage.getItem('token')
        const response = await axios.delete(`http://127.0.0.1:5000/admin/parking_lot/${deleteLot.value.id}`, {
          headers: { Authorization: `Bearer ${token}` }
        })
        if (response.status === 200) {
          closeDeleteLot()
          await fetchLots()
        }
      } catch (err) {
        if (err.response && err.response.status === 400) {
          deleteLotError.value = err.response.data.msg || 'Error deleting parking lot.'
        } else if (err.response && err.response.status === 403) {
          logout()
        } else {
          deleteLotError.value = 'An unexpected error occurred.'
        }
      }
    }

    const handleDeleteSpot = async () => {
      spotModalError.value = ''
      try {
        const token = localStorage.getItem('token')
        const response = await axios.delete(`http://127.0.0.1:5000/admin/delete_spot/${spotDetails.value.spot_id}`, {
          headers: { Authorization: `Bearer ${token}` }
        })
        if (response.status === 200) {
          closeSpotModal()
          await fetchLots()
        }
      } catch (err) {
        if (err.response && err.response.status === 403) {
          localStorage.removeItem('token');
          localStorage.removeItem('role');
          localStorage.removeItem('user_id');
          router.push('/login');
        } else if (err.response && [400,404,500].includes(err.response.status)) {
          spotModalError.value = err.response.data.msg || 'Error deleting spot.'
        } else {
          spotModalError.value = 'An unexpected error occurred.'
        }
      }
    }

    onMounted(fetchLots)

    return {
      lots, errorMsg, logout,
      showAddLot, addLotError, newLot, closeAddLot, handleAddLot,
      showEditLot, editLot, editLotError, openEditLot, closeEditLot, handleEditLot,
      showDeleteLot, deleteLot, deleteLotError, openDeleteLot, closeDeleteLot, handleDeleteLot,
      // Spot Modal
      showSpotModal, spotModalError, spotDetails, spotModalLoading, openSpotModal, closeSpotModal, handleDeleteSpot
    }
  }
}
</script>