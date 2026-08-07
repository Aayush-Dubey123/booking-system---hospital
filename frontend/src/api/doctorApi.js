import client from './client'

export const getDoctorDashboard = () =>
  client.get('/v1/doctor/dashboard')

export const getDoctorSchedule = (date) =>
  client.get('/v1/doctor/schedule', { params: { appointment_date: date } })
