import React, {useState, useEffect} from "react";
import { Switch, Route, Link, useHistory, useLocation } from "react-router-dom";
import { Container, TextField, Grid } from "@material-ui/core";
import { Alert, AlertTitle } from '@material-ui/lab';
import { Steps } from 'intro.js-react';

import ReportCard from "./report-card";
import ViewReport from "./view-report";

const Loading = () => {
	return (
		<div className='app-card has-text-centered'>
			<div className="lds-ripple"><div></div><div></div></div>
			<p className="heading has-text-primary">Loading...</p>
		</div>
	)
}

const Plan = (props) => {
	const [isAlert, setIsAlert] = useState(false);

	const ManagePlan = () => {
		if(props.currentrole.role == 2) location.href=`/subscriptions/intelgroup/${props.currentgroup}`;
		else setIsAlert(true);
	}

	return <div className="my-6">
			<h1 className="title is-size-3 has-text-centered py-6">No plan! You must select a plan to perform that action. <a className="tag title is-3" onClick={ManagePlan}>Click here to manage your plan</a></h1>
			{isAlert&& <Grid container direction="row" justify="center" alignItems="center">
				<Grid item xs={6}>
					<Alert className="has-text-centered title is-size-4" severity="error" onClose={()=>setIsAlert(false)}>! Please contact the Intel Group administrator to manage intel group plan payment to reinstate access.</Alert>
				</Grid>
			</Grid>}
		</div>
}

