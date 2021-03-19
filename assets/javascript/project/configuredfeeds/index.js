import React, { useState, useEffect } from "react";
import { Switch, Route, Link, useHistory } from "react-router-dom";
import { Container, TextField, Grid } from "@material-ui/core";
import { Alert, AlertTitle } from '@material-ui/lab';

import UpdateFeed from "./update-feed";
import FeedCard from "./feed-card";

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
		if (props.currentrole.role == 2) location.href = `/subscriptions/intelgroup/${props.currentgroup}`;
		else setIsAlert(true);
	}

	return <div className="my-6">
		<h1 className="title is-size-3 has-text-centered py-6">No plan! You must select a plan to perform that action. <a className="tag title is-3" onClick={ManagePlan}>Click here to manage your plan</a></h1>
		{isAlert && <Grid container direction="row" justify="center" alignItems="center">
			<Grid item xs={6}>
				<Alert className="has-text-centered title is-size-4" severity="error" onClose={() => setIsAlert(false)}>! Please contact the feed group administrator to manage intel group plan payment to reinstate access.</Alert>
			</Grid>
		</Grid>}
	</div>
}

const FeedList = (props) => {
	const [category, setCategory] = useState('');
	const [tag, setTag] = useState('');
	const [confidence, setConfidence] = useState('');

	const search = () => {
		let tag_value = "";
		for (const t of props.tags) {
			if (t.id == tag) tag_value = t.name
		}
		props.Search(category, tag_value, confidence);
	}
	return (
		<Container>
			<section className="section">
				{props.isInit &&
					<Alert severity="info" className="my-5">
						<AlertTitle className="subtitle is-4 has-text-weight-bold">Info</AlertTitle>
						<span className="subtitle is-5">{props.message}</span>
					</Alert>}
				<Grid container>
					<Grid item xs={3}>
						<label className="title is-3">Configured Feeds</label>
					</Grid>
					<Grid item xs={1}>
						<div style={{ paddingTop: 16 + 'px' }}>
							<label className="title is-5" >filter:</label>
						</div>
					</Grid>
					<Grid item xs={5}>
						<span>
							<TextField
								id="outlined-select-currency-native"
								select
								className="mx-2"
								value={confidence}
								onChange={(event) => setConfidence(event.target.value)}
								SelectProps={{
									native: true,
								}}
								variant="outlined"
							>
								<option value="" className="has-text-white">Confidence</option>
								{props.confidences.map((confidence) => (
									<option key={confidence} value={confidence}>
										{confidence}
									</option>
								))}
							</TextField>
							<TextField
								id="outlined-select-currency-native"
								select
								className="mx-2"
								value={category}
								onChange={(event) => setCategory(event.target.value)}
								SelectProps={{
									native: true,
								}}
								variant="outlined"
							>
								<option value="" className="has-text-white">Category</option>
								{props.categories.map((category) => (
									<option key={category.id} value={category.id}>
										{category.name}
									</option>
								))}
							</TextField>
							<TextField
								id="outlined-select-currency-native"
								select
								className="mx-2"
								value={tag}
								onChange={(event) => setTag(event.target.value)}
								SelectProps={{
									native: true,
								}}
								variant="outlined"
							>
								<option value="" className="has-text-white">Tag</option>
								{props.tags.map((tag) => (
									<option key={tag.id} value={tag.id}>
										{tag.name}
									</option>
								))}
							</TextField>
						</span>
					</Grid>
					<Grid item xs={3}>
						<span>
							<button className="button is-success is-rounded mx-2" onClick={search} >
								Filter
							</button>
						</span>
					</Grid>
				</Grid>
			</section>
			{
				props.configuredfeeds.map((feed, index) => {
					return <FeedCard index={index} key={feed.id} feed={feed} currentrole={props.currentrole} saveFeed={(data) => props.saveFeed(data)} client={props.client} />;
				})
			}

		</Container>
	);
}


