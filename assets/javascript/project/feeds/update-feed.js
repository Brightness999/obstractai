import React, {useState, useEffect} from 'react';
import { Link, useHistory, useLocation } from 'react-router-dom';
import {
	Container,
	TextField,
	Button
} from "@material-ui/core";

import {getAction} from "../../api";
import {API_ROOT} from "../const";

import Styles from '../styles';



const UpdateFeed = (props) => {
	console.log(props.currentgroup);
	const [url, setUrl] = useState(props.url || '');
	const [name, setName] = useState(props.name || '');
	const [description, setDescription] = useState(props.description || '');
	const [category, setCategory] = useState(props.category_id || '');
	const [tags, setTags] = useState(props.tags || '');
	const history = useHistory();
	const [confidence, setConfidence] = useState(props.confidence || '');

	let auth = new coreapi.auth.SessionAuthentication({
		csrfCookieName: 'csrftoken',
		csrfHeaderName: 'X-CSRFToken'
	});
	const client = new coreapi.Client({auth: auth});

	const updateFeed = () => {
		let data;
		props.categories.forEach(cate => {
			if(cate.id == category)
				data = cate;
		});
		let params ={
			url: url,
			name: name,
			description: description,
			category: category,
			tags: tags,
			confidence: confidence
		}

		let action;
		if(props.id){
			params['id'] = props.id;
			params['manage_enabled'] = 'true';
			action = getAction(API_ROOT, ["feeds", "partial_update"]);
		}
		else{
			params['manage_enabled'] = 'false';
			action = getAction(API_ROOT, ["feeds", "add"]);
		}
		if(url && name && description && category && tags){
			if(confirm("Did you really confirm?"))
				client.action(window.schema, action, params).then((result) => {
					props.saveFeed(result);
					history.push('/feeds');
				}).catch((error) => {
					console.log("Error: ", error);
					setErrors(error.content);
				});
		}
	}

	useEffect(() => {

	},[]);

	
	return (
		<Container>
			<h1 className="title is-3" style={Styles.FeedAddTitle}>Add Custom Feed</h1>
			<section className="section app-card">
				<div className="columns">
					<div className="column is-two-thirds">
						
						<TextField
							id="outlined-full-width1"
							label="URL"
							style={Styles.TextField}
							placeholder="http://rss.cnn.com/rss/edition.rss"
							fullWidth
							margin="normal"
							InputLabelProps={{
								shrink: true,
							}}
							variant="outlined"
							value={url}
							onChange={(event) => setUrl(event.target.value)}
						/>
						<TextField
							id="outlined-full-width2"
							label="Name"
							style={Styles.TextField}
							placeholder="write a name of feed"
							fullWidth
							margin="normal"
							InputLabelProps={{
								shrink: true,
							}}
							variant="outlined"
							value={name}
							onChange={(event) => setName(event.target.value)}
						/>
						<TextField
							id="outlined-full-width3"
							label="Description"
							style={Styles.TextField}
							placeholder="write about description of feed"
							fullWidth
							margin="normal"
							InputLabelProps={{
								shrink: true,
							}}
							variant="outlined"
							value={description}
							onChange={(event) => setDescription(event.target.value)}
						/>
						<TextField
							id="outlined-select-currency-native"
							style={Styles.TextField}
							fullWidth
							select
							label="Category"
							value={category}
							onChange={(event) => setCategory(event.target.value)}
							SelectProps={{
								native: true,
							}}
							variant="outlined"
						>
							<option>Select category</option>
							{props.categories.map((category) => (
								<option key={category.id} value={category.id}>
									{category.name}
								</option>
							))}
						</TextField>
						<TextField
							id="outlined-full-width5"
							label="Tags"
							style={Styles.TextField}
							placeholder="Tags Field, e.g. "
							fullWidth
							margin="normal"
							InputLabelProps={{
								shrink: true,
							}}
							variant="outlined"
							value={tags}
							onChange={(event) => setTags(event.target.value)}
						/>
						<TextField
							id="outlined-select-currency-native"
							style={Styles.TextField}
							fullWidth
							select
							label="Confidence"
							value={confidence}
							onChange={(event) => setConfidence(event.target.value)}
							SelectProps={{
								native: true,
							}}
							variant="outlined"
						>
							<option>Select confidence</option>
							{props.confidences.map((confidence) => (
								<option key={confidence} value={confidence}>
									{confidence}
								</option>
							))}
						</TextField>
					</div>
				</div>
				{ (()=>{
					if(Boolean(props.id)){
						if(props.manage_enabled == 'true'){
							return (<>
								<Button variant="contained" style={Styles.FeedAddButton} onClick={() => updateFeed()}>
									Enable
								</Button>
								<Link to="/feeds">
									<button className="button is-text">
										<span>Cancel</span>
									</button>
								</Link></>
							);
						}
						else return(
							<Link to="/feeds">
								<button className="button is-text">
									<span>Back</span>
								</button>
							</Link>
						);
					}
					else{
						return (<>
							<Button variant="contained" style={Styles.FeedAddButton} onClick={() => updateFeed()}>
								Save
							</Button>
							<Link to="/feeds">
								<button className="button is-text">
									<span>Cancel</span>
								</button>
							</Link></>
						);
					}

				}
				)()}
			</section>
		</Container>
	);
}

export default UpdateFeed