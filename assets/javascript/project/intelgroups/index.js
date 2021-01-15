
import React, {useState, useEffect} from 'react';
import {
		Switch,
		Route,
		Link,
} from "react-router-dom";
import { Table, Thead, Tbody, Tr, Th } from 'react-super-responsive-table';
import Alert from '@material-ui/lab/Alert';

import IntelGroupTable from './intel-group-table';
import {getAction} from "../../api";
import {API_ROOT} from "../const";
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
	const deleteIntelGroup = function (index) {
		if(confirm("Are you sure you want to delete?")){
			const action = getAction(API_ROOT, ['intelgroups', 'leave']);
			const params = {'role': props.intelgroups[index].id};
			props.client.action(window.schema, action, params).then((result) => {
				if(result[0].message){
					setIsAlert(true);
				}
				else
					props.saveIntelgroup(result);
			});
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
		const intelgroup_action = getAction(API_ROOT, ["intelgroups", "list"]);
		const customer_action = getAction(API_ROOT, ["customers", "list"]);
		props.client.action(window.schema, intelgroup_action).then((result) => {
			setIntelgroups(result.results);
			props.client.action(window.schema, customer_action).then((result) => {
				setUsers(result.results);
				setIsLoading(false);
			});
		});
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
		const action = getAction(API_ROOT, ["intelgroups", "invitate"]);
		const params = {'role': intelgroups[index].id};
		props.client.action(window.schema, action, params).then((result) => {
			setIntelgroups(result);
		});
	};

	const rejectInvite = (index) => {
		const action = getAction(API_ROOT, ['intelgroups', 'reject']);
        const params = {'role': intelgroups[index].id};
        props.client.action(window.schema, action, params).then((result) => {
            setIntelgroups(result);
        });
	}

	const saveIntelgroup = (data) => {setIntelgroups(data);}

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