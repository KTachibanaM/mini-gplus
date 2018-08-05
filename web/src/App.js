import React, { Component } from 'react';
import {
  BrowserRouter as Router,
  Route,
  Switch,
  Redirect
} from 'react-router-dom'
import Api from './api/Api'
import AuthenticatedRoute from './auth/AuthRoute'
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
          <AuthenticatedRoute
            exact={true}
            path='/'
            component={withNavBar(Home, '/')}
          />
          <Route path="/signup" component={withApi(SignUp, api)}/>
          <Route path="/signin" component={SignIn}/>
          <AuthenticatedRoute path="/circles" component={withNavBar(Circles, '/circles')}/>
          <AuthenticatedRoute path="/users" component={withNavBar(Users, '/users')}/>
          <AuthenticatedRoute path="/profile" component={withNavBar(Profile, '/profile')}/>
          <Redirect to='/' />
        </Switch>
      </Router>
    );
  }
}
