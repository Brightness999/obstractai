import React, { useState } from 'react';
import { Link, useHistory } from 'react-router-dom';
import {
	Container,TextField,Button,Tooltip,Slider,Typography
} from "@material-ui/core";
import { Alert } from '@material-ui/lab';
import HelpIcon from '@material-ui/icons/HelpOutline';
import { yellow } from '@material-ui/core/colors';

const UpdateFeed = (props) => {
	const [url, setUrl] = useState(props.feed.url || '');
	const [name, setName] = useState(props.name || '');
	const [description, setDescription] = useState(props.description || '');
	const [category, setCategory] = useState(props.category?props.category.id: '');
	const [tags, setTags] = useState(props.tags || '');
	const [type, setType] = useState(props.feed.type || '');
	const history = useHistory();
	const [confidence, setConfidence] = useState(props.confidence || 0);
	const [nameError, setNameError] = useState(false);
	const [descriptionError, setDescriptionError] = useState(false);
	const [categoryError, setCategoryError] = useState(false);
	const [tagError, setTagError] = useState(false);
	const [groupError, setGroupError] = useState(false);
	const value = props.confidence ? props.confidence : 0;
	
	const updateFeed = () => {
		let data;
		props.categories.forEach(cate => {
			if(cate.id == category)
				data = cate;
		});
		let params ={
			id: props.id,
			name: name.trim(),
			description: description.trim(),
			category: category=='Select category'?'':category,
			tags: tags.trim(),
			confidence: confidence,
		}
		
		if(Boolean(props.id)){
			fetch('/api/configuredfeeds', {
				method: 'put',
				headers: {
					'Content-Type': 'application/json',
					'X-CSRFToken': props.client.transports[0].auth.csrfToken
				},
				credentials: 'same-origin',
				body: JSON.stringify(params)
			}).then(res=>{return res.json()})
			.then(res=>{
				props.saveFeed(res);
				history.push('/configuredfeeds');
			})
		}
	}
	
	return (
		<Container>
			<h1 className="title is-3 pt-1" >{props.isenable?"Edit settings":"Edit settings and enable"}</h1>
			<section className="section app-card">
				<div className="columns">
					<div className="column is-two-thirds">
						{groupError && <Alert severity="error" className="title is-size-4" onClose={()=>setGroupError(false)}>Please select Intel Group.</Alert>}
						<TextField
							id="outlined-select-currency-native"
							select
							disabled={true}
							className="mt-4 mb-2 column is-four-fifths"
							label="Type"
							value={type}
							onChange={(event) => {setType(event.target.value); setTypeError(false);}}
							SelectProps={{
								native: true,
							}}
							variant="outlined"
						>
							<option className="has-text-light">Select Type</option>
							<option value="rss">RSS</option>
							<option value="curated">Curated</option>
						</TextField>
						<TextField
							label="URL"
							disabled={true}
							placeholder="http://rss.cnn.com/rss/edition.rss"
							className="column is-four-fifths"
							margin="normal"
							InputLabelProps={{
								shrink: true,
							}}
							variant="outlined"
							value={url}
							onChange={(event) => {setUrl(event.target.value); setUrlError(false);}}
						/>
						<TextField
							label="Name"
							placeholder="write a name of feed"
							className="column is-four-fifths"
							margin="normal"
							InputLabelProps={{
								shrink: true,
							}}
							variant="outlined"
							value={name}
							onChange={(event) => {setName(event.target.value); setNameError(false);}}
						/><Tooltip title="Name to be displayed in UI" arrow><HelpIcon className="mt-5" style={{color:yellow[900]}} fontSize="large"/></Tooltip>
						{nameError&&<p className="help is-danger"><span>This field may not be blank.</span></p>}
						<><TextField
							id="outlined-full-width3"
							label="Description"
							placeholder="write about description of feed"
							className="column is-four-fifths"
							margin="normal"
							InputLabelProps={{
								shrink: true,
							}}
							variant="outlined"
							value={description}
							onChange={(event) => {setDescription(event.target.value); setDescriptionError(false);}}
						/><Tooltip title="Description to be displayed in UI" arrow><HelpIcon className="mt-5" style={{color:yellow[900]}} fontSize="large"/></Tooltip></>
						{descriptionError&&<p className="help is-danger"><span>This field may not be blank.</span></p>}
						<><TextField
							id="outlined-select-currency-native"
							select
							className="mt-4 mb-2 column is-four-fifths"
							label="Category"
							value={category}
							onChange={(event) => {setCategory(event.target.value); setCategoryError(false);}}
							SelectProps={{
								native: true,
							}}
							variant="outlined"
						>
							<option className="has-text-light">Select category</option>
							{props.categories.map((category) => (
								<option key={category.id} value={category.id}>
									{category.name}
								</option>
							))}
						</TextField><Tooltip title="User can select from fixed list set by admin" arrow><HelpIcon className="mt-5" style={{color:yellow[900]}} fontSize="large"/></Tooltip></>
						{categoryError&&<p className="help is-danger"><span>This field may not be blank.</span></p>}
						<><TextField
							id="outlined-full-width5"
							label="Tags"
							placeholder="Tags Field, e.g. "
							className="column is-four-fifths"
							margin="normal"
							InputLabelProps={{
								shrink: true,
							}}
							variant="outlined"
							value={tags}
							onChange={(event) => {setTags(event.target.value); setTagError(false);}}
						/><Tooltip title="User can assign 0 or more tags (manual entry, auto identify existing tags, letters, numbers and - only)" arrow><HelpIcon className="mt-5" style={{color:yellow[900]}} fontSize="large"/></Tooltip></>
						{tagError&&<p className="help is-danger"><span>This field may not be blank.</span></p>}
						<Typography id="non-linear-slider" gutterBottom>
								Confidence
						</Typography>
						<Slider
							className="mt-6 column is-four-fifths"
							defaultValue={value}
							onChange={(e,value)=>setConfidence(value)}
							aria-labelledby="discrete-slider-always"
							step={1}
							min={0}
							max={100}
							marks={[{value:0, label:0},{value:100, label:100}]}
							valueLabelDisplay="on"
						/>
					</div>
				</div>
				<Button variant="contained" className="button is-primary" onClick={() => updateFeed()}>
					{props.isenable?"Save":"Enable"}
				</Button>
				<Link to="/configuredfeeds">
					<button className="button is-text">
						<span>Cancel</span>
					</button>
				</Link>
			</section>
		</Container>
	);
}

export default UpdateFeed