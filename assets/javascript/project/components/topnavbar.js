import React, { useEffect, useState } from "react";
import { connect } from "react-redux";
import { TextField } from "@material-ui/core";

const TopNavBar = (props) => {
	const [intelgroup, setIntelGroup] = useState('');

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
						<TextField
							id="outlined-select-currency-native"
							fullWidth
							select
							value={intelgroup}
							onChange={(event) => {
								setIntelGroup(event.target.value); 
								if(event.target.value != "")
									props.currentIntelgroup(event.target.value);}}
							SelectProps={{
								native: true,
							}}
							variant="outlined"
						>
							<option value="" className="has-text-light">IntelGroup Name</option>
							{props.mygroups.map((mygroup) => (
								<option key={mygroup.intelgroup.id} value={mygroup.intelgroup.id}>
									{mygroup.intelgroup.name}
								</option>
							))}
						</TextField>
						<div className="navbar-item has-dropdown is-hoverable">
							<a className="navbar-link">
								<span className="is-show-desktop">My Account</span>
							</a>
							<div className="navbar-dropdown is-right">
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

export default TopNavBar;
