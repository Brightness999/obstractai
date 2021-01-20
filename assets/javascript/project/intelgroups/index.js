
import React, {useState, useEffect} from 'react';
import {
		Switch,
		Route,
		Link,
} from "react-router-dom";
import { Table, Thead, Tbody, Tr, Th } from 'react-super-responsive-table';
import Alert from '@material-ui/lab/Alert';

import IntelGroupTable from './intel-group-table';
import UpdateIntelGroup from "./update-intel-group";
import User from '../users';

const EmptyIntelgroupList = function() {
  return (
	<section className="section app-card">
	  <div className="columns">
		<div className="column is-one-third">
		  <img alt="Nothing Here" src="/static/images/undraw/undraw_empty.svg"/>
		</div>
		<div className="column is-two-thirds">
		  <h1 className="title is-4">No Intel Group Yet!</h1>
		  <h2 className="subtitle">Create your first Intel Group below to get started.</h2>
		  <p>
			<Link to="/intelgroups/new">
			  <button className="button is-primary">
				<span>Create Intel Group</span>
			  </button>
			</Link>
		  </p>
		</div>
	  </div>
	</section>
  );
};

const IntelgroupList = function(props) {
	const [isAlert, setIsAlert] = useState(false);

	const deleteIntelGroup = (index) => {
		if(confirm("Are you sure you want to delete?")){
			const params = {id: props.intelgroups[index].id};
			fetch('/api/leavegroup', {
				method: 'delete',
				headers: {
					'Content-Type': 'application/json',
					'X-CSRFToken': props.client.transports[0].auth.csrfToken
				},
				credentials: 'same-origin',
				body: JSON.stringify(params)
			}).then(res=> {return res.json()})
			.then(res=>{
				if(Boolean(res.message)){
					setIsAlert(true);
				}
				else{
					console.log(res);
					props.saveIntelgroup(res);
				}
			})
		}
	};

	return (
		<section className="section app-card">
			<h1 className="title is-3">All Intel Groups</h1>
			{isAlert && <Alert severity="error" onClose={()=>setIsAlert(false)}>You can't leave the group. Before leaving group, you must make other people admin.</Alert>}
			<Table className="table is-striped is-fullwidth has-vcentered-cells">
				<Thead>
				<Tr>
					<Th>Name</Th>
					<Th>Description</Th>
					<Th>Plan</Th>
					<Th className="has-text-right">Action</Th>
				</Tr>
				</Thead>
				<Tbody>
				{
					props.intelgroups.map((group, index) => {
						// https://stackoverflow.com/a/27009534/8207
						return <IntelGroupTable key={group.id} index={index} {...group} 
							invitation={(data) => props.invitation(data)} deleteIntelGroup={(index) => deleteIntelGroup(index)} rejectInvite={(data)=>props.rejectInvite(data)}
						/>;
					})
				}
				</Tbody>
			</Table>
			<Link to="/intelgroups/new">
				<button className="button is-primary is-outlined">
					<span>Add Intel Group</span>
				</button>
			</Link>
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

const IntelGroup = (props) => {
	const [isLoading, setIsLoading] = useState(true);
	const [intelgroups, setIntelgroups] = useState([]);
	const [users, setUsers] = useState([]);
	
	useEffect(() => {
		fetch('/api/intelgroups',{
			method: 'get',
			headers: {
				'Content-Type': 'application/json'
			},
			credentials: 'same-origin',
		}).then(res=>{return res.json()})
		.then(res=>{
			console.log(res)
			setIntelgroups(res.intelgroups);
			setUsers(res.users);
			setIsLoading(false);
		})
	}, []);
	
	const handleIntelGroupSaved = function(intelgroup) {
		props.intelgroupSave(intelgroup);
		let found = false;
		const newIntelgroup = [];
		for (let existingIntelgroup of intelgroups) {
			if (existingIntelgroup.id === intelgroup.id) {
				newIntelgroup.push(intelgroup);
				found = true;
			} else {
				newIntelgroup.push(existingIntelgroup);
			}
		}
		if (!found) {
			newIntelgroup.push(intelgroup);
		}
		setIntelgroups(newIntelgroup);
	};

	const invitation = function (index) {
		const params = {id:intelgroups[index].id};
		fetch('/api/acceptinvite', {
			method: 'post',
			headers: {
				'Content-Type': 'application/json',
				'X-CSRFToken': props.client.transports[0].auth.csrfToken
			},
			credentials: 'same-origin',
			body: JSON.stringify(params)
		}).then(res=>{return res.json()})
		.then(res=>setIntelgroups(res))
	};

	const rejectInvite = (index) => {
		const params = {id: intelgroups[index].id};
		fetch('/api/rejectinvite',{
			method: 'delete',
			headers: {
				'Content-Type': 'application/json',
				'X-CSRFToken': props.client.transports[0].auth.csrfToken
			},
			credentials: 'same-origin',
			body: JSON.stringify(params)
		}).then(res=>{return res.json()})
		.then(res=>setIntelgroups(res))
	}

	const saveIntelgroup = (data) => {setIntelgroups(data); props.deleteIntelGroup(data)}

	const getDefaultView = () => {
		if (isLoading) {
			return <Loading/>
		}
		if (intelgroups.length === 0) {
			return <EmptyIntelgroupList/>;
		} else {
			return <IntelgroupList client={props.client} intelgroups={intelgroups} saveIntelgroup={saveIntelgroup} invitation={invitation} rejectInvite={rejectInvite} />
		}
	};

	const getIntelgroupById = (group_id) => {
		for(const intelgroup of intelgroups){
			if(intelgroup.intelgroup_id.toString() == group_id)
				return intelgroup;
		};
	}
	  
	const renderUpdateGroup = (data) => {
		if(isLoading){
			return <Loading/>;
		} 
		else {
			const group_id = data.match.params.id;
			const intelgroup = getIntelgroupById(group_id);			
			return(
				<UpdateIntelGroup client={props.client} {...intelgroup} intelgroupSaved={handleIntelGroupSaved} users={users} />
			) 
		}
	}
	
	return (
	  	<Switch  >
			<Route path="/intelgroups/manage/:id">
				<User client={props.client} />
			</Route>
			<Route path="/intelgroups/new">
				<UpdateIntelGroup client={props.client} intelgroupSaved={handleIntelGroupSaved} users={users} />
			</Route>
			<Route path="/intelgroups/:id" render={(props)=> renderUpdateGroup(props)} />
			<Route path="/intelgroups">
				{getDefaultView()}
			</Route> 
	   </Switch>
  );
};
export default IntelGroup;