import client from './client'

export const signup = (data) =>
  client.post('/v1/users/signup', data)

export const login = (data) =>
  client.post('/v1/users/login', data)
