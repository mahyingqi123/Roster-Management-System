<template>
  <div class="container">
    <div class="card" style="margin-bottom:16px;">
      <h1>Roster Management</h1>
      <p class="muted">Manage staff, schedule shifts, and view statistics.</p>
    </div>
    <div class="row">
      <div class="card">
        <StaffManagement />
      </div>
      <div class="card">
        <RosterDisplay />
      </div>
    </div>
  </div>

</template>

<script setup>
import StaffManagement from './components/StaffManagement.vue'
import RosterDisplay from './components/RosterDisplay.vue'
</script>


