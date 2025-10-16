<template>
  <div>
    <h2>Staff</h2>
    <form @submit.prevent="createStaff" class="form-row">
      <input v-model="form.name" placeholder="Name" required />
      <input v-model.number="form.age" type="number" placeholder="Age" />
      <input v-model="form.position" placeholder="Position" />
      <button type="submit">Add</button>
    </form>
    <div class="muted" v-if="!staff.length">No staff yet. Add your first member.</div>
    <table v-else>
      <thead>
        <tr>
          <th>ID</th>
          <th>Name</th>
          <th>Age</th>
          <th>Position</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="s in staff" :key="s.id">
          <td>{{ s.id }}</td>
          <td>{{ s.name }}</td>
          <td>{{ s.age ?? '-' }}</td>
          <td>{{ s.position ?? '-' }}</td>
          <td style="text-align:right;">
            <button class="danger" @click="remove(s.id)">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const API = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

const staff = ref([])
const form = ref({ name: '', age: null, position: '' })

async function load() {
  const { data } = await axios.get(`${API}/staff`)
  staff.value = data
}

async function createStaff() {
  const payload = { ...form.value }
  await axios.post(`${API}/staff`, payload)
  form.value = { name: '', age: null, position: '' }
  await load()
}

async function remove(id) {
  await axios.delete(`${API}/staff/${id}`)
  await load()
}

onMounted(load)
</script>


