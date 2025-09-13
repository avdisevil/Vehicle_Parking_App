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
    <div class="container mt-5">
      <h2 class="text-center mb-4">Admin Summary</h2>
      <div v-if="errorMsg" class="alert alert-danger" role="alert">
        {{ errorMsg }}
      </div>
      <div v-if="summary" class="row">
        <div class="col-md-8">
          <div class="card mb-3">
            <div class="card-body">
              <h5 class="card-title">Parking Spots Occupancy</h5>
              <canvas ref="barChartCanvas"></canvas>
            </div>
          </div>
          <div class="card">
            <div class="card-body">
              <h5 class="card-title">Lot Shares</h5>
              <canvas ref="pieChartCanvas"></canvas>
            </div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="card">
            <div class="card-body">
              <h5 class="card-title">Total Revenue</h5>
              <p class="h4 text-success">₹{{ summary.total_revenue || 0 }}</p>
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
  name: 'AdminSummary',
  setup() {
    const router = useRouter();
    const summary = ref(null)
    const errorMsg = ref("")
    const barChartCanvas = ref(null)
    const pieChartCanvas = ref(null)
    let barChart = null
    let pieChart = null

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
        const response = await axios.get('http://127.0.0.1:5000/admin/summary', {
          headers: { Authorization: `Bearer ${token}` }
        })
        if (response.status === 200) {
          summary.value = response.data
          await nextTick()
          createBarChart()
          createPieChart()
        }
      } catch (err) {
        if (err.response && err.response.status === 400) {
          errorMsg.value = err.response.data.msg || 'Error fetching admin summary.'
        } else if (err.response && (err.response.status === 403 || err.response.status === 422)) {
          logout()
        } else {
          errorMsg.value = 'An unexpected error occurred.'
        }
      }
    }

    const createBarChart = () => {
      if (barChart) barChart.destroy()
      const ctx = barChartCanvas.value.getContext('2d')
      barChart = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: ['Occupied', 'Available'],
          datasets: [{
            label: 'Spots',
            data: [summary.value.occupied, summary.value.available],
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
            legend: { display: false }
          },
          scales: {
            y: {
              beginAtZero: true,
              ticks: { stepSize: 1 }
            }
          }
        }
      })
    }

    const createPieChart = () => {
      if (pieChart) pieChart.destroy()
      const ctx = pieChartCanvas.value.getContext('2d')
      pieChart = new Chart(ctx, {
        type: 'pie',
        data: {
          labels: summary.value.lot_shares.map(l => l.lot_name),
          datasets: [{
            label: 'Reserved Spots',
            data: summary.value.lot_shares.map(l => l.reserved_spots),
            backgroundColor: [
              'rgba(255, 99, 132, 0.5)',
              'rgba(54, 162, 235, 0.5)',
              'rgba(255, 206, 86, 0.5)',
              'rgba(75, 192, 192, 0.5)',
              'rgba(153, 102, 255, 0.5)',
              'rgba(255, 159, 64, 0.5)'
            ],
            borderColor: [
              'rgba(255, 99, 132, 1)',
              'rgba(54, 162, 235, 1)',
              'rgba(255, 206, 86, 1)',
              'rgba(75, 192, 192, 1)',
              'rgba(153, 102, 255, 1)',
              'rgba(255, 159, 64, 1)'
            ],
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          plugins: {
            legend: { position: 'bottom' }
          }
        }
      })
    }

    onMounted(fetchSummary)

    return { summary, errorMsg, logout, barChartCanvas, pieChartCanvas }
  }
}
</script> 
<style scoped>
body, .container {
  background-color: #f7f7f7;
  color: #34495e;
}
.navbar {
  background-color: #2c3e50 !important;
}
.navbar-brand, .nav-link {
  color: #ffffff !important;
}
.nav-link:hover {
  color: #3498db !important;
}
h2, h5, h4 {
  color: #3498db;
}
.card {
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(44, 62, 80, 0.05);
  border: none;
}
.card-title {
  color: #34495e;
}
.btn-primary {
  background-color: #3498db;
  border-color: #3498db;
  color: #fff;
}
.btn-primary:hover {
  background-color: #2980b9;
  border-color: #2980b9;
}
.btn-success {
  background-color: #2ecc71;
  border-color: #2ecc71;
  color: #fff;
}
.btn-success:hover {
  background-color: #27ae60;
  border-color: #27ae60;
}
.btn-danger {
  background-color: #e74c3c;
  border-color: #e74c3c;
  color: #fff;
}
.btn-danger:hover {
  background-color: #c0392b;
  border-color: #c0392b;
}
.btn-warning {
  background-color: #f1c40f;
  border-color: #f1c40f;
  color: #fff;
}
.btn-warning:hover {
  background-color: #f39c12;
  border-color: #f39c12;
}
.btn:disabled {
  background-color: #bdc3c7 !important;
  color: #7f8c8d !important;
  border-color: #bdc3c7 !important;
}
.form-control:focus {
  border-color: #8e44ad;
  box-shadow: 0 0 0 2px rgba(142, 68, 173, 0.2);
}
.alert-danger {
  background-color: #e74c3c;
  color: #fff;
  border-color: #c0392b;
}
.alert-success {
  background-color: #2ecc71;
  color: #fff;
  border-color: #27ae60;
}
.alert-warning {
  background-color: #f1c40f;
  color: #34495e;
  border-color: #f39c12;
}
.table {
  background-color: #ffffff;
  color: #34495e;
}
.table th {
  background-color: #3498db;
  color: #fff;
}
.table-striped tbody tr:nth-of-type(odd) {
  background-color: #f7f7f7;
}
.table-bordered {
  border: 1px solid #bdc3c7;
}
.text-success {
  color: #2ecc71 !important;
}
.text-danger {
  color: #e74c3c !important;
}
.text-warning {
  color: #f1c40f !important;
}
.text-info {
  color: #3498db !important;
}
.text-muted {
  color: #95a5a6 !important;
}
.badge.bg-success {
  background-color: #2ecc71 !important;
  color: #fff !important;
}
.badge.bg-danger {
  background-color: #e74c3c !important;
  color: #fff !important;
}
.badge.bg-warning {
  background-color: #f1c40f !important;
  color: #34495e !important;
}
.badge.bg-info {
  background-color: #3498db !important;
  color: #fff !important;
}
.form-label {
  color: #34495e;
}
.modal-content {
  background-color: #ffffff;
  border-radius: 8px;
}
.modal-header {
  background-color: #2c3e50;
  color: #fff;
  border-bottom: 1px solid #3498db;
}
.modal-title {
  color: #3498db;
}
.btn-close {
  color: #34495e;
}
</style>