import React, {useState, useEffect} from "react";
import { Switch, Route, Link, useHistory } from "react-router-dom";
import { Container, TextField, Grid } from "@material-ui/core";

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

const ReportList = (props) => {
	const [category, setCategory] = useState('0');
	const [indicator, setIndicator] = useState('0');
	const [confidence, setConfidence] = useState('0');
	const [tag, setTag] = useState('0');
	const [feedname, setFeedName] = useState('0');
	const [classification, setClassification] = useState('0');
	const [intelligence, setIntelligence] = useState('');
	
	return (
		<Container>
			<section className="section">
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
									<option key={classification.id} value={classification.id}>
										{classification.words_matched}
									</option>
								))}
							</TextField>
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
						if(classification.intelgroup.id == report.intelgroup.id){
							classifications.push(classification);
						}
					});
					return <ReportCard index={index} key={report.id} report={report} indicators={indicators} classifications={classifications} />;
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
	const [feeditems, setFeedItmes] = useState([]);
	const [feedchannels, setFeedChannels] = useState([]);
	const [globalindicators, setGlobalIndicators] = useState([]);
	const [reports, setReports] = useState([]);
	const history = useHistory();
	const confidences = [];
	for (let i=1;i<100;i++){
		confidences[confidences.length] = i;
	}

	useEffect(()=>{
		if(props.currentgroup == '') history.push('/')
		else{
			fetch(`/api/reports/${props.currentgroup}`, {
				method: 'get',
				headers: {
				  'Content-Type': 'application/json',
				  'accept': 'application/json',
				},
				credentials: 'same-origin',
			}).then((res)=> { return res.json();})
			.then((res)=>{
				console.log(res);
				setFeeds(res.feeds);
				setCategories(res.categories);
				setClassifications(res.extractions);
				setIndicators(res.indicators);
				setFeedItmes(res.feeditems);
				setFeedChannels(res.feedchannels);
				setGlobalIndicators(res.globalindicators);
				setReports(res.reports);
				setTags(res.tags);
				setIsLoading(false);
			});
		}
	},[props.currentgroup]);

	const searchReport = (category, indicator, tag, feedname, confidence, classification, intelligence) => {
		setIsLoading(true);
		let params = {
			category:category,
			indicator:indicator,
			confidence: confidence,
			tag:tag,
			feedname:feedname,
			classification:classification
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
			console.log(res);
			setFeeds(res.feeds);
			setCategories(res.categories);
			setClassifications(res.extractions);
			setIndicators(res.indicators);
			setFeedItmes(res.feeditems);
			setFeedChannels(res.feedchannels);
			setGlobalIndicators(res.globalindicators);
			setTags(res.tags);
			setIsLoading(false);
		})
	}

	const ReportListView = () => {
		if(isLoading){
			return <Loading/>
		}
		else {
			return <ReportList categories={categories} tags={tags} feeds={feeds} client={props.client} mygroups={props.mygroups}
				classifications={classifications} indicators={indicators} feeditems={feeditems} searchReport={searchReport}
				feedchannels={feedchannels} confidences={confidences} globalindicators={globalindicators} reports={reports} />
		}
	}

	const getFeedById = (id) => {
		for(const report of reports){
			if(report.id.toString() == id)
				return report;
		};
	}

	const renderViewReport = (data) => {
		if(isLoading){
			return <Loading/>;
		} 
		else {
			const report_id = data.match.params.id;
			const report = getFeedById(report_id);
			return(
				<ViewReport client={props.client} {...report} classifications={classifications} indicators={indicators} feeditems={feeditems} feedchannels={feedchannels} feeds={feeds} />
			)
		}
	}

	return (
		<Switch>
			<Route path="/intelreports/:id" render={(props) => renderViewReport(props)} >
			</Route>
			<Route path="/intelreports">
				{ReportListView()}
			</Route> 
		</Switch>
	);
}

export default IntelReports;