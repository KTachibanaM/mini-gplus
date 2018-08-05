import React, {Component} from 'react'

export default (WrappedComponent, api) => {
  return class extends Component {
    constructor(props) {
      super(props)
    }

    render() {
      return (<WrappedComponent api={api} {...this.props}/>)
    }
  }
}
