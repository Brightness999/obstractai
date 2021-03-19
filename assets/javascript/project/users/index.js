import React, { useState, useEffect } from 'react';
import { Switch, Route, Link, useHistory } from "react-router-dom";
import { Container } from "@material-ui/core";
import { Table, Thead, Tbody, Tr, Th } from 'react-super-responsive-table';
import { Alert, AlertTitle } from '@material-ui/lab';

import UserTable from './user-table';
import UpdateUser from "./update-user";

const EmptyUserList = function () {
	return (
		<section className="section app-card">
			<div className="columns">
				<div className="column is-one-third">
					<img alt="Nothing Here" src="/static/images/undraw/undraw_empty.svg" />
				</div>
				<div className="column is-two-thirds">
					<h1 className="title is-4">No User Yet!</h1>
					<h2 className="subtitle">Create first User below to get started.</h2>
					<p>
						<Link to="/new">
							<button className="button is-primary">
								<span>Create User</span>
							</button>
						</Link>
					</p>
				</div>
			</div>
		</section>
	);
};

const UserList = function (props) {
	const history = useHistory();
	let action;
	if (props.group_role == 2) action = 'Action'
	else action = '';
	return (
		<Container>
			<section className="section app-card">
				{props.isInit &&
					<Alert severity="info" className="my-5">
						<AlertTitle className="subtitle is-4 has-text-weight-bold">Info</AlertTitle>
						<span className="subtitle is-5">{props.message}</span>
					</Alert>}
				<div>
					<label className="title is-3">Manage Intel Group Users</label>
					<button className="button is-outlined is-pulled-right mx-4" onClick={() => history.goBack()}>
						<span>Back</span>
					</button>
					{props.group_role == 2 ?
						<Link to="/users/new" >
							<button className="button is-primary is-pulled-right">
								<span>Add New Users</span>
							</button>
						</Link>
						: null
					}
				</div>
				<Table className="table is-striped is-fullwidth has-vcentered-cells">
					<Thead>
						<Tr>
							<Th>Email</Th>
							<Th>Role</Th>
							<Th>Last access</Th>
							<Th>{action}</Th>
						</Tr>
					</Thead>
					<Tbody>
						{
							props.users.map((user, index) => {
								return <UserTable key={user.id} index={index} myId={props.myId} group_role={props.group_role}
									{...user} delete={(index) => props.deleteUser(index)}
									adminUser={(role, ugr_id) => props.adminUser(role, ugr_id)}
								/>;
							})
						}
						{
							props.emails.map((email, index) => {
								return <UserTable key={email.id} index={index} myId={props.myId} group_role={props.group_role}
									{...email} emaildelete={(index) => props.deleteEmail(index)}
									adminUser={(role, ugr_id) => props.adminUser(role, ugr_id)}
								/>;
							})
						}
					</Tbody>
				</Table>
			</section>
		</Container>
	);
};




const Loading = function () {
	return (
		<div className='app-card has-text-centered'>
			<div className="lds-ripple"><div></div><div></div></div>
			<p className="heading has-text-primary">Loading...</p>
		</div>
	)
}

