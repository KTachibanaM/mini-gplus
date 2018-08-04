import React, {Component} from 'react'
import {Redirect} from 'react-router-dom'
import {
  Container,
  Image,
  Menu,
  Icon
} from 'semantic-ui-react'
import Logo from '../logo.png'

export default (WrappedComponent, path) => {
  return class extends Component {
    constructor(props) {
      super(props)
      this.state = {
        'redirectTo': undefined
      }
    }

    handleNavItemClick = (path) => {
      this.setState({'redirectTo': path})
    }

    render() {
      if (this.state.redirectTo !== undefined && this.state.redirectTo !== path) {
        return <Redirect to={this.state.redirectTo}/>
      }

      return (
        <div>
          <Menu fixed='top'>
            <Menu.Item
              as='a'
              onClick={() => {this.handleNavItemClick('/')}}
              active={path === '/'}
            >
              <Image size='mini' src={Logo} style={{ marginRight: '3em' }} />
              Home
            </Menu.Item>
            <Menu.Item
              as='a'
              onClick={() => {this.handleNavItemClick('/circles')}}
              active={path === '/circles'}
            >
              Circles
            </Menu.Item>
            <Menu.Item
              as='a'
              onClick={() => {this.handleNavItemClick('/users')}}
              active={path === '/users'}
            >
              Users
            </Menu.Item>
            <Menu.Item
              as='a'
              onClick={() => {this.handleNavItemClick('/profile')}}
              active={path === '/profile'}
            >
              Profile
            </Menu.Item>
            <Menu.Menu position='right'>
              <Menu.Item as='a'>
                <Icon name='bell outline'/>
              </Menu.Item>
              <Menu.Item as='a'>Sign out</Menu.Item>
            </Menu.Menu>
          </Menu>
          <Container style={{ marginTop: '5em' }}>
            <WrappedComponent {...this.props}/>
          </Container>
        </div>
      )
    }
  }
}
