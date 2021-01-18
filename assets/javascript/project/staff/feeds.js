import React, {useState, useEffect} from "react";
import {
	Switch,
	Route,
	Link,
	useHistory
} from "react-router-dom";
import {
	Container,
	TextField,
	Grid
} from "@material-ui/core";

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


const FeedList = (props) => {
	const [category, setCategory] = useState('');
	const [tag, setTag] = useState('');
	const [confidence, setConfidence] = useState('');
	
	const Search = () =>{
		let tag_value = "";
		for(const t of props.tags){
			if(t.id == tag) tag_value = t.name
		}
		props.Search(category, tag_value, confidence);
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
								select
								className="mx-2"
								value={confidence}
								onChange={(event) => setConfidence(event.target.value)}
								SelectProps={{
									native: true,
								}}
								variant="outlined"
							>
								<option value="">Confidence</option>
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
								<option value="">Category</option>
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
							<button className="button is-success is-rounded mx-2" onClick={Search} >
								Filter
							</button>
							
						</span>
					</Grid>
				</Grid>
			</section>
			<section className="section" >
				<Link to="/feeds/new">
					<button className="button is-medium is-link is-rounded">
						<span>Create feed</span>
					</button>
				</Link>
			</section>
			{
				props.feedlist.map((feed, index) => {
					return <FeedCard index={index} key={feed.id} feed={feed} saveFeed={(data)=>props.saveFeed(data)} client={props.client} />;
				})
			}
			
		</Container>
	);
}


const StaffFeeds = (props) => {
	const [isLoading, setIsLoading] = useState(true);
	const [feedlist, setFeedList] = useState([]);
	const [categories, setCategories] = useState([]);
	const [tags, setTags] = useState([]);
	const confidences = [];
	for(let i=1;i<=100;i++){
		confidences.push(i);
	}

	useEffect(()=>{
        let params = {
            currentgroup: props.currentgroup
        }
        fetch('/api/feedlist', {
            method: 'post',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': props.client.transports[0].auth.csrfToken
            },
            credentials: 'same-origin',
            body: JSON.stringify(params)
        }).then(res=>{return res.json()})
        .then(res=>{
            setFeedList(res.feedlist);
            setCategories(res.categories);
            setTags(res.tags);
            setIsLoading(false);
        });
	},[props.currentgroup]);

	const Search = (category, tag, confidence) => {
		let params ={
			category: category,
			tags: tag,
			confidence: confidence,
			currentgroup: props.currentgroup
		}
        fetch('/api/searchfeeds', {
            method: 'post',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': props.client.transports[0].auth.csrfToken
            },
            credentials: 'same-origin',
            body: JSON.stringify(params)
        }).then(res=>{return res.json()})
        .then(res=>{
            saveFeed(res);
        })
	}

	const FeedListView = () => {
		if(isLoading){
			return <Loading/>
		}
		else {
			return <FeedList client={props.client} saveFeed={saveFeed} feedlist={feedlist} categories={categories} tags={tags} Search={Search} confidences={confidences} />
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

	const renderUpdateFeed = (data) => {
		if(isLoading){
			return <Loading/>;
		}
		else {
		const feed_id = data.match.params.id;
			const feed = getFeedById(feed_id);			
			return(
				<UpdateFeed client={props.client} {...feed} categories={categories} 
					alltags={tags} saveFeed={saveFeed} currentgroup={props.currentgroup} confidences={confidences} />
			) ;
		}
	}

	return (
		<Switch>
			<Route path="/feeds/new">
				<UpdateFeed client={props.client} categories={categories} 
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

export default StaffFeeds;