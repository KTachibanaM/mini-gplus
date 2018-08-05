import React, {Component} from 'react';
import {Link, Redirect} from 'react-router-dom'
import {Button, Grid, Header, Segment, Message, Label} from "semantic-ui-react";
import {Form, Input} from 'formsy-semantic-ui-react'
import CatchApiErrorBuilder from '../api/CatchApiErrorBuilder'

require('promise.prototype.finally').shim();

export default class SignIn extends Component {
  constructor(props) {
    super(props)
    this.state = {
      'error': '',
      'loading': false,
      'buttonEnabled': false,
      'redirectToHome': false
    }
  }

  handleFormValid = () => {
    this.setState({'buttonEnabled': true})
  }
  handleFormInvalid = () => {
    this.setState({'buttonEnabled': false})
  }
  showError = (err) => {
    this.setState({'error': err.toString()})
  }
  handleSubmit = (inputForm) => {
    const {'id': id, 'password': password} = inputForm

    this.setState({'loading': true})
    this.props.api.signIn(
      id, password
    ).then(() => {
      this.setState({'redirectToHome': true})
    }).catch(
      new CatchApiErrorBuilder()
        .handle(401, () => {
          this.refs.form.updateInputsWithError({
            'id': 'invalid id or password',
            'password': 'invalid id or password'
          })
        })
        .unknownError(this.showError)
        .unknownStatusCode(this.showError)
        .build()
    ).finally(() => {
      this.setState({'loading': false})
    })
  }

  render() {
    if (this.state.redirectToHome) {
      return <Redirect to='/'/>
    }

    const errorLabel = <Label color="red" pointing/>

    return (
      <div className='login-form'>
        <style>{`
          body > div,
          body > div > div,
          body > div > div > div.login-form {
            height: 100%;
          }
        `}</style>
        <Grid textAlign='center' style={{height: '100%'}} verticalAlign='middle'>
          <Grid.Column style={{maxWidth: 450}}>
            <Header as='h2' textAlign='center'>
              Sign in
            </Header>
            <Form
              ref='form'
              size='large'
              loading={this.state.loading}
              onValid={this.handleFormValid}
              onInvalid={this.handleFormInvalid}
              onValidSubmit={this.handleSubmit}
            >
              <Segment>
                <Input
                  fluid
                  name='id'
                  placeholder='ID'
                  required
                  errorLabel={errorLabel}
                />
                <Input
                  fluid
                  name='password'
                  placeholder='Password'
                  type='password'
                  required
                  errorLabel={errorLabel}
                />
                <Button
                  primary
                  fluid
                  size='large'
                  disabled={!this.state.buttonEnabled}
                >
                  Sign in
                </Button>
              </Segment>
            </Form>
            {this.state.error &&
              <Message negative>
                {this.state.error}
              </Message>
            }
            <Message>
              Don't have an account? <Link to='/signup'>Sign up here</Link>
            </Message>
          </Grid.Column>
        </Grid>
      </div>
    )
  }
}
