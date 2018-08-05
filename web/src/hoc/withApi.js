import React, {Component} from 'react'

export default (WrappedComponent, api) => {
  return class extends Component {
    render() {
      return (<WrappedComponent api={api} {...this.props}/>)
    }
  }
}
