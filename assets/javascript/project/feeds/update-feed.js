import React, { useState } from 'react';
import { Link, useHistory } from 'react-router-dom';
import {
	Container,TextField,Button,Tooltip, Dialog, DialogContent, DialogTitle, Slider, Typography, Grid
} from "@material-ui/core";
import { Alert, AlertTitle } from '@material-ui/lab';
import HelpIcon from '@material-ui/icons/HelpOutline';
import { yellow } from '@material-ui/core/colors';
import { Steps } from 'intro.js-react';

const Loading = () => {
	return (
		<div className='app-card has-text-centered'>
			<div className="lds-ripple"><div></div><div></div></div>
			<p className="heading has-text-primary">Loading...</p>
		</div>
	)
}

const UpdateFeed = (props) => {
	const [url, setUrl] = useState(props.url || '');
	const [name, setName] = useState(props.name || '');
	const [description, setDescription] = useState(props.description || '');
	const [category, setCategory] = useState(props.category?props.category.id: '');
	const [tags, setTags] = useState(props.tags || '');
	const [type, setType] = useState(props.type || '');
	const history = useHistory();
	const [confidence, setConfidence] = useState(props.confidence || 0);
	const [urlError, setUrlError] = useState(false);
	const [nameError, setNameError] = useState(false);
	const [descriptionError, setDescriptionError] = useState(false);
	const [categoryError, setCategoryError] = useState(false);
	const [tagError, setTagError] = useState(false);
	const [groupError, setGroupError] = useState(false);
	const [typeError, setTypeError] = useState(false);
	const [isMessage, setIsMessage] = useState(false);
	const [fulltext, setFullText] = useState({});
	const [indicators, setIndicators] = useState([]);
	const [open, setOpen] = useState(false);
	const [urlMessage, setUrlMessage] = useState(false);
	const [isLoading, setIsLoading] = useState(false);
	const [webhook, setWebhhook] = useState(false);
	const value = props.confidence ? props.confidence : 0;
	const [stepsEnabled, setStepsEnabled] = useState(true);
	const steps = [{
		element: '#type',
		intro: 'Type of Intel Group Feed'
	},{
		element: '#url',
		intro: 'Url of Intel Group Feed'
	},{
		element: '#name',
		intro: 'Name to be displayed in U'
	},{
		element: '#description',
		intro: 'Description to be displayed in UI'
	},{
		element: '#category',
		intro: 'User can select from fixed list set by admin'
	},{
		element: '#tags',
		intro: 'User can assign 0 or more tags (manual entry, auto identify existing tags, letters, numbers and - only)'
	},{
		element: '#confidence',
		intro: 'Confidence of Intel Group Feed'
	},]

	const saveFeed = () => {
		setIsLoading(true);
		let str = tags.trim();
		if(str[str.length-1] == ',') str = str.substring(0, str.length-2);
		let params ={
			url: url.trim(),
			name: name.trim(),
			description: description.trim(),
			category: category,
			tags: str,
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
					setIsLoading(false);
					setIsMessage(true);
				}
				else{
					if(Boolean(res.isUrlExist)){
						setIsLoading(false);
						setUrlMessage(true);
					}
					else{
						setIsLoading(false);
						setIsMessage(false);
						setWebhhook(res.webhook_fail);
						props.saveFeed(res);
						setOpen(false);
						history.push('/feeds');
					}
				}
			})
	}

	const updateFeed = () => {
		let data;
		props.categories.forEach(cate => {
			if(cate.id == category)
				data = cate;
		});
		let str = tags.trim();
		if(str[str.length-1] == ',') str = str.substring(0, str.length-2);
		let params ={
			url: url.trim(),
			name: name.trim(),
			description: description.trim(),
			category: category=='Select category'?'':category,
			tags: str,
			confidence: confidence,
			type: type=='Select Type'?'':type.trim()
		}

		if(props.id){
			params['id'] = props.id;
			params['groupid'] = props.currentgroup;
		}
		else{
			params['groupid'] = props.currentgroup;
			if(props.currentgroup == '') setGroupError(true);
		}
		
		if(Boolean(props.id)){
			setIsLoading(true);
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
				setWebhhook(res.webhook_fail);
				setIsLoading(false);
				props.saveFeed(res);
				history.push('/feeds');
			})
		}
		else{
			if(url.trim() == '') setUrlError(true);
			if(name.trim() == '') setNameError(true);
			if(description.trim() == '') setDescriptionError(true);
			if(category == '' || category == 'Select category') setCategoryError(true);
			if(type.trim() == '' || type == 'Select Type') setTypeError(true);
			if(url && name && description && category && type ){
				setIsLoading(true);
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
						console.log(typeof(res.fulltext.rss.channel.item))
						console.log( res.fulltext.rss.channel.item)
						setFullText(res.fulltext);
						setIndicators(res.indicators);
						setOpen(true);
						setIsLoading(false);
					})
				}
			}
		}
	}
	
	if(isLoading){
		return <Loading />
	}
	else{
		return (
			<Container>
				{props.mygroups.length == 0 &&
				<Steps
					enabled={stepsEnabled}
					steps={steps}
					initialStep={0}
					onExit={(index)=>{
					setStepsEnabled(false);
					if(index==6)
						window.location.href="/home/intelreports";
					}}
					options={{
					doneLabel: 'Next'
					}}
				/>}
				<h1 className="title is-3 pt-1" >Add Custom Feed</h1>
				<Dialog
					maxWidth="md"
					fullWidth
					open={isMessage}
					onClose={()=>setIsMessage(false)}
					aria-labelledby="alert-dialog-title"
					aria-describedby="alert-dialog-description"
				>
					<Alert severity="error" className="my-5">
						<AlertTitle className="subtitle is-4 has-text-weight-bold">Warning</AlertTitle>
						<span className="subtitle is-5">! You must upgrade your Intel Group plan to perform that action.</span>
					</Alert>
				</Dialog>
				<Dialog
					maxWidth="md"
					fullWidth
					open={webhook}
					onClose={()=>setWebhhook(false)}
					aria-labelledby="alert-dialog-title"
					aria-describedby="alert-dialog-description"
				>
					<Alert severity="warning" className="my-5">
						<AlertTitle className="subtitle is-4 has-text-weight-bold">Fail</AlertTitle>
						<span className="subtitle is-5">Outgoing webhook is failed.</span>
					</Alert>
				</Dialog>
				<Dialog
					maxWidth="md"
					fullWidth
					open={urlMessage}
					onClose={()=>setUrlMessage(false)}
					aria-labelledby="alert-dialog-title"
					aria-describedby="alert-dialog-description"
				>
					<Alert severity="warning" className="my-5 has-text-centered">
						<AlertTitle className="subtitle is-4 has-text-weight-bold">Warning</AlertTitle>
						<span className="subtitle is-5">! This URL already exists.</span>
					</Alert>
				</Dialog>
				<section className="section app-card">
					<div className="columns">
						<div className="column is-two-thirds">
							{groupError && <Alert severity="error" className="title is-size-4" onClose={()=>setGroupError(false)}>Please select Intel Group.</Alert>}
							{Boolean(props.id)?
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
							</TextField>:
							<><TextField
								id="type"
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
								id="url"
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
								id="name"
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
								id="description"
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
								id="category"
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
								id="tags"
								label="Tags"
								placeholder="Tags Field, e.g."
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
								id="confidence"
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
						
						<Dialog fullScreen open={open} onClose={()=>setOpen(false)}>
							<DialogTitle>
								<button onClick={()=>{saveFeed()}} className="button is-success mx-4" autoFocus>
									Save
								</button>
								<button onClick={()=>{setOpen(false); }} className="button is-danger" >
									Cancel
								</button>
							</DialogTitle>
							<DialogContent>
								{Boolean(fulltext.rss) && Boolean(fulltext.rss.channel.item.length) && fulltext.rss.channel.item.map((item, index)=>{
									return <section className="section app-card" key={index}>
										<div className="columns">
											<div className="column is-one-thirds">
												<Grid container>
													<Grid item xs={12} md={8} className="container" style={{position:'relative'}}>
														<Grid container>
															<Grid item xs={12} md={6}>
																<div>
																	<span className="title has-text-weight-bold is-4"> Name: </span>
																	<span> {item.title} </span>
																</div>
																<div dangerouslySetInnerHTML={{__html:item.description}}>
																</div>
																<div>
																	<span className="title has-text-weight-bold is-4"> URL: </span>
																	<span> {item.link} </span>
																</div>
							
															</Grid>
															<Grid item xs={12} md={6}>
																<div>
																	<span className="title has-text-weight-bold is-4"> Publish Date: </span>
																	<span>{ new Date(item.pubDate).toLocaleString()}</span>
																</div>
															</Grid>
														</Grid>
														<div>
															<span>
																<button className="button is-info is-rounded mx-2" >
																<span>{category}</span>
																</button>
																<button className="button is-link is-rounded is-text mx-2">
																	<span>{name}</span>
																</button>
															</span>
														</div>
													</Grid>
													<Grid item xs={12} md={4}>
														<Grid container>
															<Grid item xs={3} className="pt-4">
																<span>Confidence:</span>
															</Grid>
															<Grid item xs={9} className="py-2">
																<button className="button is-primary is-rounded">
																	<span>{confidence}</span>
																</button>
															</Grid>
														</Grid>
														<Grid container>
															<Grid item xs={3} className="pt-4">
																<span>Indicators:</span>
															</Grid>
															<Grid item xs={9} className="py-2">
																{indicators[index].map((indicator, i)=>{
																	return <button key={i} className="button is-success is-rounded mx-1 my-1" >
																		<span>{indicator}</span>
																	</button>
																})}
																
															</Grid>
														</Grid>
													</Grid>
											</Grid>
											</div>
										</div>
									</section>
								
								})}
								{Boolean(fulltext.rss) && !Boolean(fulltext.rss.channel.item.length) && 
									<section className="section app-card">
										<div className="columns">
											<div className="column is-one-thirds">
												<Grid container>
													<Grid item xs={12} md={8} className="container" style={{position:'relative'}}>
														<Grid container>
															<Grid item xs={12} md={6}>
																<div>
																	<span className="title has-text-weight-bold is-4"> Name: </span>
																	<span> {fulltext.rss.channel.item.title} </span>
																</div>
																<div dangerouslySetInnerHTML={{__html:fulltext.rss.channel.item.description}}>
																</div>
																<div>
																	<span className="title has-text-weight-bold is-4"> URL: </span>
																	<span> {fulltext.rss.channel.item.link} </span>
																</div>
							
															</Grid>
															<Grid item xs={12} md={6}>
																<div>
																	<span className="title has-text-weight-bold is-4"> Publish Date: </span>
																	<span>{ new Date(fulltext.rss.channel.item.pubDate).toLocaleString()}</span>
																</div>
															</Grid>
														</Grid>
														<div>
															<span>
																<button className="button is-info is-rounded mx-2" >
																<span>{props.categories.map((ca, index)=>{
																	if(ca.id == category) return ca.name
																})}</span>
																</button>
																<button className="button is-link is-rounded is-text mx-2">
																	<span>{name}</span>
																</button>
															</span>
														</div>
													</Grid>
													<Grid item xs={12} md={4}>
														<Grid container>
															<Grid item xs={3} className="pt-4">
																<span>Confidence:</span>
															</Grid>
															<Grid item xs={9} className="py-2">
																<button className="button is-primary is-rounded">
																	<span>{confidence}</span>
																</button>
															</Grid>
														</Grid>
														<Grid container>
															<Grid item xs={3} className="pt-4">
																<span>Indicators:</span>
															</Grid>
															<Grid item xs={9} className="py-2">
																{indicators.map((indicator, i)=>{
																	return <button key={i} className="button is-success is-rounded mx-1 my-1" >
																		<span>{indicator}</span>
																	</button>
																})}
																
															</Grid>
														</Grid>
													</Grid>
											</Grid>
											</div>
										</div>
									</section>
								}
							</DialogContent>
						</Dialog>
					</div>
					{ (()=>{
						if(Boolean(props.id)){
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
						else{
							return (<>
								<Button variant="contained" className="button is-primary" onClick={() => updateFeed()}>
									Preview
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
}

export default UpdateFeed