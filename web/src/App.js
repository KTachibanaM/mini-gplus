import React, { Component } from 'react';
import {
  BrowserRouter as Router,
  Route,
  Switch,
  Redirect
} from 'react-router-dom'
import AuthenticatedRoute from './Authentication/AuthenticatedRoute'
import withAuthentication from './Authentication/withAuthentication'
import SignIn from './Pages/SignIn'
import SignUp from './Pages/SignUp'
import Home from './Pages/Home'

export default class App extends Component {
  render() {
    return (
      <Router>
        <Switch>
          <AuthenticatedRoute
            exact={true}
            path='/'
            component={withAuthentication(Home)}
          />
          <Route path="/signup" component={SignUp}/>
          <Route path="/signin" component={SignIn}/>
          <Redirect to='/' />
        </Switch>
      </Router>
    );
  }
}
