import React from 'react';
import { Link } from 'react-router-dom'
import {Button, Form, Grid, Header, Segment, Message} from "semantic-ui-react";

export default () => (
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
          Sign in
        </Header>
        <Form size='large'>
          <Segment>
            <Form.Input fluid placeholder='ID' />
            <Form.Input fluid placeholder='Password' type='password'/>
            <Button primary fluid size='large'>
              Sign in
            </Button>
          </Segment>
        </Form>
        <Message>
          Don't have an account? <Link to='/signup'>Sign up here</Link>
        </Message>
      </Grid.Column>
    </Grid>
  </div>
)
