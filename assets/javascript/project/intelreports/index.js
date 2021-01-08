import React, {useState, useEffect} from "react";
import { Switch, Route, Link } from "react-router-dom";
import { Container, TextField, Grid } from "@material-ui/core";

import ReportCard from "./report-card";
import ViewReport from "./view-report";
import {getAction} from "../../api";
import {API_ROOT} from "../const";
import Styles from '../styles';

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
	const [intelligence, setIntelligence] = useState('0');

	const searchReport = () => {
		let params = {
			category:category,
			indicator:indicator,
			confidence: confidence,
			tag:tag,
			feedname:feedname,
			classification:classification
		}
		if(category!='0' || indicator!='0' || confidence!='0' || tag!='0' || feedname!='0' || classification!='0'){
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
			})
		}
	}
	
	return (
		<Container>
			<section className="section">
				<Grid container>
					<Grid item md={3} xs={6}>
							<label className="title is-2">Intel Reports</label>
					</Grid>
					<Grid item md={1} xs={6}>
						<div style={{paddingTop:16+'px'}}>
							<label className="title is-5" >filter:</label>
						</div>
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
								<option value="0">Indicator</option>
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
								<option value="0">Confidence</option>
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
								<option value="0">Category</option>
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
								<option value="0">Tag</option>
								{props.tags.map((tag) => (
									<option key={tag.id} value={tag.id}>
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
								<option value="0">Feed Name</option>
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
								<option value="0">Classification</option>
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
							<button className="button is-success mt-3" onClick={()=>searchReport()} >
								Filter
							</button>
						</span>
					</Grid>
				</Grid>
			</section>
			{
				props.feeditems.map((feeditem, index) => {
					const indicators = [];
					props.indicators.forEach(indicator => {
						if(feeditem.id == indicator.feeditem_id){
							indicators.push(indicator)
						}
					});
					const classifications = [];
					props.classifications.forEach(classification => {
						props.feeds.forEach(feed => {
							if(feed.uniqueid == feeditem.feed.uniqueid){
								classifications.push(classification);
							}
						});
					});
					const itemfeed = [];
					props.feeds.forEach(feed => {
						if(feed.uniqueid == feeditem.feed.uniqueid){
							itemfeed.push(feed);
						}
					});
					return <ReportCard index={index} key={feeditem.id} feeditem={feeditem} feed={itemfeed} indicators={indicators} classifications={classifications} />;
				})
			}
			
		</Container>
	);
}


const IntelReports = () => {
	let auth = new coreapi.auth.SessionAuthentication({
		csrfCookieName: 'csrftoken',
		csrfHeaderName: 'X-CSRFToken'
	});
	const client = new coreapi.Client({auth: auth});
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
	const confidences = [];
	for (let i=1;i<100;i++){
		confidences[confidences.length] = i;
	}

	useEffect(()=>{
		fetch('/api/reports', {
            method: 'get',
            headers: {
              'Content-Type': 'application/json',
              'accept': 'application/json',
            },
            credentials: 'same-origin',
        }).then((res)=> { return res.json();})
        .then((res)=>{
			setFeeds(res.feeds);
			setCategories(res.categories);
			setIsLoading(false);
			setClassifications(res.extractions);
			setIndicators(res.indicators);
			setFeedItmes(res.feeditems);
			setFeedChannels(res.feedchannels);
			setGlobalIndicators(res.globalindicators);
			setTags(res.tags);
        });
	},[]);

	const Search = (category, tag) => {
		let params ={
			category: category,
			tags: tag
		}
		const action = getAction(API_ROOT, ["feeds", "search"]);
		client.action(window.schema, action, params).then((result) => {
			saveFeed(result);
		});
	}

	const ReportListView = () => {
		if(isLoading){
			return <Loading/>
		}
		else {
			return <ReportList categories={categories} tags={tags} feeds={feeds} client={client}
				classifications={classifications} indicators={indicators} feeditems={feeditems}
				feedchannels={feedchannels} confidences={confidences} tags={tags} globalindicators={globalindicators} />
		}
	}

	const getFeedById = (id) => {
		for(const feeditem of feeditems){
			if(feeditem.id.toString() == id)
				return feeditem;
		};
	}

	const renderViewReport = (props) => {
		if(isLoading){
			return <Loading/>;
		} 
		else {
			const feeditem_id = props.match.params.id;
			const feeditem = getFeedById(feeditem_id);			
			return(
				<ViewReport client={client} {...feeditem} classifications={classifications} indicators={indicators} feeditems={feeditems} feedchannels={feedchannels} />
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