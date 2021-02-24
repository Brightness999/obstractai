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
	const [attributes, setAttributes] = useState([]);
	const [globalattributes, setGlobalAttributes] = useState([]);
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
			setIsLoading(true);
			
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
						setIsLoading(false);
						setIsMessage(false);
						setWebhhook(res.webhook_fail);
						props.saveFeed(res);
						setOpen(false);
						history.push('/feeds');
					}
				})
		}
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
					console.log(res);
					if(res.isUrlExist){
						setUrlMessage(true);
						setIsLoading(false);
					}
					else{
						setFullText(res.fulltext);
						setIndicators(res.indicators);
						setAttributes(res.attributes);
						setGlobalAttributes(res.globalattributes);
						setOpen(true);
						setIsLoading(false);
					}
				})
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
					onClose={()=>{setUrlMessage(false);history.push('/feeds');}}
					aria-labelledby="alert-dialog-title"
					aria-describedby="alert-dialog-description"
				>
					<Alert severity="warning" className="my-5 has-text-centered">
						<AlertTitle className="subtitle is-4 has-text-weight-bold">Warning</AlertTitle>
						<span className="subtitle is-5">! You already have an enabled feed with this URL with title XXXXX. Please edit it.</span>
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
									let str=item.description;
									indicators[index].forEach(indicator => {
										indicator.value.forEach(item => {
											if(!(item*1>0 && item*1<10) && item.indexOf('?') == -1){
												item = item.replace(/'/gi, "").replace(/\\/gi, "").trim();
												let reg = new RegExp(item, 'g'), result, ids = [];
												while ( (result = reg.exec(str)) ) {
													ids.push(result.index);
												}
												for(let i=0;i<ids.length;i++) {
													let astartreg = />/gi, alastreg = /</gi, re, astart = [], alast = [];
													while ( (re = astartreg.exec(str)) ) {
														astart.push(re.index);
													}
													while ( (re = alastreg.exec(str)) ) {
														alast.push(re.index);
													}
													for(let j=0;j<astart.length-1;j++){
														if(ids[i] >= astart[j] && ids[i] <= alast[j+1]){
															let flag = true
															if(indicator.indicator == 'ipv4addr'){
																if((str.substr(ids[i]+item.length, 1)*1 > 0 && str.substr(ids[i]+item.length, 1)*1 < 9) || str.substr(ids[i]+item.length, 1) == '/'){
																	flag = false
																}
															}
															if(indicator.indicator == 'fqdn'){
																if(str.substr(ids[i]-1, 1) == '.' || str.substr(ids[i]-1, 1) == '/' || str.substr(ids[i]-1, 1) == '@'){
																	flag = false
																}
															}
															if(flag){
																let target = "<span style='background:#faeb42;'>" + item + "</span>";
																let target1 = `<Tooltip title='indicator = ${indicator.indicator}'>${target}</Tooltip>`;
																str = str.substring(0, ids[i]) + target1 + str.substr(ids[i]+item.length);
																for(let k=i+1;k<ids.length;k++){
																	ids[k] = ids[k] + target1.length - item.length;
																}
															}
														}
													}
												};
											}
										});
										if(indicator.indicator == 'filename'){
											let imgstart = new RegExp('<img', 'gi'), result, start = [], last=[];
											while ( (result = imgstart.exec(str)) ) {
												start.push(result.index);
											}
											start.forEach(s => {
												for(let i=0;i<str.length;i++){
													let p=0
													if(str[i] == '>' && i > s){
														p++;
														if(p == 1){
															last.push(i);
															break;
														}
													}
												}
											});
											for(let i=0;i<start.length;i++){
												let temp=[];
												indicator.value.forEach(item => {
													let reg = new RegExp(item, 'gi'), result, ids=[];
													while ( (result = reg.exec(str)) ) {
														ids.push(result.index);
													}
													if(ids[0]>start[i] && ids[0]<last[i]){
														temp.push(item);
													}
												});
												let target = str.substring(start[i], last[i]+1);
												let target1 = `<Tooltip title="indicator = ${indicator.indicator}">${target}</Tooltip>`;
												for(let j=i+1;j<start.length;j++){
													start[j] = start[j] + target1.length-target.length;
													last[j] = last[j] + target1.length-target.length;
												}
												str = str.replace(target, target1)
											}
										}
									});
									
									let words = [];
									attributes.forEach(attribute => {
										if(attribute.words_matched.indexOf(",")>-1){
											let temp = attribute.words_matched.split(",");
											words = words.concat(temp);
										}
										else words.push(attribute.words_matched);
									});
									globalattributes.forEach(globalattribute => {
										if(globalattribute.globalattribute.words_matched.indexOf(",")>-1){
											let temp = globalattribute.globalattribute.words_matched.split(",");
											words = words.concat(temp);
										}
										else words.push(globalattribute.globalattribute.words_matched);
									});
									words.forEach(word => {
										let reg = new RegExp(word.trim(), "g"), result, ids = [];
										while ((result = reg.exec(str))) {
											ids.push(result.index);
										}
										for(let i=0;i<ids.length;i++) {
											let astartreg = />/gi, alastreg = /</gi, re, astart = [], alast = [];
											while ( (re = astartreg.exec(str)) ) {
												astart.push(re.index);
											}
											while ( (re = alastreg.exec(str)) ) {
												alast.push(re.index);
											}
											for(let j=0;j<astart.length-1;j++){
												if(ids[i] >= astart[j] && ids[i] <= alast[j+1]){
													let target = `<span style="background:#00e7ff;">${word.trim()}</span>`;
													str = str.substring(0, ids[i]) + target + str.substr(ids[i]+word.trim().length);
													for(let k=i+1;k<ids.length;k++){
														ids[k] = ids[k] + target.length - word.trim().length;
													}
												}
											}
										}
									});
									return <div className="section app-card" key={index}>
										<section className="section">
											<Grid container>
												<Grid item xs={12} md={6}>
													<h1 className="title is-2">{item.title}</h1>
												</Grid>
												<Grid item xs={12} md={6}>
													<span>
														<button className="button is-info is-rounded mx-2">
															<span>
																{props.categories.map((ca, index)=>{
																	if(ca.id == category) return ca.name
																})}
															</span>
														</button>
														{tags.trim() != '' && tags.split(',').map((tag, index)=>{
															return <button key={index} className="button is-warning is-rounded mx-2" >
																<span>{tag}</span>
															</button>
														})}
														<button className="button is-danger is-rounded mx-2" >
															<span>{name}</span>
														</button>
														<button className="button is-primary is-rounded mx-2" >
															<span>{confidence}</span>
														</button>
													</span>
												</Grid>
											</Grid>
										</section>
										<section>
											<Grid container id="">
												<Grid item xs={12} dangerouslySetInnerHTML={{__html:str}}></Grid>
											</Grid>
										</section>
									</div>
								})}
								{(()=>{
									if(Boolean(fulltext.rss) && !Boolean(fulltext.rss.channel.item.length)){
										let str=fulltext.rss.channel.item.description;
										indicators[0].forEach(indicator => {
											indicator.value.forEach(item => {
												if(!(item*1>0 && item*1<10) && item.indexOf('?') == -1){
													item = item.replace(/'/gi, "").replace(/\\/gi, "").trim();
													let reg = new RegExp(item, 'g'), result, ids = [];
													while ( (result = reg.exec(str)) ) {
														ids.push(result.index);
													}
													for(let i=0;i<ids.length;i++) {
														let astartreg = />/gi, alastreg = /</gi, re, astart = [], alast = [];
														while ( (re = astartreg.exec(str)) ) {
															astart.push(re.index);
														}
														while ( (re = alastreg.exec(str)) ) {
															alast.push(re.index);
														}
														for(let j=0;j<astart.length-1;j++){
															if(ids[i] >= astart[j] && ids[i] <= alast[j+1]){
																let flag = true
																if(indicator.indicator == 'ipv4addr'){
																	if((str.substr(ids[i]+item.length, 1)*1 > 0 && str.substr(ids[i]+item.length, 1)*1 < 9) || str.substr(ids[i]+item.length, 1) == '/'){
																		flag = false
																	}
																}
																if(indicator.indicator == 'fqdn'){
																	if(str.substr(ids[i]-1, 1) == '.' || str.substr(ids[i]-1, 1) == '/' || str.substr(ids[i]-1, 1) == '@'){
																		flag = false
																	}
																}
																if(flag){
																	let target = "<span style='background:#faeb42;'>" + item + "</span>";
																	let target1 = `<Tooltip title='indicator = ${indicator.indicator}'>${target}</Tooltip>`;
																	str = str.substring(0, ids[i]) + target1 + str.substr(ids[i]+item.length);
																	for(let k=i+1;k<ids.length;k++){
																		ids[k] = ids[k] + target1.length - item.length;
																	}
																}
															}
														}
													};
												}
											});
											if(indicator.indicator == 'filename'){
												let imgstart = new RegExp('<img', 'gi'), result, start = [], last=[];
												while ( (result = imgstart.exec(str)) ) {
													start.push(result.index);
												}
												start.forEach(s => {
													for(let i=0;i<str.length;i++){
														let p=0
														if(str[i] == '>' && i > s){
															p++;
															if(p == 1){
																last.push(i);
																break;
															}
														}
													}
												});
												for(let i=0;i<start.length;i++){
													let temp=[];
													indicator.value.forEach(item => {
														let reg = new RegExp(item, 'gi'), result, ids=[];
														while ( (result = reg.exec(str)) ) {
															ids.push(result.index);
														}
														if(ids[0]>start[i] && ids[0]<last[i]){
															temp.push(item);
														}
													});
													let target = str.substring(start[i], last[i]+1);
													let target1 = `<Tooltip title="indicator = ${indicator.indicator}">${target}</Tooltip>`;
													for(let j=i+1;j<start.length;j++){
														start[j] = start[j] + target1.length-target.length;
														last[j] = last[j] + target1.length-target.length;
													}
													str = str.replace(target, target1)
												}
											}
										});
										
										let words = [];
										attributes.forEach(attribute => {
											if(attribute.words_matched.indexOf(",")>-1){
												let temp = attribute.words_matched.split(",");
												words = words.concat(temp);
											}
											else words.push(attribute.words_matched);
										});
										globalattributes.forEach(globalattribute => {
											if(globalattribute.globalattribute.words_matched.indexOf(",")>-1){
												let temp = globalattribute.globalattribute.words_matched.split(",");
												words = words.concat(temp);
											}
											else words.push(globalattribute.globalattribute.words_matched);
										});
										words.forEach(word => {
											let reg = new RegExp(word.trim(), "g"), result, ids = [];
											while ((result = reg.exec(str))) {
												ids.push(result.index);
											}
											for(let i=0;i<ids.length;i++) {
												let astartreg = />/gi, alastreg = /</gi, re, astart = [], alast = [];
												while ( (re = astartreg.exec(str)) ) {
													astart.push(re.index);
												}
												while ( (re = alastreg.exec(str)) ) {
													alast.push(re.index);
												}
												for(let j=0;j<astart.length-1;j++){
													if(ids[i] >= astart[j] && ids[i] <= alast[j+1]){
														let target = `<span style="background:#00e7ff;">${word.trim()}</span>`;
														str = str.substring(0, ids[i]) + target + str.substr(ids[i]+word.trim().length);
														for(let k=i+1;k<ids.length;k++){
															ids[k] = ids[k] + target.length - word.trim().length;
														}
													}
												}
											}
										});
										return <div className="section app-card">
											<section className="section">
												<Grid container>
													<Grid item xs={12} md={6}>
														<h1 className="title is-2">{fulltext.rss.channel.item.title}</h1>
													</Grid>
													<Grid item xs={12} md={6}>
														<span>
															<button className="button is-info is-rounded mx-2">
																<span>
																	{props.categories.map((ca, index)=>{
																		if(ca.id == category) return ca.name
																	})}
																</span>
															</button>
															{tags.trim() != '' && tags.trim().split(',').map((tag, index)=>{
																return <button key={index} className="button is-warning is-rounded mx-2" >
																	<span>{tag}</span>
																</button>
															})}
															<button className="button is-danger is-rounded mx-2" >
																<span>{name}</span>
															</button>
															<button className="button is-primary is-rounded mx-2" >
																<span>{confidence}</span>
															</button>
														</span>
													</Grid>
												</Grid>
											</section>
											<section>
												<Grid container id="">
													<Grid item xs={12} dangerouslySetInnerHTML={{__html:str}}></Grid>
												</Grid>
											</section>
										</div>
									}
								})()}
							</DialogContent>
						</Dialog>
					</div>
					<Button variant="contained" className="button is-primary" onClick={() => updateFeed()}>
						Preview
					</Button>
					<Link to="/feeds">
						<button className="button is-text">
							<span>Cancel</span>
						</button>
					</Link>
				</section>
			</Container>
		);
	}
}

export default UpdateFeed