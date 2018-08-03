import React, {Component} from 'react'
import {Route, Redirect} from 'react-router-dom'
import {isAuthenticated} from "./Authenticator";

export default ({ component: Component, ...rest }) => (
  <Route {...rest} render={(props) => (
    isAuthenticated() ? <Component {...props} /> : <Redirect to='/signin' />
  )} />
)
