import React, {Component} from 'react';
import axios from 'axios'
import {Redirect} from 'react-router-dom'
import {unAuthenticate} from "../auth/AuthCookie";
require('promise.prototype.finally').shim();

export default class Home extends Component {
  constructor(props) {
    super(props)
    this.state = {
      'id': 'nil',
      'redirectToSignIn': false
    }
  }

  componentDidMount() {
    axios.get(
      'http://localhost:5000/api/user',
      {
        headers: {
          'Authorization': `Bearer ${this.props.authentication}`
        }
      }
    ).then(res => {
      if (res.status === 200) {
        this.setState({'id': res.data.id})
        return
      }
      console.error(res)
    }).catch(err => {
      if (!err.response) {
        console.error(err)
        return
      }
      const res = err.response
      if (res.status === 401) {
        console.error('unauthenticated')
        return
      }
      console.error(res)
    }).finally(() => {
    })
  }

  handleSignOut = () => {
    unAuthenticate()
    this.setState({'redirectToSignIn': true})
  }

  render() {
    if (this.state.redirectToSignIn) {
      return <Redirect to='/signin'/>
    }

    return (
      <div>
        <div>{this.state.id}</div>
        <button onClick={this.handleSignOut}>SignOut</button>
      </div>
    )
  }
}
