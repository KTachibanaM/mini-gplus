import axios from 'axios'
import ApiError from './ApiError'
require('promise.prototype.finally').shim();
axios.defaults.validateStatus = () => {return true}

class ThenBuilder {
  constructor() {
    this.resolves = {}
    this.rejects = {}
  }

  addResolve(statusCode, responseToData) {
    this.resolves[statusCode] = responseToData
    return this
  }

  addReject(statusCode, responseToErr) {
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
          .addResolve(201, () => {return undefined})
          .addReject(409, () => {return new ApiError(409)})
          .build(resolve, reject)
      ).catch(err => {
        reject(err)
      })
    })
  }

  signIn(id, password) {

  }

  getMe() {}

  getUsers() {}
}


