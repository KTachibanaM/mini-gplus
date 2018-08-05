import Cookies from 'universal-cookie';

const CookieKey = 'access_token'
const CookiePath = '/'

export const cookieExists = () => {
  const cookies = new Cookies();
  return cookies.get(CookieKey) !== undefined
}

export const getCookie = () => {
  const cookies = new Cookies();
  return cookies.get(CookieKey)
}

export const setCookie = (accessToken) => {
  const cookies = new Cookies();
  cookies.set(CookieKey, accessToken, { path: CookiePath })
}

export const removeCookie = () => {
  const cookies = new Cookies();
  cookies.remove(CookieKey, { path: CookiePath })
}
