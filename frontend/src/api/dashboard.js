import client from './client'

export const getDashboard = () =>
  client.get('/v1/dashboard')
