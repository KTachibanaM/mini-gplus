import React, { Component } from 'react';
import {
  BrowserRouter as Router,
  Route,
  Switch,
  Redirect
} from 'react-router-dom'
import AuthenticatedRoute from './auth/AuthRoute'
import SignIn from './pages/SignIn'
import SignUp from './pages/SignUp'
import Home from './pages/Home'

export default class App extends Component {
  render() {
    return (
      <Router>
        <Switch>
          <AuthenticatedRoute
            exact={true}
            path='/'
            component={Home}
          />
          <Route path="/signup" component={SignUp}/>
          <Route path="/signin" component={SignIn}/>
          <Redirect to='/' />
        </Switch>
      </Router>
    );
  }
}
