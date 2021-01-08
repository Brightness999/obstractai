import React, { useState, useEffect } from "react";
import { Link, Switch, Route } from "react-router-dom";
import { Paper, Grid, Card } from "@material-ui/core";

import Plan from "./plan";
import { getAction } from "../../api";
import { API_ROOT } from "../const";
import Styles from "../styles";
import ManagePlan from "./manage-plan";


const Loading = function() {
	return (
		<div className='app-card has-text-centered'>
			<div className="lds-ripple"><div></div><div></div></div>
			<p className="heading has-text-primary">Loading...</p>
		</div>
	)
}

const EmptyPlan = function() {
	return (
	  <section className="section app-card">
		<div className="columns">
		  <div className="column is-one-third">
			<img alt="Nothing Here" src="/static/images/undraw/undraw_empty.svg"/>
		  </div>
		  <div className="column is-two-thirds">
			<h1 className="title is-4">No Plan Yet!</h1>
			<h2 className="subtitle">Register Plan below to get started.</h2>
			<p>
			  <Link to="/new">
				<button className="button is-primary">
				  <span className="icon is-small"><i className="fa fa-plus"></i></span>
				  <span>Register Plan</span>
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
		<section className="section">
			<h1 className="title is-3">Manage Plan</h1>
			<Grid container spacing={3}>
				{props.plans.map((plan, index)=>{
					return	<Plan index={index} key={plan.id} plan={plan} />
				})}
			</Grid>
		</section>
	);
};

const CurrentPlan = () => {
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
			setPlans(result.results);
			setIsLoading(false);
		});
	}, []);

	const CurrentPlanView = function() {
		if (isLoading) {
			return <Loading/>
		}
		if (plans.length === 0) {
			return <EmptyPlan/>;
		} else {
			return <PlanList plans={plans}/>
		}
	};

	return (
		<Switch>
			<Route path="/manageplan/manage">
				<ManagePlan client={client} plans={plans} />
			</Route>
			<Route path="/manageplan">
				{CurrentPlanView()}
			</Route>
		</Switch>
	);
}

export default CurrentPlan;