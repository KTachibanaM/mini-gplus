export default class CatchApiErrorBuilder {
  constructor() {
    this.handlers = {}
    this.unknownErrorHandler = undefined
    this.unknownStatusCodeHandler = undefined
  }

  handle(statusCode, handleData) {
    this.handlers[statusCode] = handleData
    return this
  }

  unknownError(handler) {
    this.unknownErrorHandler = handler
    return this
  }

  unknownStatusCode(handler) {
    this.unknownStatusCodeHandler = handler
    return this
  }

  build() {
    return err => {
      if (err.name !== 'mini-gplus.ApiError') {
        if (this.unknownErrorHandler) {
          this.unknownErrorHandler(err)
        } else {
          throw err
        }
      } else {
        if (this.handlers[err.statusCode]) {
          this.handlers[err.statusCode](err)
        } else {
          if (this.unknownStatusCodeHandler) {
            this.unknownStatusCodeHandler(err)
          } else {
            throw err
          }
        }
      }
    }
  }
}
