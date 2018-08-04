import React, {Component} from 'react'
import {Route, Redirect} from 'react-router-dom'
import {isAuthenticated, getAuthentication} from "./cookie";

export default ({ component: Component, ...rest }) => (
  <Route {...rest} render={(props) => (
    isAuthenticated() ? <Component authentication={getAuthentication()} {...props} /> : <Redirect to='/signin' />
  )} />
)
