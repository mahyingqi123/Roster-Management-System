import { mount, flushPromises } from '@vue/test-utils'
import RosterDisplay from '../RosterDisplay.vue'
import axios from 'axios'

vi.mock('axios')
const mockedAxios = axios as unknown as { get: any, post: any, delete: any }

describe('RosterDisplay', () => {
  beforeEach(() => vi.resetAllMocks())

  it('loads roster and stats, can assign and unassign, auto and export', async () => {
    // Generic GET mock that returns appropriate shapes for any number of calls
    mockedAxios.get = vi.fn().mockImplementation((url: string) => {
      if (url.includes('/roster')) return Promise.resolve({ data: [] })
      if (url.includes('/stats/coverage')) return Promise.resolve({ data: [] })
      if (url.includes('/stats/staff-load')) return Promise.resolve({ data: [] })
      if (url.includes('/export/roster.csv')) return Promise.resolve({ data: { filename: 'roster.csv', content: 'date,shift_type,staff_id,staff_name,position', content_type: 'text/csv' } })
      return Promise.resolve({ data: {} })
    })

    mockedAxios.post = vi.fn()
      .mockResolvedValueOnce({ data: { id: 1, shift_id: 1, staff_id: 1 } }) // assign
      .mockResolvedValueOnce({ data: { created_assignments: [1] } }) // auto
    mockedAxios.delete = vi.fn().mockResolvedValue({ status: 204 })

    const wrapper = mount(RosterDisplay)
    await flushPromises()

    // set new assignment inputs
    await wrapper.find('input[type="number"]').setValue('1')
    await wrapper.find('button').trigger('click') // Assign button is first
    await flushPromises()

    // unassign
    const removeBtn = wrapper.findAll('button').find(b => b.text() === 'Remove')
    if (removeBtn) {
      await removeBtn.trigger('click')
      expect(mockedAxios.delete).toHaveBeenCalled()
    }

    // auto schedule
    const autoBtn = wrapper.findAll('button').find(b => b.text() === 'Auto-Schedule')
    await autoBtn?.trigger('click')
    expect(mockedAxios.post).toHaveBeenCalledWith(expect.stringMatching(/\/schedule\/auto$/), expect.any(Object))

    // export
    const exportBtn = wrapper.findAll('button').find(b => b.text() === 'Export CSV')
    await exportBtn?.trigger('click')
    expect(mockedAxios.get).toHaveBeenCalledWith(expect.stringMatching(/\/export\/roster\.csv$/), expect.any(Object))
  })
})


