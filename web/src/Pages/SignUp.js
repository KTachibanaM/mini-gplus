import React, {Component} from 'react';
import {Button, Grid, Header, Message, Segment} from 'semantic-ui-react'
import {Form, Input} from 'formsy-semantic-ui-react'
import {Link} from "react-router-dom";

class SignUp extends Component {
  constructor(props) {
    super(props)
    this.state = {
      'buttonEnabled': false,
      'loading': false
    }
  }
  handleFormValid = () => {
    this.setState({'buttonEnabled': true})
  }
  handleFormInvalid = () => {
    this.setState({'buttonEnabled': false})
  }
  handleSubmit = (inputForm) => {
    const { id, password, confirmPassword } = inputForm
    if (password !== confirmPassword) {
      this.refs.form.updateInputsWithError({
        'password': 'Password does not match',
        'confirmPassword': 'Password does not match'
      })
      return
    }
    this.setState({'loading': true})
  }
  render() {
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
                />
                <Input
                  fluid
                  name='password'
                  placeholder='Password'
                  type='password'
                  required
                />
                <Input
                  fluid
                  name='confirmPassword'
                  placeholder='Confirm password'
                  type='password'
                  required
                />
                <Button fluid primary size='large' disabled={!this.state.buttonEnabled}>
                  Sign up
                </Button>
              </Segment>
            </Form>
            <Message>
              Already have an account? <Link to='/signin'>Sign in here</Link>
            </Message>
          </Grid.Column>
        </Grid>
      </div>
    )
  }
}

export default SignUp
