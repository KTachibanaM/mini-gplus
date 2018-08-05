export default class ApiError extends Error {
  constructor(statusCode, data) {
    super()
    this.name = 'mini-gplus.ApiError'
    this.message = `${statusCode}: ${data}`
    this.statusCode = statusCode
    this.data = data
  }
}
