import client from './client'

export const bookAppointment = (data) =>
  client.post('/v1/appointments/book', data)

export const getMyAppointments = () =>
  client.get('/v1/appointments/my')
