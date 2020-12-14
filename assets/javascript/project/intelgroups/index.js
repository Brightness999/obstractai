
import React, {useState, useEffect} from 'react';
import {
		BrowserRouter as Router,
		Switch,
		Route,
		Link,
} from "react-router-dom";
import IntelGroupTable from './intel-group-table';
import {getAction} from "../../api";
import {API_ROOT} from "../const";
import UpdateIntelGroup from "./update-intel-group";

const EmptyIntelgroupList = function() {
  return (
	<section className="section app-card">
	  <div className="columns">
		<div className="column is-one-third">
		  <img alt="Nothing Here" src="static/images/undraw/undraw_empty.svg"/>
		</div>
		<div className="column is-two-thirds">
		  <h1 className="title is-4">No Intel Group Yet!</h1>
		  <h2 className="subtitle">Create your first Intel Group below to get started.</h2>
		  <p>
			<Link to="/new">
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
			<table className="table is-striped is-fullwidth has-vcentered-cells">
				<thead>
				<tr>
					<th>Name</th>
					<th>Description</th>
					<th>Plan</th>
					<th></th>
				</tr>
				</thead>
				<tbody>
				{
					props.intelgroups.map((group, index) => {
						// https://stackoverflow.com/a/27009534/8207
						return <IntelGroupTable key={group.id} index={index} {...group} delete={(index) => props.deleteIntelgroup(index)}
						/>;
					})
				}
				</tbody>
			</table>
			<Link to="/new">
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
	let auth = new coreapi.auth.SessionAuthentication({
		csrfCookieName: 'csrftoken',
		csrfHeaderName: 'X-CSRFToken'
	});
	const client = new coreapi.Client({auth: auth});
	const [isLoading, setIsLoading] = useState(true);
	const [intelgroups, setIntelgroups] = useState([]);
	// const client = props.client;
	
	useEffect(() => {
		const action = getAction(API_ROOT, ["intelgroups", "list"]);
		client.action(window.schema, action).then((result) => {
			setIntelgroups(result.results);
			setIsLoading(false);
		});
	}, []);
	
	const getIntelgroupById = function(id) {
		for (const intelgroup of intelgroups) {
			if (intelgroup.id.toString() === id) {
				return intelgroup;
			}
		}
	};

	const handleIntelGroupSaved = function(intelgroup) {
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

	const deleteIntelgroup = function (index) {
		const action = getAction(API_ROOT, ["intelgroups", "delete"]);
		const params = {id: intelgroups[index].id};
		client.action(window.schema, action, params).then((result) => {
			const newIntelgroups = intelgroups.slice(0, index).concat(intelgroups.slice(index + 1));
			setIntelgroups(newIntelgroups);
		});
	};

	const updateIntelgroup = function (props) {
		if (isLoading) {
			return <Loading/>;
		} else {
			const intelgroupId = props.match.params.id;
			const intelgroup = getIntelgroupById(intelgroupId);
			return (
				<UpdateIntelGroup client={client} {...intelgroup} intelgroupSaved={handleIntelGroupSaved}/>
			);
		}
	};

	const getDefaultView = function() {
	if (isLoading) {
	  return <Loading/>
	}
	if (intelgroups.length === 0) {
	  return <EmptyIntelgroupList/>;
	} else {
	  return <IntelgroupList intelgroups={intelgroups} deleteIntelgroup={deleteIntelgroup}/>
	}
  };
	
	return (
	<Router basename='/intelgroups'>
	  <Switch>
		<Route path="/new">
		  <UpdateIntelGroup client={client} intelgroupSaved={handleIntelGroupSaved}/>
		</Route>
		<Route path="/edit/:id" render={(props) => updateIntelgroup(props)}>
		</Route>
		<Route path="/">
		  {getDefaultView()}
		</Route>
	   </Switch>
	</Router>
  );
};
export default IntelGroup;