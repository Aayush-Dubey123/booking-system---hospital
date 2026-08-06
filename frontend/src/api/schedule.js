import client from './client'

export const getSchedule = (date) =>
  client.get('/v1/schedule', { params: { appointment_date: date } })
