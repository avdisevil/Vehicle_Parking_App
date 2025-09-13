<template>
  <div class="container d-flex flex-column justify-content-center align-items-center vh-100">
    <router-link to="/" class="mb-4 w-100 d-flex justify-content-center">
      <button class="btn btn-secondary">Home</button>
    </router-link>
    <div class="w-100" style="max-width: 400px;">
      <h2 class="mb-4 text-center">Register</h2>
      <form @submit.prevent="handleRegister">
        <div class="mb-3">
          <label for="fullName" class="form-label">Full Name</label>
          <input type="text" class="form-control" id="fullName" v-model="fullName" required />
        </div>
        <div class="mb-3">
          <label for="email" class="form-label">Email</label>
          <input type="email" class="form-control" id="email" v-model="email" required />
        </div>
        <div class="mb-3">
          <label for="password" class="form-label">Password</label>
          <input type="password" class="form-control" id="password" v-model="password" required />
        </div>
        <div class="mb-3">
          <label for="address" class="form-label">Address</label>
          <input type="text" class="form-control" id="address" v-model="address" required />
        </div>
        <div class="mb-3">
          <label for="pincode" class="form-label">Pincode</label>
          <input type="text" class="form-control" id="pincode" v-model="pincode" required />
        </div>
        <button type="submit" class="btn btn-success w-100">Register</button>
      </form>
      <div v-if="errorMsg" class="alert alert-danger mt-3" role="alert">
        {{ errorMsg }}
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

export default {
  name: "Register",
  setup() {
    const fullName = ref("");
    const email = ref("");
    const password = ref("");
    const address = ref("");
    const pincode = ref("");
    const errorMsg = ref("");
    const router = useRouter();

    const clearFields = () => {
      fullName.value = "";
      email.value = "";
      password.value = "";
      address.value = "";
      pincode.value = "";
    };

    const handleRegister = async () => {
      errorMsg.value = "";
      try {
        const response = await axios.post('http://127.0.0.1:5000/register', {
          email: email.value,
          password: password.value,
          full_name: fullName.value,
          address: address.value,
          pincode: pincode.value
        });
        if (response.status === 201) {
          router.push('/login');
        }
      } catch (err) {
        if (err.response && err.response.status === 400) {
          errorMsg.value = err.response.data.msg || 'Registration failed.';
          clearFields();
        } else if (err.response && err.response.status === 422) {
          router.push('/login');
        } else {
          errorMsg.value = 'An unexpected error occurred.';
        }
      }
    };

    return {
      fullName,
      email,
      password,
      address,
      pincode,
      handleRegister,
      errorMsg
    };
  },
};
</script>
