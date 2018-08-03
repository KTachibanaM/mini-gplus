import Cookies from 'universal-cookie';

const CookieKey = 'access_token'
const CookiePath = '/'

export const isAuthenticated = () => {
  const cookies = new Cookies();
  return cookies.get(CookieKey) !== undefined
}

export const getAuthentication = () => {
  const cookies = new Cookies();
  return cookies.get(CookieKey)
}

export const authenticate = (accessToken) => {
  const cookies = new Cookies();
  cookies.set(CookieKey, accessToken, { path: CookiePath })
}

export const unauthenticate = () => {
  const cookies = new Cookies();
  cookies.set(CookieKey, undefined, { path: CookiePath })
}
