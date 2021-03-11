import React, { useEffect, useState } from "react";
import { useHistory } from "react-router-dom";
import { TextField } from "@material-ui/core";

const TopNavBar = (props) => {
	const [intelgroup, setIntelGroup] = useState(localStorage.getItem('currentgroup') || '');
	const history = useHistory();
	useEffect(()=>{
		const $navbarBurgers = Array.prototype.slice.call(document.querySelectorAll('.navbar-burger'), 0);
		if ($navbarBurgers.length > 0) {
            $navbarBurgers.forEach(el => {
                el.addEventListener('click', () => {
                    const target = el.dataset.target;
                    const $target = document.getElementById(target);
                    el.classList.toggle('is-active');
                    $target.classList.toggle('is-active');
                });
            });
        }
	},[intelgroup]);

	
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
					{/* <div className="navbar-start">
						<TextField id="outlined-basic" placeholder="Search for intelligence" variant="outlined" />
					</div> */}
					<div className="navbar-end">
						{props.mygroups.length>0&&
						<TextField
							id="outlined-select-currency-native"
							fullWidth
							select
							value={intelgroup}
							onChange={(event) => {
								if(event.target.value == 'add'){
									history.push('/newgroup');
								}
								else{
									localStorage.setItem('currentgroup', event.target.value);
									setIntelGroup(event.target.value);
									if(event.target.value != "")
										props.currentIntelgroup(event.target.value);}}
								}
							SelectProps={{
								native: true,
							}}
							variant="outlined"
						>
							<option value="" className="has-text-white">Select Group</option>
							{props.mygroups.map((mygroup) => (
								<option key={mygroup.intelgroup.id} value={mygroup.intelgroup.id}>
									{mygroup.intelgroup.name}
								</option>
							))}
							<option value="add" className="has-text-primary">Create New Group</option>
						</TextField>}
						{props.mygroups.length>0?
						<div className="navbar-item has-dropdown is-hoverable">
							<a className="navbar-link">
								<span className="is-show-desktop">My Account</span>
							</a>
							<div className="navbar-dropdown is-right">
								<a className="navbar-item" href="/app/account" >
								<span>Profile</span>
								</a>
								<a className="navbar-item" href="/accounts/password/change">
								<span>Change Password</span>
								</a>
								<a className="navbar-item" href="#" onClick={()=>{
									localStorage.removeItem('currentgroup');
									window.location.href = "/accounts/logout";
								}}>
								<span>Sign out</span>
								</a>
							</div>
						</div>:
						<a className="navbar-item" href="#" >
						<span>Sign out</span>
						</a>}
					</div>
				</div>
			</div>
		</nav>
	);
}

export default TopNavBar;
