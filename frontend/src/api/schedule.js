import client from './client'

export const getSchedule = (date, hospitalId) =>
  client.get('/v1/schedule', { 
    params: { 
      appointment_date: date,
      ...(hospitalId && { hospital_id: hospitalId })
    } 
  })
