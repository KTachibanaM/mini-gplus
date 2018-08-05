import React, {Component} from 'react'
import {cookieExists, getCookie} from "../api/authCookie";
import {Redirect} from "react-router-dom";

export default (WrappedComponent) => {
  return class extends Component {
    render() {
      if (cookieExists()) {
        const authentication = getCookie()
        return (<WrappedComponent authentication={authentication} {...this.props}/>)
      } else {
        return (<Redirect to='/signin'/>)
      }
    }
  }
}
