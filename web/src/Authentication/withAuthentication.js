import React, {Component} from 'react';
import {getAuthentication} from "./Authenticator";

export default (WrappedComponent) => {
  const authentication = getAuthentication()
  return class extends Component {
    constructor(props) {
      super(props)
    }

    render() {
      return <WrappedComponent
        authentication={authentication}
        {...this.props}
      />
    }
  }
}
