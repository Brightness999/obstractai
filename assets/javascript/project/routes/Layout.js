import React from 'react';
import PropTypes from 'prop-types';
import { Switch, Route } from 'react-router-dom';
import { connect } from 'react-redux';

import HomePage from '../Home';
import TopNavbar from '../components/topnavbar';
import IntelGroup from '../intelgroups/index';
// import Login from '../containers/Login';
// import PrivateRoute from '../components/PrivateRoute';

// const propTypes = {
//   logged: PropTypes.bool.isRequired
// };

function Layout() {
  return (
    <>
      <TopNavbar></TopNavbar>
      <Switch>
        <Route exact path="/" component={HomePage} />
        <Route exact path="/intelgroups" component={IntelGroup} />
        {/* <PrivateRoute isAuthenticated={logged} component={CustomHome} /> */}
      </Switch>
    </>
  );
}

// Layout.propTypes = propTypes;

// const mapStateToProps = state => ({
//   logged: state.logged
// });

export default Layout;
