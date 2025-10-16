<template>
  <div>
    <h2>Roster</h2>
    <div class="form-row">
      <input type="date" v-model="range.start" />
      <input type="date" v-model="range.end" />
      <select v-model="newAssign.shift_type">
        <option value="morning">morning</option>
        <option value="afternoon">afternoon</option>
        <option value="night">night</option>
      </select>
      <input type="date" v-model="newAssign.date" />
      <input type="number" v-model.number="newAssign.staff_id" placeholder="staff_id" />
      <button @click="assign">Assign</button>
      <button class="ghost" @click="load">Refresh</button>
      <button @click="autoSchedule">Auto-Schedule</button>
      <button class="ghost" @click="downloadCsv">Export CSV</button>
    </div>

    <table>
      <thead>
        <tr>
          <th>Date</th>
          <th>Shift</th>
          <th>Staff</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="r in roster" :key="r.assignment_id">
          <td>{{ r.date }}</td>
          <td>{{ r.shift_type }}</td>
          <td>({{ r.staff_id }}) {{ r.staff_name }}</td>
          <td style="text-align:right;"><button class="danger" @click="unassign(r.assignment_id)">Remove</button></td>
        </tr>
      </tbody>
    </table>

    <h3 style="margin-top:16px;">Coverage</h3>
    <div class="form-row">
      <label class="muted">Pivot by:</label>
      <select v-model="pivotMode">
        <option value="day">Day</option>
        <option value="week">Week</option>
      </select>
    </div>
    <table>
      <thead>
        <tr>
          <th>{{ pivotMode === 'day' ? 'Date' : 'Week' }}</th>
          <th v-for="st in shiftTypes" :key="st">{{ st }}</th>
          <th>Total</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in coveragePivotRows" :key="row.key">
          <td>{{ row.key }}</td>
          <td v-for="st in shiftTypes" :key="st">{{ row.byShift[st] ?? 0 }}</td>
          <td>{{ row.total }}</td>
        </tr>
      </tbody>
    </table>

    <h3 style="margin-top:16px;">Staff Load</h3>
    <div class="form-row">
      <label class="muted">Group:</label>
      <select v-model="groupMode">
        <option value="overall">Overall</option>
        <option value="by-day">By Day</option>
        <option value="by-shift">By Shift</option>
      </select>
    </div>
    <div style="background:#0e1430; border:1px solid var(--border); border-radius:8px; padding:12px;">
      <Bar v-if="chartData" :data="chartData" :options="chartOptions" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { Chart, BarElement, CategoryScale, LinearScale, Tooltip, Legend } from 'chart.js'
import { Bar } from 'vue-chartjs'

Chart.register(BarElement, CategoryScale, LinearScale, Tooltip, Legend)

const API = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

const today = new Date().toISOString().slice(0,10)
const inSeven = new Date(Date.now() + 6*24*3600*1000).toISOString().slice(0,10)

const range = ref({ start: today, end: inSeven })
const roster = ref([])
const coverage = ref([])
const staffLoad = ref([])
const shiftTypes = ref(['morning','afternoon','night'])
const pivotMode = ref('day')
const groupMode = ref('overall')
const newAssign = ref({ date: today, shift_type: 'morning', staff_id: null })

async function load() {
  const [r1, r2, r3] = await Promise.all([
    axios.get(`${API}/roster`, { params: range.value }),
    axios.get(`${API}/stats/coverage`, { params: range.value }),
    axios.get(`${API}/stats/staff-load`, { params: range.value })
  ])
  roster.value = r1.data
  coverage.value = r2.data
  staffLoad.value = r3.data
}

async function assign() {
  const payload = { ...newAssign.value }
  await axios.post(`${API}/assignments`, payload)
  await load()
}

async function unassign(id) {
  await axios.delete(`${API}/assignments/${id}`)
  await load()
}

async function autoSchedule() {
  await axios.post(`${API}/schedule/auto`, {
    start: range.value.start,
    end: range.value.end,
    shift_types: ['morning', 'afternoon', 'night'],
    min_per_shift: 1
  })
  await load()
}

async function downloadCsv() {
  const { data } = await axios.get(`${API}/export/roster.csv`, { params: range.value })
  const blob = new Blob([data.content], { type: data.content_type })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = data.filename
  a.click()
  URL.revokeObjectURL(url)
}

onMounted(load)

// Coverage pivot rows
const coveragePivotRows = computed(() => {
  const rows = new Map()
  for (const c of coverage.value) {
    const key = pivotMode.value === 'week' ? weekKey(c.date) : c.date
    const row = rows.get(key) || { key, byShift: {}, total: 0 }
    row.byShift[c.shift_type] = (row.byShift[c.shift_type] || 0) + c.count
    row.total += c.count
    rows.set(key, row)
  }
  return Array.from(rows.values())
})

function weekKey(iso) {
  const d = new Date(iso)
  // Monday-based week number
  const target = new Date(d.valueOf())
  const dayNr = (d.getUTCDay() + 6) % 7
  target.setUTCDate(d.getUTCDate() - dayNr + 3)
  const firstThursday = new Date(Date.UTC(target.getUTCFullYear(),0,4))
  const week = 1 + Math.round(((target.getTime() - firstThursday.getTime()) / 86400000 - 3) / 7)
  return `${target.getUTCFullYear()}-W${String(week).padStart(2,'0')}`
}

// Chart data for staff load
const chartData = computed(() => {
  if (groupMode.value === 'overall') {
    return {
      labels: staffLoad.value.map(s => `${s.name} (${s.staff_id})`),
      datasets: [{
        label: 'Total Assignments',
        data: staffLoad.value.map(s => s.total_assignments),
        backgroundColor: '#4f7cff'
      }]
    }
  }
  if (groupMode.value === 'by-day') {
    const map = new Map() // label -> { name -> count }
    for (const r of roster.value) {
      const label = r.date
      const entry = map.get(label) || {}
      entry[r.staff_name] = (entry[r.staff_name] || 0) + 1
      map.set(label, entry)
    }
    return stackedFromMap(map)
  }
  if (groupMode.value === 'by-shift') {
    const map = new Map()
    for (const r of roster.value) {
      const label = r.shift_type
      const entry = map.get(label) || {}
      entry[r.staff_name] = (entry[r.staff_name] || 0) + 1
      map.set(label, entry)
    }
    return stackedFromMap(map)
  }
  return null
})

function stackedFromMap(map) {
  const labels = Array.from(map.keys())
  const names = Array.from(new Set([].concat(...Array.from(map.values()).map(obj => Object.keys(obj)))))
  return {
    labels,
    datasets: names.map((name, i) => ({
      label: name,
      data: labels.map(l => map.get(l)?.[name] || 0),
      backgroundColor: palette(i)
    }))
  }
}

function palette(i) {
  const colors = ['#4f7cff','#34d399','#f59e0b','#ef4444','#a78bfa','#10b981']
  return colors[i % colors.length]
}

const chartOptions = {
  responsive: true,
  plugins: { legend: { labels: { color: '#e6eaf2' } } },
  scales: {
    x: { ticks: { color: '#a9b0c2' }, grid: { color: 'rgba(255,255,255,0.05)' } },
    y: { ticks: { color: '#a9b0c2' }, grid: { color: 'rgba(255,255,255,0.05)' } }
  }
}
</script>