const ReportList = (props) => {
	const [category, setCategory] = useState('0');
	const [indicator, setIndicator] = useState('0');
	const [confidence, setConfidence] = useState('0');
	const [tag, setTag] = useState('0');
	const [feedname, setFeedName] = useState('0');
	const [classification, setClassification] = useState('0');
	const [intelligence, setIntelligence] = useState('');
	const [stepsEnabled, setStepsEnabled] = useState(true);
	const history = useHistory();
	const steps = [{
		element: '#card',
		intro: 'Intel Report'
	},{
		element: '#button',
		intro: 'Click to view intelreport.'
	}]
	
	const setOnboarding = () => {
        fetch('/api/onboarding', {
            method: 'get',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': props.client.transports[0].auth.csrfToken,
            },
            credentials: 'same-origin',
        }).then(res=>{return res.json();})
        .then(res=>{
				setStepsEnabled(false);
				window.location.href = '/app';
        })
    }

	return (
		<Container>
			{props.onboarding &&
			<Steps
				enabled={stepsEnabled}
				steps={steps}
				initialStep={0}
				options={{
					skipLabel: 'Skip',
				}}
				onAfterChange={(nextIndex, newElement)=>{
					document.querySelector('.introjs-skipbutton').addEventListener('click', function(){
						setOnboarding();
					})
					if(nextIndex == 1){
						document.querySelector('.introjs-donebutton').style.display='none';
						newElement.addEventListener('click', function(){
							setStepsEnabled(false);
							window.location.href=`/app/intelreports/${props.reports[0].uniqueid}`;
						})
					}
				}}
				onBeforeExit={()=>{return false;}}
				onExit={()=>{}}
			/>}
			<section className="section">
				{props.isInit&&
				<Alert severity="info" className="my-5">
					<AlertTitle className="subtitle is-4 has-text-weight-bold">Info</AlertTitle>
					<span className="subtitle is-5">{props.message}</span>
				</Alert>}
				<Grid container>
					<Grid item md={3} xs={6}>
							<label className="title is-2">Intel Reports</label>
					</Grid>
					<Grid item md={1} xs={6}>
						<p className="title is-5 pt-4" >filter:</p>
					</Grid>
					<Grid item md={7} xs={8}>
						<span className="col-10">
							<TextField
								className="px-2 py-1"
								id="outlined-select-currency-native"
								select
								value={indicator}
								onChange={(event) => setIndicator(event.target.value)}
								SelectProps={{
									native: true,
								}}
								variant="outlined"
							>
								<option value="0" className="has-text-light">Indicator</option>
								{props.globalindicators.map((globalindicator) => (
									<option key={globalindicator.id} value={globalindicator.id}>
										{globalindicator.value}
									</option>
								))}
							</TextField>
			  				<TextField
							  	className="px-2 py-1"
								id="outlined-select-currency-native"
								select
								value={confidence}
								onChange={(event) => setConfidence(event.target.value)}
								SelectProps={{
									native: true,
								}}
								variant="outlined"
							>
								<option value="0" className="has-text-light">Confidence</option>
								{props.confidences.map((confidence) => (
									<option key={confidence} value={confidence}>
										{confidence}
									</option>
								))}
							</TextField>
							<TextField
								id="outlined-select-currency-native"
								className="px-2 py-1"
								select
								value={category}
								onChange={(event) => setCategory(event.target.value)}
								SelectProps={{
									native: true,
								}}
								variant="outlined"
							>
								<option value="0" className="has-text-light">Category</option>
								{props.categories.map((category) => (
									<option key={category.id} value={category.id}>
										{category.name}
									</option>
								))}
							</TextField>
							<TextField
								id="outlined-select-currency-native"
								className="px-2 py-1"
								select
								value={tag}
								onChange={(event) => setTag(event.target.value)}
								SelectProps={{
									native: true,
								}}
								variant="outlined"
							>
								<option value="0" className="has-text-light">Tag</option>
								{props.tags.map((tag) => (
									<option key={tag.id} value={tag.name}>
										{tag.name}
									</option>
								))}
							</TextField>
			  				<TextField
								id="outlined-select-currency-native"
								className="px-2 py-1"
								select
								value={feedname}
								onChange={(event) => setFeedName(event.target.value)}
								SelectProps={{
									native: true,
								}}
								variant="outlined"
							>
								<option value="0" className="has-text-light">Feed Name</option>
								{props.feeds.map((feed) => (
									<option key={feed.id} value={feed.id}>
										{feed.name}
									</option>
								))}
							</TextField>
			  				<TextField
								id="outlined-select-currency-native"
								className="px-2 py-1"
								select
								value={classification}
								onChange={(event) => setClassification(event.target.value)}
								SelectProps={{
									native: true,
								}}
								variant="outlined"
							>
								<option value="0" className="has-text-light">Classification</option>
								{props.classifications.map((classification) => (
									<option key={classification.id} value={classification.words_matched}>
										{classification.words_matched}
									</option>
								))}
								{props.globalattributes.map((classification) => (
									<option key={classification.id} value={classification.words_matched}>
										{classification.globalattribute.words_matched}
									</option>
								))}
							</TextField>
							<TextField
								className="px-2 py-1"
								value={intelligence}
								placeholder="Search for intelligence"
								onChange={(event) => setIntelligence(event.target.value)}
								InputLabelProps={{
									shrink: true,
								}}
								variant="outlined"
							/>
						</span>
					</Grid>
					<Grid item md={1} xs={4}>
						<span>
							<button className="button is-success mt-3" onClick={()=>props.searchReport(category, indicator, tag, feedname, confidence, classification, intelligence)} >
								Filter
							</button>
						</span>
					</Grid>
				</Grid>
			</section>
			{
				props.reports.map((report, index) => {
					const indicators = [];
					props.indicators.forEach(indicator => {
						if(report.feeditem.id == indicator.feeditem_id){
							indicators.push(indicator)
						}
					});
					const classifications = [];
					props.classifications.forEach(classification => {
						if(classification.intelgroup.id == props.currentgroup){
							classifications.push(classification);
						}
					});
					const feeds = []
					props.feeds.forEach(feed => {
						if(feed.feed.id == report.feeditem.feed.id){
							feeds.push(feed)
						}
					});
					return <ReportCard index={index} key={report.id} report={report} feeds={feeds} indicators={indicators} classifications={classifications} globalattributes={props.globalattributes}/>;
				})
			}
			
		</Container>
	);
}

