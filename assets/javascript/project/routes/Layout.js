import React from 'react';
import PropTypes from 'prop-types';
import { Switch, Route } from 'react-router-dom';
import { connect } from 'react-redux';

import HomePage from '../Home';
import TopNavbar from '../components/topnavbar';
import IntelGroup from '../intelgroups/index';
import User from '../users/index';

function Layout() {
  return (
    <>
      <TopNavbar></TopNavbar>
      <Router basename='/home'>
      <Switch>
        <Route exact path="/" component={HomePage} />
        <Route exact path="/intelgroups/" component={IntelGroup} />
        {/* <Route exact path="/users/" component={User} /> */}
      </Switch>
      </Router>
    </>
  );
}

export default Layout;
