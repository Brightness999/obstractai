
import React, {useState, useEffect} from 'react';
import {
		BrowserRouter as Router,
		Switch,
		Route,
		Link,
		useParams,
		useLocation
} from "react-router-dom";
import { Table, Thead, Tbody, Tr, Th } from 'react-super-responsive-table';
import UserTable from './user-table';
import {getAction} from "../../api";
import {API_ROOT} from "../const";
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
				<span className="icon is-small"><i className="fa fa-plus"></i></span>
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
	let action;
	if(props.group_role == 2) action = 'Action'
	else action = '';
	return (
		<section className="section app-card">
			<div style={{marginBottom: 30+'px'}}>
				<label className="title is-4">Manage Intel Group Users</label>
				{ props.group_role == 2 ? 
						<Link to="/new" >
							<button className="button is-primary is-filled is-pulled-right">
								<span className="icon is-small">
									<i className="fa fa-plus"></i>
								</span>
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
						<Th>Last access(UI and API)</Th>
						<Th>{ action }</Th>
					</Tr>
				</Thead>
				<Tbody>
				{
					props.users.map((user, index) => {
						// https://stackoverflow.com/a/27009534/8207
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
	const path = useLocation().pathname;
	const group_id = useParams().id;
	let auth = new coreapi.auth.SessionAuthentication({
		csrfCookieName: 'csrftoken',
		csrfHeaderName: 'X-CSRFToken'
	});
	const client = new coreapi.Client({auth: auth});
	const [isLoading, setIsLoading] = useState(true);
	const [users, setUsers] = useState([]);
	const [myId, setMyId] = useState([]);
	const [groupRole, setGroupRole] = useState([]);
	let params = {
		role: group_id
	}
	useEffect(() => {
		const action = getAction(API_ROOT, ["users", "manage"]);
		client.action(window.schema, action, params).then((result) => {
			setUsers(result[2]);
			setMyId(result[1]);
			setGroupRole(result[0]);
			setIsLoading(false);
		});
	}, []);

	const handleUserSaved = function(user) {
		let found = false;
		const newUser = [];
		for (let existingUser of users) {
			if (existingUser.id === user.id) {
				newUser.push(user);
				found = true;
			} else {
				newUser.push(existingUser);
			}
		}
		if (!found) {
			newUser.push(user);
		}
		setUsers(newUser);
	};

	const deleteUser = function (index) {
		const action = getAction(API_ROOT, ["intelgrouprole", "delete"]);
		const params = {id: users[index].id};
		client.action(window.schema, action, params).then((result) => {
			const newUsers = users.slice(0, index).concat(users.slice(index + 1));
			setUsers(newUsers);
		});
	};

	const adminUser = function (role,ugr_id) {
		if(role == 2) role = 1;
		else if(role == 1) role = 2;
		const action = getAction(API_ROOT, ["intelgrouprole", "makeadmin"]);
		let params = {
			'role': ugr_id
		}
		client.action(window.schema, action,params).then((result) => {
			setUsers(result[2]);
			setMyId(result[1]);
			setGroupRole(result[0]);
			setIsLoading(false);
		});
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
	<Router basename='/home/intelgroups/manage'>
	  <Switch>
		<Route path="/new">
		  <UpdateUser client={client} userSaved={handleUserSaved} group_id={group_id} path={path.split('/')[3]} />
		</Route>
		<Route path="/">
		  {getDefaultView()}
		</Route>
	   </Switch>
	</Router>
  );
};
export default User;