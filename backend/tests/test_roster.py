from datetime import date, timedelta


def seed_staff(client, n=3):
  ids = []
  for i in range(n):
    r = client.post('/staff', json={ 'name': f'Staff{i+1}', 'age': 25+i, 'position': 'Ops' })
    ids.append(r.json()['id'])
  return ids


def test_assignments_and_roster(client):
  staff_ids = seed_staff(client, 2)
  d = date.today().isoformat()

  # create assignments
  r = client.post('/assignments', json={ 'date': d, 'shift_type': 'morning', 'staff_id': staff_ids[0] })
  assert r.status_code == 201
  a1 = r.json()['id']

  r = client.get('/roster', params={ 'start': d, 'end': d })
  roster = r.json()
  assert len(roster) == 1
  assert roster[0]['staff_id'] == staff_ids[0]

  # delete assignment
  r = client.delete(f"/assignments/{a1}")
  assert r.status_code == 204

  r = client.get('/roster', params={ 'start': d, 'end': d })
  assert r.json() == []


def test_stats_export_auto_schedule(client):
  staff_ids = seed_staff(client, 3)
  start = date.today()
  end = start + timedelta(days=2)

  # auto schedule
  r = client.post('/schedule/auto', json={
    'start': start.isoformat(),
    'end': end.isoformat(),
    'shift_types': ['morning','afternoon'],
    'min_per_shift': 1
  })
  assert r.status_code == 200
  created = r.json()['created_assignments']
  assert len(created) >= 1

  # stats
  params = { 'start': start.isoformat(), 'end': end.isoformat() }
  r = client.get('/stats/coverage', params=params)
  assert r.status_code == 200
  assert isinstance(r.json(), list)

  r = client.get('/stats/staff-load', params=params)
  assert r.status_code == 200
  assert isinstance(r.json(), list)

  # export
  r = client.get('/export/roster.csv', params=params)
  assert r.status_code == 200
  body = r.json()
  assert 'content' in body and body['content'].startswith('date,shift_type,staff_id,staff_name,position')


