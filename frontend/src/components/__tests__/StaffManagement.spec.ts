import { mount, flushPromises } from '@vue/test-utils'
import StaffManagement from '../StaffManagement.vue'
import axios from 'axios'

vi.mock('axios')
const mockedAxios = axios as unknown as { get: any, post: any, delete: any }

describe('StaffManagement', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  it('loads and displays staff, can create and delete', async () => {
    mockedAxios.get = vi.fn()
      // initial load
      .mockResolvedValueOnce({ data: [] })
      // after create reload
      .mockResolvedValueOnce({ data: [{ id: 1, name: 'Alice', age: 30, position: 'Nurse' }] })
      // after delete reload
      .mockResolvedValueOnce({ data: [] })

    mockedAxios.post = vi.fn().mockResolvedValue({ data: { id: 1, name: 'Alice', age: 30, position: 'Nurse' } })
    mockedAxios.delete = vi.fn().mockResolvedValue({ status: 204 })

    const wrapper = mount(StaffManagement)
    await flushPromises()

    // create
    await wrapper.find('input[placeholder="Name"]').setValue('Alice')
    await wrapper.find('input[placeholder="Age"]').setValue('30')
    await wrapper.find('input[placeholder="Position"]').setValue('Nurse')
    await wrapper.find('form').trigger('submit.prevent')
    expect(mockedAxios.post).toHaveBeenCalled()
    await flushPromises()
    expect(wrapper.html()).toContain('Alice')

    // delete first item
    const buttons = wrapper.findAll('button')
    const deleteBtn = buttons.find(b => b.text() === 'Delete')
    await deleteBtn?.trigger('click')
    expect(mockedAxios.delete).toHaveBeenCalledWith(expect.stringMatching(/\/staff\/1$/))
    await flushPromises()
    expect(wrapper.html()).not.toContain('Alice')
  })
})