const IntelReports = (props) => {
	const [isLoading, setIsLoading] = useState(true);
	const [categories, setCategories] = useState([]);
	const [tags, setTags] = useState([]);
	const [indicators, setIndicators] = useState([]);
	const [feeds, setFeeds] = useState([]);
	const [classifications, setClassifications] = useState([]);
	const [intelligences, setIntelligences] = useState([]);
	const [globalindicators, setGlobalIndicators] = useState([]);
	const [globalattributes, setGlobalAttributes] = useState([]);
	const [reports, setReports] = useState([]);
	const [banner, setBanner] = useState(false);
	const history = useHistory();
	const confidences = [];
	for (let i=1;i<100;i++){
		confidences[confidences.length] = i;
	}

	useEffect(()=>{
		if(props.currentgroup == '' && !props.onboarding){
			history.push('/');
		}
		else{
			let params = {id:props.currentgroup}
			setIsLoading(true);
			fetch('/api/reports', {
				method: 'post',
				headers: {
				  'Content-Type': 'application/json',
				  'accept': 'application/json',
				  'X-CSRFToken': props.client.transports[0].auth.csrfToken
				},
				credentials: 'same-origin',
				body: JSON.stringify(params)
			}).then((res)=> { return res.json();})
			.then((res)=>{
				console.log(res);
				if(Boolean(res.banner)){
					setBanner(res.banner);
					setIsLoading(false);
				}
				else{
					setFeeds(res.feeds);
					setCategories(res.categories);
					setClassifications(res.extractions);
					setIndicators(res.indicators);
					setGlobalIndicators(res.globalindicators);
					setGlobalAttributes(res.globalattributes);
					setReports(res.reports);
					setTags(res.tags);
					setIsLoading(false);
				}
			});
		}
	},[props.currentgroup]);

	const searchReport = (category, indicator, tag, feedname, confidence, classification, intelligence) => {
		setIsLoading(true);
		let params = {
			id:props.currentgroup,
			category:category,
			indicator:indicator,
			confidence: confidence,
			tag:tag,
			feedname:feedname,
			classification:classification,
			intelligence:intelligence
		}
		fetch('/api/searchreports', {
			method: 'post',
			headers: {
				'Content-Type': 'application/json',
				'X-CSRFToken': props.client.transports[0].auth.csrfToken,
			},
			credentials: 'same-origin',
			body: JSON.stringify(params),
		}).then(res=>{return res.json()})
		.then(res=>{
			setIndicators(res.indicators);
			setReports(res.reports);
			setIsLoading(false);
		})
	}

	const ReportListView = () => {
		if(isLoading){
			return <Loading/>
		}
		else {
			if(props.currentrole.role == 0 ){
				return(
					<div className='app-card has-text-centered'>
						<div className="lds-ripple"><div></div><div></div></div>
						<p className="subtitle is-3">! You have an invitation to <span className="title is-3 has-text-primary">{props.currentrole.intelgroup.name}</span> pending. <Link className="muted-link subtitle is-3" to="/account" >Click here to accept.</Link></p>
					</div>
				);
			}
			else if(props.currentrole.role == 4){
				return(
					<div className='section has-text-centered'>
						<p className="subtitle is-3">Your request for <span className="title is-3 has-text-primary">{props.currentrole.intelgroup.name}</span> Intel Group has not been accepted yet.</p>
					</div>
				)
			}
			else{
				if(props.isPlan)
				return <ReportList categories={categories} tags={tags} client={props.client} isInit={props.isInit} message={props.message} 
				mygroups={props.mygroups} classifications={classifications} feeds={feeds} globalattributes={globalattributes}
				indicators={indicators} searchReport={searchReport} confidences={confidences} globalindicators={globalindicators} 
				reports={reports} isInit={props.isInit} message={props.message} onboarding={props.onboarding} currentgroup={props.currentgroup} />
				else return <Plan currentgroup={props.currentgroup} currentrole={props.currentrole} />
			}
			
		}
	}
	
	const getReportById = (id) => {
		for(const report of reports){
			if(report.uniqueid == id)
			return report;
		};
	}
	
	const getFeedByReport = (report) => {
		for(const feed of feeds){
			if(feed.feed.id == report.feeditem.feed.id)
			return feed;
		};
	}
	
	const renderViewReport = (data) => {
		if(isLoading){
			return <Loading/>;
		}
		else if(banner){
			return(
				<div className='app-card has-text-centered'>
					<div className="lds-ripple"><div></div><div></div></div>
					<p className="subtitle is-3">! You can't access this report.</p>
				</div>
			);
		}
		else {
			const report_id = data.match.params.id;
			const report = getReportById(report_id);
			const feed = getFeedByReport(report)
			return(
				<ViewReport currentgroup={props.currentgroup} banner={banner} feed={feed} onboarding={props.onboarding} client={props.client} {...report} mygroups={props.mygroups} classifications={classifications} globalattributes={globalattributes} indicators={indicators} />
				)
			}
		}
		
		return (
			<Switch>
			<Route path="/intelreports/:id" render={(props) => renderViewReport(props)} ></Route>
			<Route path="/intelreports/:id/:groupid" render={(props) => renderViewReport(props)} ></Route>
			<Route path="/intelreports">
				{ReportListView()}
			</Route> 
		</Switch>
	);
}

export default IntelReports;