import React, { Component } from 'react';
import {
  BrowserRouter as Router,
  Route,
  Switch,
  Redirect
} from 'react-router-dom'
import Api from './api/Api'
import withAuthRedirect from './hoc/withAuthRedirect'
import withNavBar from './hoc/withNavBar'
import withApi from './hoc/withApi'
import SignIn from './pages/SignIn'
import SignUp from './pages/SignUp'
import Home from './pages/Home'
import Circles from './pages/Circles'
import Users from './pages/Users'
import Profile from './pages/Profile'

const api = new Api(
  "http://localhost:5000/api"
)

export default class App extends Component {
  render() {
    return (
      <Router>
        <Switch>
          <Route
            exact={true}
            path='/'
            component={withAuthRedirect(withNavBar(Home, '/'))}
          />
          <Route
            path="/profile"
            component={withApi(withAuthRedirect(withNavBar(Profile, '/profile')), api)}
          />
          <Route
            path="/users"
            component={withApi(withAuthRedirect(withNavBar(Users, '/users')), api)}
          />
          <Route
            path="/signup"
            component={withApi(SignUp, api)}
          />
          <Route
            path="/signin"
            component={withApi(SignIn, api)}
          />
          <Route path="/circles" component={withAuthRedirect(withNavBar(Circles, '/circles'))}/>
          <Redirect to='/'/>
        </Switch>
      </Router>
    );
  }
}
