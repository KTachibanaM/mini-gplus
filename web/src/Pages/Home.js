import React, {Component} from 'react';
import axios from 'axios'
require('promise.prototype.finally').shim();

export default class Home extends Component {
  constructor(props) {
    super(props)
    this.state = {
      'id': 'nil'
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

  render() {
    return (
      <div>
        {this.state.id}
      </div>
    )
  }
}
