import React, {useState, useEffect} from 'react';
import {
		BrowserRouter as Router,
		Switch,
		Route,
		Link,
		useParams,
		useHistory,
} from "react-router-dom";
import { Table, Thead, Tbody, Tr, Th } from 'react-super-responsive-table';

import UserTable from './user-table';
import UpdateUser from "./update-user";

const EmptyUserList = function() {
  return (
	<section className="section app-card">
	  <div className="columns">
		<div className="column is-one-third">
		  <img alt="Nothing Here" src="/static/images/undraw/undraw_empty.svg"/>
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

const UserList = function(props) {
	const history = useHistory();
	let action;
	if(props.group_role == 2) action = 'Action'
	else action = '';
	return (
		<section className="section app-card">
			<div>
				<label className="title is-4">Manage Intel Group Users</label>
				<button className="button is-outlined is-pulled-right mx-4" onClick={()=>history.goBack()}>
					<span>Back</span>
				</button>
				{ props.group_role == 2 ? 
						<Link to="/new" >
							<button className="button is-primary is-pulled-right">
								<span>Invite Users</span>
							</button>
						</Link>
					:null
				}
			</div>
			<Table className="table is-striped is-fullwidth has-vcentered-cells">
				<Thead>
					<Tr>
						<Th>Email</Th>
						<Th>Role</Th>
						<Th>Last access</Th>
						<Th>{ action }</Th>
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
				</Tbody>
			</Table>
		</section>
	);
};




const Loading = function() {
	return (
		<div className='app-card has-text-centered'>
			<div className="lds-ripple"><div></div><div></div></div>
			<p className="heading has-text-primary">Loading...</p>
		</div>
	)
}

const User = (props) => {
	const group_id = useParams().id;
	const [isLoading, setIsLoading] = useState(true);
	const [users, setUsers] = useState([]);
	const [myId, setMyId] = useState([]);
	const [groupRole, setGroupRole] = useState([]);
	let params = {
		id: group_id
	}
	useEffect(() => {
		fetch('/api/users', {
			method: 'post',
			headers: {
				'Content-Type': 'application/json',
				'X-CSRFToken': props.client.transports[0].auth.csrfToken
			},
			credentials: 'same-origin',
			body: JSON.stringify(params)
		}).then(res=>{return res.json()})
		.then(res=>{
			setUsers(res.users);
			setMyId(res.myId);
			setGroupRole(res.grouprole);
			setIsLoading(false);
		})
	}, []);

	const handleUserSaved = function(invitedUsers) {
		const newUsers = [];
		for (let existingUser of users) {
			newUsers.push(existingUser);
		}
		for (let user of invitedUsers) {
			newUsers.push(user);
		}
		setUsers(newUsers);
	};

	const deleteUser = function (index) {
		const params = {id: users[index].id};
		if(confirm('Are you sure to revoke invite?'))
			fetch('/api/role', {
				method: 'delete',
				headers: {
					'Content-Type': 'application/json',
					'X-CSRFToken': props.client.transports[0].auth.csrfToken
				},
				credentials: 'same-origin',
				body: JSON.stringify(params)
			}).then(res=>{return res.json()})
			.then(res=>{
				const newUsers = users.slice(0, index).concat(users.slice(index + 1));
				setUsers(newUsers);
			})
	};

	const adminUser = function (role,ugr_id) {
		if(role == 2) role = 1;
		else if(role == 1) role = 2;
		let params = {
			id: ugr_id,
			role: role,
			groupid: group_id
		}
		fetch('/api/role',{
			method: 'put',
			headers: {
				'Content-Type': 'application/json',
				'X-CSRFToken': props.client.transports[0].auth.csrfToken
			},
			credentials: 'same-origin',
			body: JSON.stringify(params)
		}).then(res=>{return res.json()})
		.then(res=>{
			setUsers(res.users);
			setMyId(res.myId);
			setGroupRole(res.grouprole);
			setIsLoading(false);
		})
	};

	const getDefaultView = function() {
		if (isLoading) {
			return <Loading/>
		}
		if (users.length === 0) {
			return <EmptyUserList/>;
		} else {
			return <UserList users={users} deleteUser={deleteUser} adminUser={adminUser} myId={myId} group_role={groupRole} />
		}
  };
	
	return (
	<Router basename={`/home/intelgroups/manage/${group_id}`}>
	  <Switch>
		<Route path="/new">
		  <UpdateUser client={props.client} userSaved={handleUserSaved} group_id={group_id} />
		</Route>
		<Route path="/">
		  {getDefaultView()}
		</Route>
	   </Switch>
	</Router>
  );
};
export default User;