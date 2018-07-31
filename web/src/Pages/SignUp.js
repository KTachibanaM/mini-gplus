import React  from 'react';
import {Button, Form, Grid, Header, Message, Segment} from 'semantic-ui-react'
import {Link} from "react-router-dom";

const SignUp = () => (
  <div className='login-form'>
    {/*
      Heads up! The styles below are necessary for the correct render of this example.
      You can do same with CSS, the main idea is that all the elements up to the `Grid`
      below must have a height of 100%.
    */}
    <style>{`
      body > div,
      body > div > div,
      body > div > div > div.login-form {
        height: 100%;
      }
    `}</style>
    <Grid textAlign='center' style={{ height: '100%' }} verticalAlign='middle'>
      <Grid.Column style={{ maxWidth: 450 }}>
        <Header as='h2' textAlign='center'>
          Sign up
        </Header>
        <Form size='large'>
          <Segment>
            <Form.Input fluid placeholder='ID' />
            <Form.Input fluid placeholder='Password' type='password'/>
            <Form.Input fluid placeholder='Confirm password' type='password'/>
            <Button fluid size='large'>
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

export default SignUp
