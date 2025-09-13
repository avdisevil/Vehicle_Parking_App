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
      <h2 class="text-center mb-4">User Summary</h2>
      <div v-if="errorMsg" class="alert alert-danger" role="alert">
        {{ errorMsg }}
      </div>
      <div v-if="successMsg" class="alert alert-success" role="alert">
        {{ successMsg }}
      </div>
      <div v-if="summary" class="row">
        <div class="col-md-8">
          <div class="card">
            <div class="card-body">
              <h5 class="card-title">Reservation Statistics</h5>
              <canvas ref="chartCanvas"></canvas>
            </div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="card mb-3">
            <div class="card-body">
              <h5 class="card-title">Summary</h5>
              <div class="mb-3">
                <h6>Total Amount Spent</h6>
                <p class="h4 text-success">₹{{ summary.total_spent || 0 }}</p>
              </div>
            </div>
          </div>
          <div class="card">
            <div class="card-body">
              <h5 class="card-title">Export all reservation details as csv to your mail</h5>
              <button class="btn btn-primary w-100" @click="handleExportCSV">Export Data as CSV</button>
            </div>
          </div>
        </div>
      </div>
      <div v-else-if="!errorMsg" class="text-center text-muted">Loading summary...</div>
    </div>
  </div>
</template>

<script>
import { useRouter } from 'vue-router'
import { ref, onMounted, nextTick } from 'vue'
import axios from 'axios'
import Chart from 'chart.js/auto'

export default {
  name: 'UserSummary',
  setup() {
    const router = useRouter();
    const summary = ref(null)
    const errorMsg = ref("")
    const successMsg = ref("")
    const chartCanvas = ref(null)
    let chart = null

    const logout = () => {
      localStorage.removeItem('token');
      localStorage.removeItem('role');
      localStorage.removeItem('user_id');
      router.push('/login');
    };

    const fetchSummary = async () => {
      errorMsg.value = ""
      try {
        const token = localStorage.getItem('token')
        const response = await axios.get('http://127.0.0.1:5000/user/summary', {
          headers: { Authorization: `Bearer ${token}` }
        })
        if (response.status === 200) {
          summary.value = response.data
          await nextTick()
          createChart()
        }
      } catch (err) {
        if (err.response && err.response.status === 400) {
          errorMsg.value = err.response.data.msg || 'Error fetching summary.'
        } else if (err.response && (err.response.status === 403 || err.response.status === 422)) {
          logout()
        } else {
          errorMsg.value = 'An unexpected error occurred.'
        }
      }
    }

    const handleExportCSV = async () => {
      errorMsg.value = ""
      successMsg.value = ""
      try {
        const token = localStorage.getItem('token')
        const response = await axios.post('http://127.0.0.1:5000/export_parking_csv', {}, {
          headers: { Authorization: `Bearer ${token}` }
        })
        if (response.status === 202) {
          successMsg.value = response.data.msg || 'Your parking history is being processed. You\'ll receive an email once ready.'
        }
      } catch (err) {
        if (err.response && err.response.status === 403) {
          logout()
        } else {
          errorMsg.value = 'Error exporting CSV. Please try again.'
        }
      }
    }

    const createChart = () => {
      if (chart) {
        chart.destroy()
      }
      
      const ctx = chartCanvas.value.getContext('2d')
      chart = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: ['Active Reservations', 'Checked Out Reservations'],
          datasets: [{
            label: 'Number of Reservations',
            data: [summary.value.active_reservations, summary.value.checked_out_reservations],
            backgroundColor: [
              'rgba(255, 99, 132, 0.2)',
              'rgba(54, 162, 235, 0.2)'
            ],
            borderColor: [
              'rgba(255, 99, 132, 1)',
              'rgba(54, 162, 235, 1)'
            ],
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          plugins: {
            legend: {
              display: false
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                stepSize: 1
              }
            }
          }
        }
      })
    }

    onMounted(fetchSummary)

    return { summary, errorMsg, successMsg, logout, chartCanvas, handleExportCSV }
  }
}
</script> 