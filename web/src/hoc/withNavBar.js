import React, {Component} from 'react'
import {Redirect} from 'react-router-dom'
import {
  Container,
  Image,
  Menu,
  Icon,
  MenuItem
} from 'semantic-ui-react'
import Logo from '../logo.png'
import {unAuthenticate} from "../auth/cookie";

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

    handleSignOut = () => {
      unAuthenticate()
      this.setState({'redirectTo': '/signin'})
    }

    render() {
      if (this.state.redirectTo !== undefined && this.state.redirectTo !== path) {
        return <Redirect to={this.state.redirectTo}/>
      }

      return (
        <div>
          <Menu fixed='top'>
            <MenuItem
              as='a'
              onClick={() => {this.handleNavItemClick('/')}}
              active={path === '/'}
            >
              <Image size='mini' src={Logo} style={{ marginRight: '3em' }} />
              Home
            </MenuItem>
            <MenuItem
              as='a'
              onClick={() => {this.handleNavItemClick('/circles')}}
              active={path === '/circles'}
            >
              Circles
            </MenuItem>
            <MenuItem
              as='a'
              onClick={() => {this.handleNavItemClick('/users')}}
              active={path === '/users'}
            >
              Users
            </MenuItem>
            <MenuItem
              as='a'
              onClick={() => {this.handleNavItemClick('/profile')}}
              active={path === '/profile'}
            >
              Profile
            </MenuItem>
            <Menu.Menu position='right'>
              <MenuItem as='a' size='large'>
                <Icon name='bell outline'/>
              </MenuItem>
              <MenuItem
                as='a'
                onClick={() => {this.handleSignOut()}}
              >
                Sign out
              </MenuItem>
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
