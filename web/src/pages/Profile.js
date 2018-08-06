import React, {Component} from 'react'
import CatchApiErrorBuilder from '../api/CatchApiErrorBuilder'
import {Header, HeaderContent, Message, Loader} from 'semantic-ui-react'

require('promise.prototype.finally').shim();


export default class Profile extends Component {
  constructor(props) {
    super(props)
    this.state = {
      'loading': true,
      'error': undefined,
      'data': undefined
    }
  }

  showError = (err) => {
    this.setState({'error': err.toString()})
  }

  componentDidMount() {
    this.props.api.getMe()
      .then(data => {
        this.setState({'data': data})
      })
      .catch(
        new CatchApiErrorBuilder()
          .unknownError(this.showError)
          .unknownStatusCode(this.showError)
          .build()
      ).finally(() => {
        this.setState({'loading': false})
    })
  }

  render() {
    if (this.state.loading) {
      return (
        <Loader size='massive'/>
      )
    }
    if (this.state.error) {
      return (
        <Message negative>{this.state.error}</Message>
      )
    }

    return (
      <div>
        <Header as='h1' icon textAlign='center'>
          <HeaderContent>{this.state.data['id']}</HeaderContent>
        </Header>
      </div>
    )
  }
}