const User = (props) => {
	const [isLoading, setIsLoading] = useState(true);
	const [users, setUsers] = useState([]);
	const [emails, setEmails] = useState([]);
	const [myId, setMyId] = useState([]);
	const [groupRole, setGroupRole] = useState({});
	const [currentgroup, setCurrentGroup] = useState('');
	const history = useHistory();

	useEffect(() => {
		if (props.currentgroup == '') {
			history.push('/');
		}
		else {
			setCurrentGroup(props.currentgroup);
			if (currentgroup != '' && currentgroup != props.currentgroup) {
				history.push('/intelreports');
			}
			else {
				let params = {
					id: props.currentgroup
				}
				fetch('/api/users', {
					method: 'post',
					headers: {
						'Content-Type': 'application/json',
						'X-CSRFToken': props.client.transports[0].auth.csrfToken
					},
					credentials: 'same-origin',
					body: JSON.stringify(params)
				}).then(res => { return res.json() })
					.then(res => {
						setUsers(res.users);
						setEmails(res.emails);
						setMyId(res.myId);
						setGroupRole(res.grouprole);
						setIsLoading(false);
					});
			}
		}
	}, [props.currentgroup]);

	const handleUserSaved = function (invitedUsers, invitedEmails) {
		const newUsers = [];
		for (let existingUser of users) {
			newUsers.push(existingUser);
		}
		for (let user of invitedUsers) {
			newUsers.push(user);
		}
		setEmails(invitedEmails);
		setUsers(newUsers);
		history.push('/users');
	};


	const deleteUser = function (index) {
		const params = { id: users[index].id };
		if (confirm('Are you sure to perform this action?'))
			fetch('/api/role', {
				method: 'delete',
				headers: {
					'Content-Type': 'application/json',
					'X-CSRFToken': props.client.transports[0].auth.csrfToken
				},
				credentials: 'same-origin',
				body: JSON.stringify(params)
			}).then(res => { return res.json() })
				.then(res => {
					const newUsers = users.slice(0, index).concat(users.slice(index + 1));
					setUsers(newUsers);
				})
	};

	const deleteEmail = function (index) {
		const params = { id: emails[index].id };
		if (confirm('Are you sure to perform this action?'))
			fetch('/api/invite', {
				method: 'delete',
				headers: {
					'Content-Type': 'application/json',
					'X-CSRFToken': props.client.transports[0].auth.csrfToken
				},
				credentials: 'same-origin',
				body: JSON.stringify(params)
			}).then(res => { return res.json() })
				.then(res => {
					const newEmails = emails.slice(0, index).concat(emails.slice(index + 1));
					setEmails(newEmails);
				})
	};

	const adminUser = function (role, ugr_id) {
		if (role == 2) role = 1;
		else if (role == 1) role = 2;
		else if (role == 4) role = 1;
		let params = {
			id: ugr_id,
			role: role,
			groupid: props.currentgroup
		}
		if (confirm('Are you sure to perform this action?')) {
			fetch('/api/role', {
				method: 'put',
				headers: {
					'Content-Type': 'application/json',
					'X-CSRFToken': props.client.transports[0].auth.csrfToken
				},
				credentials: 'same-origin',
				body: JSON.stringify(params)
			}).then(res => { return res.json() })
				.then(res => {
					setUsers(res.users);
					setMyId(res.myId);
					setGroupRole(res.grouprole);
					setIsLoading(false);
				});
		}
	};

	const getDefaultView = function () {
		if (isLoading) {
			return <Loading />
		}
		if (users.length === 0) {
			return <EmptyUserList />;
		} else {
			if (groupRole.role == 0) {
				return (
					<div className='app-card has-text-centered'>
						<div className="lds-ripple"><div></div><div></div></div>
						<p className="subtitle is-3">! You have an invitation to <span className="title is-3 has-text-primary">{groupRole.intelgroup.name}</span> pending. <Link className="muted-link subtitle is-3" to="/account" >Click here to accept.</Link></p>
					</div>
				)
			}
			if (groupRole.role == 1) {
				return (
					<div className='section has-text-centered'>
						<p className="subtitle is-3">! You are now a member of <span className="title is-3 has-text-primary">{groupRole.intelgroup.name}</span>.</p>
					</div>
				)
			}
			if (groupRole.role == 2) {
				// if(props.isPlan)
				return <UserList users={users} emails={emails} deleteUser={deleteUser} deleteEmail={deleteEmail} adminUser={adminUser} myId={myId} group_role={groupRole.role} isInit={props.isInit} message={props.message} isAutoDown={props.isAutoDown} />
				// else return <Plan currentgroup={props.currentgroup} currentrole={currentrole} />
			}
			if (groupRole.role == 4) {
				return (
					<div className='section has-text-centered'>
						<p className="subtitle is-3">Your request for <span className="title is-3 has-text-primary">{groupRole.intelgroup.name}</span> Intel Group has not been accepted yet.</p>
					</div>
				)
			}
			// return <UserList users={users} deleteUser={deleteUser} adminUser={adminUser} myId={myId} group_role={groupRole.role} />
		}
	};

	return (
		<Switch>
			<Route path="/users/new">
				<UpdateUser client={props.client} userSaved={(user, emails) => handleUserSaved(user, emails)} groupid={props.currentgroup} />
			</Route>
			<Route path="/">
				{getDefaultView()}
			</Route>
		</Switch>
	);
};
export default User;