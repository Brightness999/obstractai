import React, {useState, useEffect} from 'react';
import { Link, useHistory, useLocation } from 'react-router-dom';
import {
	Container,TextField,Button,Tooltip,Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle, 
} from "@material-ui/core";
import { Alert, AlertTitle } from '@material-ui/lab';
import HelpIcon from '@material-ui/icons/HelpOutline';
import { yellow } from '@material-ui/core/colors';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import IconButton from '@material-ui/core/IconButton';
import Typography from '@material-ui/core/Typography';
import CloseIcon from '@material-ui/icons/Close';

const UpdateFeed = (props) => {
	const [url, setUrl] = useState(props.url || '');
	const [name, setName] = useState(props.name || '');
	const [description, setDescription] = useState(props.description || '');
	const [category, setCategory] = useState(props.category_id || '');
	const [tags, setTags] = useState(props.tags || '');
	const [type, setType] = useState(props.type || '');
	const history = useHistory();
	const [confidence, setConfidence] = useState(props.confidence || '');
	const [urlError, setUrlError] = useState(false);
	const [nameError, setNameError] = useState(false);
	const [descriptionError, setDescriptionError] = useState(false);
	const [categoryError, setCategoryError] = useState(false);
	const [tagError, setTagError] = useState(false);
	const [groupError, setGroupError] = useState(false);
	const [typeError, setTypeError] = useState(false);
	const [isMessage, setIsMessage] = useState(false);
	const [fulltext, setFullText] = useState({});
	const [open, setOpen] = useState(false);
	
	const saveFeed = () => {
		let params ={
			url: url.trim(),
			name: name.trim(),
			description: description.trim(),
			category: category,
			tags: tags.trim(),
			confidence: confidence,
			type:type.trim()
		}
		params['intelgroup_id'] = props.currentgroup;
		params['manage_enabled'] = 'false';
		if(props.currentgroup == '') setGroupError(true);
		if(props.currentgroup != '')
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
				if(Boolean(res.message)){
					setIsMessage(true);
				}
				else{
					setIsMessage(false);
					props.saveFeed(res);
					history.push('/feeds');
				}
			})
	}

	const updateFeed = () => {
		let data;
		props.categories.forEach(cate => {
			if(cate.id == category)
				data = cate;
		});
		let params ={
			url: url.trim(),
			name: name.trim(),
			description: description.trim(),
			category: category,
			tags: tags.trim(),
			confidence: confidence,
			type:type.trim()
		}

		if(props.id){
			params['id'] = props.id;
			params['manage_enabled'] = 'true';
		}
		else{
			params['intelgroup_id'] = props.currentgroup;
			params['manage_enabled'] = 'false';
			if(props.currentgroup == '') setGroupError(true);
		}
		
		if(url.trim() == '') setUrlError(true);
		if(name.trim() == '') setNameError(true);
		if(description.trim() == '') setDescriptionError(true);
		if(category == '') setCategoryError(true);
		if(tags.trim() == '') setTagError(true);
		if(type.trim() == '') setTypeError(true);

		if(url && name && description && category && tags && type ){
			if(Boolean(props.id)){
				fetch('/api/feeds', {
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
					history.push('/feeds');
				})
			}
			else{
				if(props.currentgroup != ''){
					fetch('/api/pullfeed', {
						method: 'post',
						headers: {
							'Content-Type': 'application/json',
							'X-CSRFToken': props.client.transports[0].auth.csrfToken
						},
						credentials: 'same-origin',
						body: JSON.stringify(params)
					}).then(res=>{return res.json()})
					.then(res=>{
						console.log(res.fulltext);
						setFullText(res.fulltext);
						setOpen(true)
					})
				}
			}
		}
	}


	
	return (
		<Container>
			<h1 className="title is-3 pt-1" >Add Custom Feed</h1>
			{isMessage&&
			<Alert severity="warning" className="my-5"  onClose={()=>setIsMessage(false)}>
				<AlertTitle className="subtitle is-4 has-text-weight-bold">Warning</AlertTitle>
				<span className="subtitle is-5">! You must upgrade your Intel Group plan to perform that action.</span>
			</Alert>}
			<section className="section app-card">
				<div className="columns">
					{props.currentrole.role==2&&
						<div className="column is-two-thirds">
							{groupError && <Alert severity="error" className="title is-size-4" onClose={()=>setGroupError(false)}>Please select Intel Group.</Alert>}

							{Boolean(props.id)?
							<TextField
								id="outlined-select-currency-native"
								select
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
							</TextField>:
							<><TextField
								id="outlined-select-currency-native"
								select
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
							</TextField><Tooltip title="Either RSS or Curated" arrow><HelpIcon className="mt-5" style={{color:yellow[900]}} fontSize="large"/></Tooltip></>}
							{typeError&&<p className="help is-danger"><span>This field may not be blank.</span></p>}
							{Boolean(props.id)?
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
							/>:
							<><TextField
								label="URL"
								placeholder="http://rss.cnn.com/rss/edition.rss"
								className="column is-four-fifths"
								margin="normal"
								InputLabelProps={{
									shrink: true,
								}}
								variant="outlined"
								value={url}
								onChange={(event) => {setUrl(event.target.value); setUrlError(false);}}
							/><Tooltip title="If RSS type. URL of the RSS feed, must be RSS." arrow><HelpIcon className="mt-5" style={{color:yellow[900]}} fontSize="large"/></Tooltip></>}
							{urlError&&<p className="help is-danger"><span>This field may not be blank.</span></p>}
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
								<option>Select category</option>
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
							<><TextField
								id="outlined-select-currency-native"
								select
								className="mt-4 column is-four-fifths"
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
							</TextField><Tooltip title="Value between 1 and 100 for how reliable is source" arrow><HelpIcon className="mt-5" style={{color:yellow[900]}} fontSize="large"/></Tooltip></>
						</div>
						
					}
					{props.currentrole.role==1&&
						<div className="column is-two-thirds">
							{groupError && <Alert severity="error" onClose={()=>setGroupError(false)}>Please select Intel Group.</Alert>}
							<><TextField
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
							/><Tooltip title="Name to be displayed in UI" arrow><HelpIcon className="mt-5" style={{color:yellow[900]}} fontSize="large"/></Tooltip></>
							{urlError&&<p className="help is-danger"><span>This field may not be blank.</span></p>}
							<><TextField
								label="Name"
								disabled={true}
								placeholder="write a name of feed"
								className="column is-four-fifths"
								margin="normal"
								InputLabelProps={{
									shrink: true,
								}}
								variant="outlined"
								value={name}
								onChange={(event) => {setName(event.target.value); setNameError(false);}}
							/><Tooltip title="Name to be displayed in UI" arrow><HelpIcon className="mt-5" style={{color:yellow[900]}} fontSize="large"/></Tooltip></>
							{nameError&&<p className="help is-danger"><span>This field may not be blank.</span></p>}
							<><TextField
								id="outlined-full-width3"
								label="Description"
								disabled={true}
								placeholder="write about description of feed"
								class="column is-four-fifths"
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
								disabled={true}
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
								<option>Select category</option>
								{props.categories.map((category) => (
									<option key={category.id} value={category.id}>
										{category.name}
									</option>
								))}
							</TextField><Tooltip title="User can select from a fixed list set by admin" arrow><HelpIcon className="mt-5" style={{color:yellow[900]}} fontSize="large"/></Tooltip></>
							{categoryError&&<p className="help is-danger"><span>This field may not be blank.</span></p>}
							<><TextField
								id="outlined-full-width5"
								label="Tags"
								disabled={true}
								placeholder="Tags Field, e.g. "
								margin="normal"
								className="column is-four-fifths"
								InputLabelProps={{
									shrink: true,
								}}
								variant="outlined"
								value={tags}
								onChange={(event) => {setTags(event.target.value); setTagError(false);}}
							/><Tooltip title="User can assign 0 or more tags (manual entry, auto identify existing tags, letters, numbers and - only)" arrow><HelpIcon className="mt-5" style={{color:yellow[900]}} fontSize="large"/></Tooltip></>
							{tagError&&<p className="help is-danger"><span>This field may not be blank.</span></p>}
							<><TextField
								id="outlined-select-currency-native"
								disabled={true}
								select
								className="mt-4 column is-four-fifths"
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
							</TextField><Tooltip title="Value between 1 and 100 for how reliable is source" arrow><HelpIcon className="mt-5" style={{color:yellow[900]}} fontSize="large"/></Tooltip></>
						</div>
					}
					<Dialog fullScreen open={open} onClose={()=>setOpen(false)}>
					<DialogTitle>
						<button onClick={()=>{setOpen(false); saveFeed()}} className="button is-success mx-4" autoFocus>
							Save
						</button>
						<button onClick={()=>{setOpen(false); }} className="button is-danger" >
							Cancel
						</button>
					</DialogTitle>
						<DialogContent>
							<pre>{JSON.stringify(fulltext, null, 2) }</pre>
						</DialogContent>
					</Dialog>
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