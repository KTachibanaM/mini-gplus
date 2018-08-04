import React, {Component} from 'react';
import {Button, Grid, Header, Message, Segment, Label} from 'semantic-ui-react'
import {Form, Input} from 'formsy-semantic-ui-react'
import {Link, Redirect} from "react-router-dom";
import axios from 'axios'

require('promise.prototype.finally').shim();

export default class SignUp extends Component {
  constructor(props) {
    super(props)
    this.state = {
      'error': '',
      'buttonEnabled': false,
      'loading': false,
      'redirectToSignIn': false
    }
  }

  handleFormValid = () => {
    this.setState({'buttonEnabled': true})
  }
  handleFormInvalid = () => {
    this.setState({'buttonEnabled': false})
  }
  showError = (message) => {
    this.setState({'error': message})
  }
  handleSubmit = (inputForm) => {
    const {'id': id, 'password': password, 'confirmPassword': confirmPassword} = inputForm
    if (password !== confirmPassword) {
      this.refs.form.updateInputsWithError({
        'password': 'Password does not match',
        'confirmPassword': 'Password does not match'
      })
      return
    }
    this.setState({'loading': true})
    axios.post(
      'http://localhost:5000/api/users',
      {
        'id': id,
        'password': password
      }
    ).then(res => {
      if (res.status === 201) {
        this.setState({'redirectToSignIn': true})
        return
      }
      this.showError(`Unknown response ${res}`)
    }).catch(err => {
      if (!err.response) {
        this.showError(`Unknown error ${err}`)
        return
      }
      const res = err.response
      if (res.status === 409) {
        this.refs.form.updateInputsWithError({
          'id': 'id is already taken'
        })
        return
      }
      this.showError(`Unknown response ${res}`)
    }).finally(() => {
      this.setState({'loading': false})
    })
  }

  render() {
    if (this.state.redirectToSignIn) {
      return <Redirect to={'/signin'}/>
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
        `}
        </style>
        <Grid textAlign='center' style={{height: '100%'}} verticalAlign='middle'>
          <Grid.Column style={{maxWidth: 450}}>
            <Header as='h2' textAlign='center'>
              Sign up
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
                <Input
                  fluid
                  name='confirmPassword'
                  placeholder='Confirm password'
                  type='password'
                  required
                  errorLabel={errorLabel}
                />
                <Button
                  fluid
                  primary
                  size='large'
                  disabled={!this.state.buttonEnabled}
                >
                  Sign up
                </Button>
              </Segment>
            </Form>
            {this.state.error && <Message negative>
              {this.state.error}
            </Message>}
            <Message>
              Already have an account? <Link to='/signin'>Sign in here</Link>
            </Message>
          </Grid.Column>
        </Grid>
      </div>
    )
  }
}