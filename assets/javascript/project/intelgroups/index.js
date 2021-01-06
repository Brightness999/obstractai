
import React, {useState, useEffect} from 'react';
import {
		Switch,
		Route,
		Link,
		useParams,
		useLocation
} from "react-router-dom";
import { Table, Thead, Tbody, Tr, Th } from 'react-super-responsive-table';
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
				<span className="icon is-small"><i className="fa fa-plus"></i></span>
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
	return (
		<section className="section app-card">
			<h1 className="subtitle">All Intel Groups</h1>
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
							invitation={(data) => props.invitation(data)} deleteIntelGroup={(index) => props.deleteIntelGroup(index)}
						/>;
					})
				}
				</Tbody>
			</Table>
			<Link to="/intelgroups/new">
				<button className="button is-primary is-outlined">
					<span className="icon is-small">
						<i className="fa fa-plus"></i>
					</span>
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
		if(confirm("Do you want to accept?")){
			const action = getAction(API_ROOT, ["intelgroups", "invitate"]);
			const params = {'role': intelgroups[index].id};
			props.client.action(window.schema, action, params).then((result) => {
				setIntelgroups(result);
			});
		}
	};

	const deleteIntelGroup = function (index) {
		if(confirm("Are you sure you want to delete?")){
			const action = getAction(API_ROOT, ["intelgroups", "deleteIntelGroup"]);
			const params = {'role': intelgroups[index].intelgroup_id};
			props.client.action(window.schema, action, params).then((result) => {
				const newIntelgroup = intelgroups.slice(0, index).concat(intelgroups.slice(index+1));
				setIntelgroups(newIntelgroup);
			});
		}
	};


	const getDefaultView = () => {
		if (isLoading) {
			return <Loading/>
		}
		if (intelgroups.length === 0) {
			return <EmptyIntelgroupList/>;
		} else {
			return <IntelgroupList intelgroups={intelgroups} invitation={invitation} deleteIntelGroup={deleteIntelGroup}/>
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
				<User/>
			</Route>
			<Route path="/intelgroups/new">
				<UpdateIntelGroup client={props.client} intelgroupSaved={handleIntelGroupSaved} users={users} />
			</Route>
			<Route path="/intelgroups/:id" render={(props)=> renderUpdateGroup(props)} />
				{/* <UpdateIntelGroup client={props.client} intelgroupSaved={handleIntelGroupSaved} users={users} /> */}
			{/* </Route> */}
			<Route path="/intelgroups">
				{getDefaultView()}
			</Route> 
	   </Switch>
  );
};
export default IntelGroup;