import React, { useEffect, useState } from "react";
import { connect } from "react-redux";
import { TextField } from "@material-ui/core";
import { Dropdown } from "semantic-ui-react";

const TopNavBar = (props) => {
	const [intelgroup, setIntelgroup] = useState('');
	const intelgroupOptions = props.mygroups.map((group, index) => ({
		key: index, value: group.intelgroup.id, text: group.intelgroup.name
	}));

	useEffect(()=>{
		props.mygroups.map((group, index) => ({
			key: index, value: group.intelgroup.id, text: group.intelgroup.name
		}));
	},[props.mygroups]);


	return (
		<nav className="navbar" role="navigation" aria-label="main navigation">
			<div className="container">
				<div className="navbar-brand">
					<a className="navbar-item" href="#">
					</a>
					<img src="/static/images/favicons/logo.png" alt=""/>
					<a role="button" className="navbar-burger burger" aria-label="menu" aria-expanded="false" data-target="nav-menu">
					<span aria-hidden="true"></span>
					<span aria-hidden="true"></span>
					<span aria-hidden="true"></span>
					</a>
				</div>
				<div className="navbar-menu" id="nav-menu">
					<div className="navbar-start">
						<TextField id="outlined-basic" placeholder="Search for intelligence" variant="outlined" />
					</div>
					<div className="navbar-end">
						<Dropdown
							placeholder='IntelGroup Name'
							search
							selection
							options={intelgroupOptions}
							onChange={(e, {value}) => {
								setIntelgroup(value);
								props.currentIntelgroup(value);
							}}
						/>
						<div className="navbar-item has-dropdown is-hoverable">
							<a className="navbar-link">
								<span className="is-show-desktop">My Account</span>
							</a>
							<div className="navbar-dropdown is-right">
								{/* <a className="navbar-item" href="/users/profile" >
								<span className="icon"><i className="fa fa-user"></i></span><span>Profile</span>
								</a> */}
								<a className="navbar-item" href="/home/account" >
								<span className="icon"><i className="fa fa-user"></i></span><span>Profile</span>
								</a>
								<a className="navbar-item" href="/accounts/password/change">
								<span className="icon"><i className="fa fa-unlock-alt"></i></span><span>Change Password</span>
								</a>
								<a className="navbar-item" href="/accounts/logout" >
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

// const mapStateToProps = function (state) {
//   return {
//   };
// };
export default TopNavBar;
