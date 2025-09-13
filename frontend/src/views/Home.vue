<template>
  <div class="container d-flex flex-column justify-content-center align-items-center vh-100">
    <h1 class="mb-5">Vehicle Parking App</h1>
    <div class="d-flex gap-3">
      <router-link to="/login">
        <button class="btn btn-primary btn-lg">Login</button>
      </router-link>
      <router-link to="/register">
        <button class="btn btn-success btn-lg">Register</button>
      </router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: "Home",
};
</script>