const ConfiguredFeeds = (props) => {
	const [isLoading, setIsLoading] = useState(true);
	const [configuredfeeds, setConfiguredFeeds] = useState([]);
	const [categories, setCategories] = useState([]);
	const [tags, setTags] = useState([]);
	const [banner, setBanner] = useState(false);
	const history = useHistory();
	const confidences = [];
	for (let i = 1; i <= 100; i++) {
		confidences.push(i);
	}

	useEffect(() => {
		if (props.currentgroup == '') {
			history.push('/');
		}
		else {
			let params = { id: props.currentgroup };
			fetch('/api/configuredfeeds', {
				method: 'post',
				headers: {
					'Content-Type': 'application/json',
					'X-CSRFToken': props.client.transports[0].auth.csrfToken
				},
				credentials: 'same-origin',
				body: JSON.stringify(params)
			}).then(res => { return res.json() })
				.then(res => {
					if (Boolean(res.banner)) {
						setBanner(res.banner);
						setIsLoading(false);
					}
					else {
						setConfiguredFeeds(res.configuredfeeds);
						setCategories(res.categories);
						setTags(res.tags);
						setIsLoading(false);
					}
				});
		}
	}, []);


	const Search = (category, tag, confidence) => {
		let params = {
			category: category,
			tags: tag,
			confidence: confidence,
			currentgroup: props.currentgroup
		}
		fetch('/api/searchconfiguredfeeds', {
			method: 'post',
			headers: {
				'Content-Type': 'application/json',
				'X-CSRFToken': props.client.transports[0].auth.csrfToken
			},
			credentials: 'same-origin',
			body: JSON.stringify(params)
		}).then(res => { return res.json() })
			.then(res => {
				saveFeed(res);
			})
	}

	const ConfiguredFeedsView = () => {
		if (isLoading) {
			return <Loading />
		}
		else {
			if (props.currentrole.role == 0) {
				return (
					<div className='app-card has-text-centered'>
						<div className="lds-ripple"><div></div><div></div></div>
						<p className="subtitle is-3">! You have an invitation to <span className="title is-3 has-text-primary">{props.currentrole.intelgroup.name}</span> pending. <Link className="muted-link subtitle is-3" to="/account" >Click here to accept.</Link></p>
					</div>
				)
			}
			if (props.currentrole.role == 1) {
				return (
					<div className='section has-text-centered'>
						<p className="subtitle is-3">! You are now a member of <span className="title is-3 has-text-primary">{props.currentrole.intelgroup.name}</span>.</p>
					</div>
				)
			}
			if (props.currentrole.role == 2) {
				if (props.isPlan)
					return <FeedList client={props.client} saveFeed={saveFeed} configuredfeeds={configuredfeeds} categories={categories} tags={tags}
						Search={Search} confidences={confidences} currentrole={props.currentrole} isInit={props.isInit} message={props.message} />
				else return <Plan currentgroup={props.currentgroup} currentrole={props.currentrole} />
			}
			if (props.currentrole.role == 4) {
				return (
					<div className='section has-text-centered'>
						<p className="subtitle is-3">Your request for <span className="title is-3 has-text-primary">{props.currentrole.intelgroup.name}</span> Intel Group has not been accepted yet.</p>
					</div>
				)
			}
			// else{
			// 	if(props.isPlan){
			// 		return <FeedList client={props.client} saveFeed={saveFeed} feedlist={feedlist} categories={categories} tags={tags} 
			// 			Search={Search} confidences={confidences} currentrole={currentrole} isInit={props.isInit} message={props.message} customfeeds={customfeeds} />
			// 	}
			// 	else{
			// 		return <Plan currentgroup={props.currentgroup} currentrole={currentrole} />
			// 	}

			// }
		}
	}

	const getFeedById = (id) => {
		for (const feed of configuredfeeds) {
			if (feed.uniqueid == id)
				return feed;
		};
	}

	const saveFeed = (result) => {
		setConfiguredFeeds(result);
	}

	const renderUpdateFeed = (data) => {
		if (isLoading) {
			return <Loading />;
		}
		else if (banner) {
			return (
				<div className='app-card has-text-centered'>
					<div className="lds-ripple"><div></div><div></div></div>
					<p className="subtitle is-3">! You can't access this feed.</p>
				</div>
			);
		}
		else {
			const feed_id = data.match.params.id;
			const feed = getFeedById(feed_id);
			return (
				<UpdateFeed client={props.client} {...feed} categories={categories} currentrole={props.currentrole}
					alltags={tags} saveFeed={saveFeed} currentgroup={props.currentgroup} confidences={confidences} />
			);
		}
	}

	return (
		<Switch>
			<Route path="/configuredfeeds/:id" render={(props) => renderUpdateFeed(props)} >
			</Route>
			<Route path="/configuredfeeds">
				{ConfiguredFeedsView()}
			</Route>
		</Switch>
	);
}

export default ConfiguredFeeds;