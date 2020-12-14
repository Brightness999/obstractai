
import React, {useState, useEffect} from 'react';
import {
		BrowserRouter as Router,
		Switch,
		Route,
		Link,
} from "react-router-dom";
import PlanTable from './plan-table';
import {getAction} from "../../api";
import {API_ROOT} from "../const";
import UpdatePlan from "./update-plan";

const EmptyPlanList = function() {
  return (
	<section className="section app-card">
	  <div className="columns">
		<div className="column is-one-third">
		  <img alt="Nothing Here" src="static/images/undraw/undraw_empty.svg"/>
		</div>
		<div className="column is-two-thirds">
		  <h1 className="title is-4">No Plan Yet!</h1>
		  <h2 className="subtitle">Create first Plan below to get started.</h2>
		  <p>
			<Link to="/new">
			  <button className="button is-primary">
				<span className="icon is-small"><i className="fa fa-plus"></i></span>
				<span>Create Plan</span>
			  </button>
			</Link>
		  </p>
		</div>
	  </div>
	</section>
  );
};

const PlanList = function(props) {
	return (
		<section className="section app-card">
			<h1 className="subtitle">All Plan</h1>
			<table className="table is-striped is-fullwidth has-vcentered-cells">
				<thead>
				<tr>
					<th>Name</th>
					<th>Type</th>
                    <th>Annual Price</th>
                    <th>Monthy Price</th>
                    <th>Max Feeds</th>
                    <th>Max Users</th>
					<th>Enable Cutomize Feeds</th>
                    <th>Enable API</th>
                    <th>Enable Cutomize Extraction</th>
					<th></th>
				</tr>
				</thead>
				<tbody>
				{
					props.plans.map((plan, index) => {
						// https://stackoverflow.com/a/27009534/8207
						return <PlanTable key={plan.id} index={index} {...plan} delete={(index) => props.deletePlan(index)}
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
					<span>Add Plan</span>
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

const Plan = (props) => {
	let auth = new coreapi.auth.SessionAuthentication({
		csrfCookieName: 'csrftoken',
		csrfHeaderName: 'X-CSRFToken'
	});
	const client = new coreapi.Client({auth: auth});
	const [isLoading, setIsLoading] = useState(true);
	const [plans, setPlans] = useState([]);
	
	useEffect(() => {
		const action = getAction(API_ROOT, ["plans", "list"]);
		client.action(window.schema, action).then((result) => {
			setIntelgroups(result.results);
			setIsLoading(false);
		});
	}, []);
	
	const getPlanById = function(id) {
		for (const plan of plans) {
			if (plan.id.toString() === id) {
				return plan;
			}
		}
	};

	const handlePlanSaved = function(plan) {
		let found = false;
		const newPlan = [];
		for (let existingPlan of plans) {
			if (existingPlan.id === plan.id) {
				newPlan.push(plan);
				found = true;
			} else {
				newPlan.push(existingPlan);
			}
		}
		if (!found) {
			newPlan.push(plan);
		}
		setIntelgroups(newPlan);
	};

	const deletePlan = function (index) {
		const action = getAction(API_ROOT, ["plans", "delete"]);
		const params = {id: plans[index].id};
		client.action(window.schema, action, params).then((result) => {
			const newPlans = plans.slice(0, index).concat(plans.slice(index + 1));
			setIntelgroups(newPlans);
		});
	};

	const updatePlan = function (props) {
		if (isLoading) {
			return <Loading/>;
		} else {
			const planId = props.match.params.id;
			const plan = getPlanById(planId);
			return (
				<UpdatePlan client={client} {...plan} planSaved={handlePlanSaved}/>
			);
		}
	};

	const getDefaultView = function() {
	if (isLoading) {
	  return <Loading/>
	}
	if (intelgroups.length === 0) {
	  return <EmptyPlanList/>;
	} else {
	  return <PlanList plans={plans} deletePlan={deletePlan}/>
	}
  };
	
	return (
	<Router basename='/plans'>
	  <Switch>
		<Route path="/new">
		  <UpdatePlan client={client} planSaved={handlePlanSaved}/>
		</Route>
		<Route path="/edit/:id" render={(props) => updatePlan(props)}>
		</Route>
		<Route path="/">
		  {getDefaultView()}
		</Route>
	   </Switch>
	</Router>
  );
};
export default Plan;