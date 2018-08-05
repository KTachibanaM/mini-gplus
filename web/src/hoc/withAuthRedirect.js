import React, {Component} from 'react'
import {isAuthenticated, getAuthentication} from "../auth/cookie";
import {Redirect} from "react-router-dom";

export default (WrappedComponent) => {
  return class extends Component {
    render() {
      if (isAuthenticated()) {
        const authentication = getAuthentication()
        return (<WrappedComponent authentication={authentication} {...this.props}/>)
      } else {
        return (<Redirect to='/signin'/>)
      }
    }
  }
}
