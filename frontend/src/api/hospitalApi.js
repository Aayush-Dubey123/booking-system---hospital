import client from './client'

export const getHospitals = () =>
  client.get('/v1/hospitals')

export const getHospital = (id) =>
  client.get(`/v1/hospitals/${id}`)

export const createHospital = (data) =>
  client.post('/v1/hospitals', data)

export const getHospitalDoctors = (id) =>
  client.get(`/v1/hospitals/${id}/doctors`)

export const addDoctorToHospital = (id, data) =>
  client.post(`/v1/hospitals/${id}/doctors`, data)

export const getHospitalAppointments = (id) =>
  client.get(`/v1/hospitals/${id}/appointments`)
