import React, {Component} from 'react'
import {Loader, Message, Grid, GridRow, GridColumn} from "semantic-ui-react";
import CatchApiErrorBuilder from "../api/CatchApiErrorBuilder";
import UserCard from '../components/UserCard'

export default class Users extends Component {
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
    this.props.api.getUsers()
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

    const users = this.state.data
    const fullRowCount = Math.floor(users.length / 3)
    const lastColCount = users.length % 3
    const rows = []
    for (let i = 0; i < fullRowCount; ++i) {
      rows.push(
        <GridRow key={i}>
          <GridColumn key={0}>
            <UserCard user={users[i]}/>
          </GridColumn>
          <GridColumn key={1}>
            <UserCard user={users[i + 1]}/>
          </GridColumn>
          <GridColumn key={2}>
            <UserCard user={users[i + 2]}/>
          </GridColumn>
        </GridRow>
      )
    }
    if (lastColCount !== 0) {
      const lastCols = []
      for (let i = 0; i < lastColCount; ++i) {
        lastCols.push(
          <GridColumn key={i}>
            <UserCard user={users[fullRowCount * 3 + i]}/>
          </GridColumn>
        )
      }
      rows.push(
        <GridRow key={fullRowCount}>
          {lastCols}
        </GridRow>
      )
    }

    return (
      <Grid columns={3}>
        {rows}
      </Grid>
    )
  }
}
