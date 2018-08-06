import axios from 'axios'
import ApiError from './ApiError'
import {cookieExists, getCookie, setCookie} from "./authCookie";
require('promise.prototype.finally').shim();
axios.defaults.validateStatus = () => {return true}

class ThenBuilder {
  constructor() {
    this.resolves = {}
    this.rejects = {}
  }

  addResolve(statusCode, responseToData) {
    if (responseToData === undefined) {
      responseToData = () => {return undefined}
    }
    this.resolves[statusCode] = responseToData
    return this
  }

  addReject(statusCode, responseToErr) {
    if (responseToErr === undefined) {
      responseToErr = () => {return undefined}
    }
    this.rejects[statusCode] = responseToErr
    return this
  }

  build(resolve, reject) {
    return res => {
      const statusCode = res.status
      if (this.resolves[statusCode]) {
        resolve(this.resolves[statusCode](res))
      } else if (this.rejects[statusCode]) {
        reject(this.rejects[statusCode](res))
      } else {
        reject(new Error(`Unknown status code ${statusCode}`))
      }
    }
  }
}

export default class Api {
  constructor(endpoint) {
    this.endpoint = endpoint
  }

  signUp(id, password) {
    return new Promise((resolve, reject) => {
      axios.post(
        `${this.endpoint}/users`,
        {
          'id': id,
          'password': password
        }
      ).then(
        new ThenBuilder()
          .addResolve(201)
          .addReject(409, () => {return new ApiError(409)})
          .build(resolve, reject)
      ).catch(err => {
        reject(err)
      })
    })
  }

  signIn(id, password) {
    return new Promise((resolve, reject) => {
      axios.post(
        `${this.endpoint}/auth`,
        {
          'id': id,
          'password': password
        }
      ).then(
        new ThenBuilder()
          .addResolve(200, res => {
            const {'access_token': accessToken} = res.data
            setCookie(accessToken)
          })
          .addReject(401, () => {return new ApiError(401)})
          .build(resolve, reject)
      ).catch(err => {
        reject(err)
      })
    })
  }

  static rejectOnUnauthorized(rejectFunc) {
    if (!cookieExists()) {
      rejectFunc(new ApiError(401))
      return true
    } else {
      return false
    }
  }

  static authorizedHeaders() {
    return {
      'Authorization': `Bearer ${getCookie()}`
    }
  }

  getMe() {
    return new Promise((resolve, reject) => {
      if (Api.rejectOnUnauthorized(reject)) {
        return
      }
      axios.get(
        `${this.endpoint}/me`,
        {
          headers: Api.authorizedHeaders()
        }
      ).then(
        new ThenBuilder()
          .addResolve(200, res => {
            return res.data
          })
          .addReject(401, () => {return new ApiError(401)})
          .build(resolve, reject)
      ).catch(err => {
        reject(err)
      })
    })
  }

  getUsers() {
    return new Promise((resolve, reject) => {
      if (Api.rejectOnUnauthorized(reject)) {
        return
      }
      axios.get(
        `${this.endpoint}/users`,
        {
          headers: Api.authorizedHeaders()
        }
      ).then(
        new ThenBuilder()
          .addResolve(200, res => {
            return res.data
          })
          .addReject(401, () => {return new ApiError(401)})
          .build(resolve, reject)
      ).catch(err => {
        reject(err)
      })
    })
  }
}


