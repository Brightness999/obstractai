import React, {useState, useEffect} from "react";
import {
	Switch,
	Route,
	Link,
} from "react-router-dom";
import {
	Container,
	TextField,
	Grid
} from "@material-ui/core";

import UpdateFeed from "./update-feed";
import FeedCard from "./feed-card";
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


const FeedList = (props) => {
	const [category, setCategory] = useState('');
	const [tag, setTag] = useState('');
	const [confidence, setConfidence] = useState('');
	
	const search = () =>{
		let tag_value = "";
		for(const t of props.tags){
			if(t.id == tag) tag_value = t.name
		}
		props.Search(category, tag_value);
	}
	return (
		<Container>
			<section className="section">
				<Grid container>
					<Grid item xs={3}>
							<label className="title is-3">Feed Store</label>
					</Grid>
					<Grid item xs={1}>
						<div style={{paddingTop:16+'px'}}>
							<label className="title is-5" >filter:</label>
						</div>
					</Grid>
					<Grid item xs={5}>
						<span>
							<TextField
								id="outlined-select-currency-native"
								style={Styles.FeedStoreFilterField}
								select
								value={confidence}
								onChange={(event) => setConfidence(event.target.value)}
								SelectProps={{
									native: true,
								}}
								variant="outlined"
							>
								<option>Confidence</option>
								{props.confidences.map((confidence) => (
									<option key={confidence} value={confidence}>
										{confidence}
									</option>
								))}
							</TextField>
							<TextField
								id="outlined-select-currency-native"
								style={Styles.FeedStoreFilterField}
								select
								value={category}
								onChange={(event) => setCategory(event.target.value)}
								SelectProps={{
									native: true,
								}}
								variant="outlined"
							>
								<option value="">Category</option>
								{props.categories.map((category) => (
									<option key={category.id} value={category.id}>
										{category.name}
									</option>
								))}
							</TextField>
							<TextField
								id="outlined-select-currency-native"
								style={Styles.FeedStoreFilterField}
								select
								value={tag}
								onChange={(event) => setTag(event.target.value)}
								SelectProps={{
									native: true,
								}}
								variant="outlined"
							>
								<option value="">Tag</option>
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
							<button className="button is-outlined" style={Styles.FeedStoreFilterButton} onClick={search} >
								Filter
							</button>
							
						</span>
					</Grid>
				</Grid>
			</section>
			<section className="section" style={Styles.SectionStyle}>
				<Link to="/feeds/new">
					<button style={Styles.FeedStoreCreateButton}>
						<span className="icon is-small">
							<i className="fa fa-plus"></i>
						</span>
						<span>Create custom feed</span>
					</button>
				</Link>
			</section>
			{
				props.feedlist.map((feed, index) => {
					return <FeedCard index={index} key={feed.id} feed={feed} />;
				})
			}
			
		</Container>
	);
}


const Feeds = (props) => {
	let auth = new coreapi.auth.SessionAuthentication({
		csrfCookieName: 'csrftoken',
		csrfHeaderName: 'X-CSRFToken'
	});
	const client = new coreapi.Client({auth: auth});
	const [isLoading, setIsLoading] = useState(true);
	const [feedlist, setFeedList] = useState([]);
	const [categories, setCategories] = useState([]);
	const [tags, setTags] = useState([]);
	const [currentgroup, setCurrentGroup] = useState(props.currentgroup);
	const confidences = [];
	for(let i=1;i<=100;i++){
		confidences.push(i);
	}

	useEffect(()=>{
		setCurrentGroup(props.currentgroup);
	},[props.currentgroup]);

	useEffect(()=>{
		const feed_action = getAction(API_ROOT, ["feeds", "list"]);
		const category_action = getAction(API_ROOT, ["categories", "list"]);
		const tag_action = getAction(API_ROOT, ["tags", "list"]);
		client.action(window.schema, feed_action).then((result) => {
			setFeedList(result.results);
			client.action(window.schema, category_action).then((result) => {
				setCategories(result.results);
				client.action(window.schema, tag_action).then((result) => {
					setTags(result.results);
					setIsLoading(false);
				})
			});
		});
	},[]);

	const Search = (category, tag) => {
		let auth = new coreapi.auth.SessionAuthentication({
			csrfCookieName: 'csrftoken',
			csrfHeaderName: 'X-CSRFToken'
		});
		const client = new coreapi.Client({auth: auth});
		let params ={
			category: category,
			tags: tag
		}
		const action = getAction(API_ROOT, ["feeds", "search"]);
		client.action(window.schema, action, params).then((result) => {
			saveFeed(result);
		});
	}

	const FeedListView = () => {
		if(isLoading){
			return <Loading/>
		} else {
			return <FeedList feedlist={feedlist} categories={categories} tags={tags} Search={Search} confidences={confidences} />
		}
	}

	const getFeedById = (id) => {
		for(const feed of feedlist){
			if(feed.id.toString() == id)
				return feed;
		};
	}

	const saveFeed = (result) => {
		setFeedList(result);
	}

	const renderUpdateFeed = (props) => {
		if(isLoading){
			return <Loading/>;
		} 
		else {
			const feed_id = props.match.params.id;
			const feed = getFeedById(feed_id);			
			return(
				<UpdateFeed client={client} currentgroup={currentgroup} {...feed} categories={categories} 
					alltags={tags} saveFeed={saveFeed} currentgroup={props.currentgroup} confidences={confidences} />
			) 
		}
	}

	return (
		<Switch>
			<Route path="/feeds/new">
				<UpdateFeed client={client} currentgroup={currentgroup} categories={categories} 
					alltags={tags} saveFeed={saveFeed} currentgroup={props.currentgroup} confidences={confidences} />
			</Route>
			<Route path="/feeds/edit/:id" render={(props) => renderUpdateFeed(props)} >
			</Route>
			<Route path="/feeds">
				{FeedListView()}
			</Route> 
		</Switch>
	);
}

export default Feeds;