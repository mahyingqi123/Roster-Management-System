def test_staff_crud(client):
  # list empty
  res = client.get('/staff')
  assert res.status_code == 200
  assert res.json() == []

  # create
  res = client.post('/staff', json={ 'name': 'Alice', 'age': 30, 'position': 'Nurse' })
  assert res.status_code == 201
  alice = res.json()
  assert alice['name'] == 'Alice'

  # list now 1
  res = client.get('/staff')
  assert len(res.json()) == 1

  # delete
  res = client.delete(f"/staff/{alice['id']}")
  assert res.status_code == 204

  # list empty again
  res = client.get('/staff')
  assert res.json() == []


