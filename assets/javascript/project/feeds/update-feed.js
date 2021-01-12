import React, {useState, useEffect} from 'react';
import { Link, useHistory, useLocation } from 'react-router-dom';
import {
	Container,
	TextField,
	Button
} from "@material-ui/core";
import Alert from '@material-ui/lab/Alert';

import {getAction} from "../../api";
import {API_ROOT} from "../const";
import Styles from '../styles';

const UpdateFeed = (props) => {
	const [url, setUrl] = useState(props.url || '');
	const [name, setName] = useState(props.name || '');
	const [description, setDescription] = useState(props.description || '');
	const [category, setCategory] = useState(props.category_id || '');
	const [tags, setTags] = useState(props.tags || '');
	const history = useHistory();
	const [confidence, setConfidence] = useState(props.confidence || '');
	const [urlError, setUrlError] = useState(false);
	const [nameError, setNameError] = useState(false);
	const [descriptionError, setDescriptionError] = useState(false);
	const [categoryError, setCategoryError] = useState(false);
	const [tagError, setTagError] = useState(false);
	const [groupError, setGroupError] = useState(false);

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
			confidence: confidence,
		}

		let action;
		if(props.id){
			params['id'] = props.id;
			params['manage_enabled'] = 'true';
		}
		else{
			params['intelgroup_id'] = props.currentgroup;
			params['manage_enabled'] = 'false';
		}
		
		if(url.trim() == '') setUrlError(true);
		if(name.trim() == '') setNameError(true);
		if(description.trim() == '') setDescriptionError(true);
		if(category == '') setCategoryError(true);
		if(tags.trim() == '') setTagError(true);
		if(props.currentgroup == '') setGroupError(true);

		if(url && name && description && category && tags && props.currentgroup != ''){
			if(Boolean(props.id)){
				action = getAction(API_ROOT, ["feeds", "partial_update"]);
				props.client.action(window.schema, action, params).then(result=>{
					props.saveFeed(result);
					history.push('/feeds');
				})
			}
			else{
				if(confirm("Did you really confirm?"))
					fetch('/api/feeds', {
						method: 'post',
						headers: {
							'Content-Type': 'application/json',
							'X-CSRFToken': props.client.transports[0].auth.csrfToken,
						},
						credentials: 'same-origin',
						body: JSON.stringify(params),
					}).then(res=>{return res.json()})
					.then(res=>{
						props.saveFeed(res);
						history.push('/feeds');
					})
			}
		}
	}

	useEffect(() => {

	},[]);

	
	return (
		<Container>
			<h1 className="title is-3 pt-1" >Add Custom Feed</h1>
			<section className="section app-card">
				<div className="columns">
					{props.currentrole.role==2&&
						<div className="column is-two-thirds">
							{groupError && <Alert severity="error" onClose={()=>setGroupError(false)}>Please select Intel Group.</Alert>}
							{Boolean(props.id)?
							<TextField
								id="outlined-full-width1"
								label="URL"
								disabled={true}
								placeholder="http://rss.cnn.com/rss/edition.rss"
								fullWidth
								margin="normal"
								InputLabelProps={{
									shrink: true,
								}}
								variant="outlined"
								value={url}
								onChange={(event) => {setUrl(event.target.value); setUrlError(false);}}
							/>:
							<TextField
								id="outlined-full-width1"
								label="URL"
								placeholder="http://rss.cnn.com/rss/edition.rss"
								fullWidth
								margin="normal"
								InputLabelProps={{
									shrink: true,
								}}
								variant="outlined"
								value={url}
								onChange={(event) => {setUrl(event.target.value); setUrlError(false);}}
							/>}
							{urlError&&<p className="help is-danger"><span>This field may not be blank.</span></p>}
							<TextField
								id="outlined-full-width2"
								label="Name"
								placeholder="write a name of feed"
								fullWidth
								margin="normal"
								InputLabelProps={{
									shrink: true,
								}}
								variant="outlined"
								value={name}
								onChange={(event) => {setName(event.target.value); setNameError(false);}}
							/>
							{nameError&&<p className="help is-danger"><span>This field may not be blank.</span></p>}
							<TextField
								id="outlined-full-width3"
								label="Description"
								placeholder="write about description of feed"
								fullWidth
								margin="normal"
								InputLabelProps={{
									shrink: true,
								}}
								variant="outlined"
								value={description}
								onChange={(event) => {setDescription(event.target.value); setDescriptionError(false);}}
							/>
							{descriptionError&&<p className="help is-danger"><span>This field may not be blank.</span></p>}
							<TextField
								id="outlined-select-currency-native"
								fullWidth
								select
								className="mt-4 mb-2"
								label="Category"
								value={category}
								onChange={(event) => {setCategory(event.target.value); setCategoryError(false);}}
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
							{categoryError&&<p className="help is-danger"><span>This field may not be blank.</span></p>}
							<TextField
								id="outlined-full-width5"
								label="Tags"
								placeholder="Tags Field, e.g. "
								fullWidth
								margin="normal"
								InputLabelProps={{
									shrink: true,
								}}
								variant="outlined"
								value={tags}
								onChange={(event) => {setTags(event.target.value); setTagError(false);}}
							/>
							{tagError&&<p className="help is-danger"><span>This field may not be blank.</span></p>}
							<TextField
								id="outlined-select-currency-native"
								fullWidth
								select
								className="mt-4"
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
						
					}
					{props.currentrole.role==1&&
						<div className="column is-two-thirds">
							{groupError && <Alert severity="error" onClose={()=>setGroupError(false)}>Please select Intel Group.</Alert>}
							<TextField
								id="outlined-full-width1"
								label="URL"
								disabled={true}
								placeholder="http://rss.cnn.com/rss/edition.rss"
								fullWidth
								margin="normal"
								InputLabelProps={{
									shrink: true,
								}}
								variant="outlined"
								value={url}
								onChange={(event) => {setUrl(event.target.value); setUrlError(false);}}
							/>
							{urlError&&<p className="help is-danger"><span>This field may not be blank.</span></p>}
							<TextField
								id="outlined-full-width2"
								label="Name"
								disabled={true}
								placeholder="write a name of feed"
								fullWidth
								margin="normal"
								InputLabelProps={{
									shrink: true,
								}}
								variant="outlined"
								value={name}
								onChange={(event) => {setName(event.target.value); setNameError(false);}}
							/>
							{nameError&&<p className="help is-danger"><span>This field may not be blank.</span></p>}
							<TextField
								id="outlined-full-width3"
								label="Description"
								disabled={true}
								placeholder="write about description of feed"
								fullWidth
								margin="normal"
								InputLabelProps={{
									shrink: true,
								}}
								variant="outlined"
								value={description}
								onChange={(event) => {setDescription(event.target.value); setDescriptionError(false);}}
							/>
							{descriptionError&&<p className="help is-danger"><span>This field may not be blank.</span></p>}
							<TextField
								id="outlined-select-currency-native"
								disabled={true}
								fullWidth
								select
								className="mt-4 mb-2"
								label="Category"
								value={category}
								onChange={(event) => {setCategory(event.target.value); setCategoryError(false);}}
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
							{categoryError&&<p className="help is-danger"><span>This field may not be blank.</span></p>}
							<TextField
								id="outlined-full-width5"
								label="Tags"
								disabled={true}
								placeholder="Tags Field, e.g. "
								fullWidth
								margin="normal"
								InputLabelProps={{
									shrink: true,
								}}
								variant="outlined"
								value={tags}
								onChange={(event) => {setTags(event.target.value); setTagError(false);}}
							/>
							{tagError&&<p className="help is-danger"><span>This field may not be blank.</span></p>}
							<TextField
								id="outlined-select-currency-native"
								fullWidth
								disabled={true}
								select
								className="mt-4"
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
					}
				</div>
				{ (()=>{
					if(Boolean(props.id)){
						if(props.currentrole.role == 2){
							return (<>
								<Button variant="contained" className="button is-primary" onClick={() => updateFeed()}>
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
							<Button variant="contained" className="button is-primary" onClick={() => updateFeed()}>
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