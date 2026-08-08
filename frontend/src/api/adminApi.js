import client from './client'

export const getAllOwners = () =>
  client.get('/v1/admin/owners')

export const getAllDoctors = () =>
  client.get('/v1/admin/doctors')

export const deleteUser = (id) =>
  client.delete(`/v1/admin/users/${id}`)
