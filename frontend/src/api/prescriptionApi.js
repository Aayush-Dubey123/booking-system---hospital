import client from './client'

export const createPrescription = (data) =>
  client.post('/v1/prescriptions', data)

export const getMyPrescriptions = () =>
  client.get('/v1/prescriptions/my')

export const getPrescriptionByAppointment = (appointmentId) =>
  client.get(`/v1/prescriptions/appointment/${appointmentId}`)
