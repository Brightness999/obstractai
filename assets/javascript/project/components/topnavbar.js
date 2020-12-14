import React from "react";
import {connect} from "react-redux";
import {Link} from "react-router-dom";

function TopNavBar(props) {
	return (
	<nav className="navbar" role="navigation" aria-label="main navigation">
		<div className="container">
		<div className="navbar-brand">
			<a className="navbar-item" href="#">
				{/* {{project_meta.NAME}} */}
			</a>
			<img src="static/images/favicons/logo.png" alt=""/>
			<a role="button" className="navbar-burger burger" aria-label="menu" aria-expanded="false" data-target="nav-menu">
			<span aria-hidden="true"></span>
			<span aria-hidden="true"></span>
			<span aria-hidden="true"></span>
			</a>
		</div>
		<div className="navbar-menu" id="nav-menu">
			<div className="navbar-start">
				<Link to="/intelgroups" className="navbar-item">Intel Groups</Link>
				<Link to="/users" className="navbar-item">Users</Link>
				<Link to="/feeds" className="navbar-item">Feeds</Link>
				<Link to="/plans" className="navbar-item">Plans</Link>

			</div>
			<div className="navbar-end">
				
				<div className="navbar-item has-dropdown is-hoverable">
				<a className="navbar-link">
					<span className="is-hidden-desktop">My Account</span>
				</a>
				<div className="navbar-dropdown is-right">
					<a className="navbar-item" href="{% url 'users:user_profile' %}" >
					<span className="icon"><i className="fa fa-user"></i></span><span>Profile</span>
					</a>
					<a className="navbar-item" href="{% url 'account_change_password' %}">
					<span className="icon"><i className="fa fa-unlock-alt"></i></span><span>Change Password</span>
					</a>
					<a className="navbar-item" href="{% url 'account_logout' %}" >
					<span className="icon"><i className="fa fa-sign-out"></i></span><span>Sign out</span>
					</a>
				</div>
				</div>
			</div>
		</div>
		</div>
	</nav>
  );
}

const mapStateToProps = function (state) {
  return {
  };
};
export default connect(mapStateToProps,null)(TopNavBar);
