import React, { useState, useEffect } from 'react';
import { Link, useHistory } from "react-router-dom";
import ReactTags from 'react-tag-autocomplete';
import { Tooltip, TextField, Grid, Container } from "@material-ui/core";
import HelpIcon from '@material-ui/icons/Help';
import { yellow } from '@material-ui/core/colors';
import { Steps, Hints } from 'intro.js-react';

const Welcome = (props) => {
	const history = useHistory();
	useEffect(()=>{
		if(props.currentgroup != "")
		{
			history.push('intelreports');
		}
	},[props.currentgroup]);
	return (
		<div className="my-6">
			<h1 className="title is-size-2 has-text-centered py-6">Welcome to Cyobstract</h1>
			{props.mygroups.map(mygroup=>{
				if(mygroup.role == 0)
					return <div className="section app-card has-text-centered" key={mygroup.id}>
						<p className="subtitle is-4">! You have an invitation to <span className="title is-3 has-text-primary">{mygroup.intelgroup.name}</span> pending. <Link className="muted-link subtitle is-4 has-text-danger" to="/account" >Click here to accept.</Link></p>
					</div> 
			})}
		</div>
	);
}

const AddIntelgroup = (props) => {

	const [name, setName] = useState('');
  	const [description, setDescription] = useState('');
	const [isPublic, setIsPublic] = useState(false);
	const [isRefuse, setIsRefuse] = useState(false);
	const [tags, setTags] = useState([]);
	const history = useHistory();
	const [stepsEnabled, setStepsEnabled] = useState(true);
	const initialStep = 0;
	const steps = [{
		title: 'Welcome',
		intro: 'Hello World! 👋'
	  },{
		element: '#name',
		intro: 'Intel Group Name'
	  },{
		element: '#description',
		intro: 'Intel Group Description'
	  },{
		element: '#users',
		intro: 'Users to invite Intel Group'
	  },{
		element: '#public',
		intro: 'Options to make public or private Intel Group'
	  },{
		element: '#button',
		intro: 'Click to create Intel Group'
	  }]

	const reacttag= React.createRef();
	const onDelete= (i)=> {
		var temp = tags.slice(0)
		temp.splice(i, 1)
		setTags(temp)
	}
	  
	const onAddition = (tag)=> {
		let mailformat = /^([A-Za-z0-9_\-\.\+])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$/;
		if(tag.name.match(mailformat)){
			var temp = [].concat(tags, tag)
			setTags(temp)
		}
	}

	const saveIntelgroup = function() {
		const emails = [];
		tags.forEach(tag => {
			if(tag.name.search('\\+') > -1){
				let pluspos = tag.name.search('\\+');
				let lastpos = tag.name.search('@');
				let flag = true;
				emails.forEach(email => {
					if(email == tag.name.substring(0,pluspos) + tag.name.substr(lastpos)){
					flag = false;
					}
				});
				if(flag){
					emails.push(tag.name.substring(0,pluspos) + tag.name.substr(lastpos))
				}
			}
			else{
				emails.push(tag.name)
			}
		});
		let params = {
		  name: name,
		  description: description,
		  emails: emails,
		  ispublic: isPublic?true:false,
		};
		if((name != '' && description != '') || isRefuse){
			fetch('/api/intelgroups', {
				method: 'post',
				headers: {
					'Content-Type': 'application/json',
					'X-CSRFToken': props.client.transports[0].auth.csrfToken
				},
				credentials: 'same-origin',
				body: JSON.stringify(params)
			}).then(res=>{return res.json()})
			.then(res=>{
				props.intelgroupSave(res);
			})
		}
	};

	return (
		<Container>
			<section className="section app-card">
				<Steps
					enabled={stepsEnabled}
					steps={steps}
					initialStep={initialStep}
					onBeforeExit={()=>{return false;}}
					onBeforeChange={(nextIndex)=>{
						if(nextIndex == 0 || nextIndex == 1){
							return true;
						}
						else if(nextIndex == 2 && name != ''){
							return true;
						}
						else if(nextIndex == 3 && description != ''){
							return true;
						}
						else if(nextIndex == 4){
							return true;
						}
						else if(nextIndex == 5){
							return true;
						}
						else{
							return false;
						}
					}}
					onAfterChange={(nextIndex, newElement)=>{
						if(nextIndex == 5){
							newElement.addEventListener('click', function(){
								setStepsEnabled(false);
								window.location.href="/app/feeds";
							})
						}
					}}
					onExit={()=>{}}
					/>
				<h2 className="subtitle">Create New Intel Group</h2>
				<div id="name"><label className="label">Name</label>
				<TextField
					placeholder="Name of intel group"
					className="column is-three-quarters"
					margin="normal"
					InputLabelProps={{
						shrink: true,
					}}
					variant="outlined"
					value={name}
					onChange={(event) => setName(event.target.value)}
				/><Tooltip title="Name to be displayed in UI" arrow><HelpIcon className="mt-5" style={{color:yellow[900]}} fontSize="large"/></Tooltip></div>
				<div id="description"><label className="label">Description</label>
				<TextField
					placeholder="Description of intel group"
					className="column is-three-quarters"
					margin="normal"
					InputLabelProps={{
						shrink: true,
					}}
					variant="outlined"
					value={description}
					onChange={(event) => setDescription(event.target.value)}
				/><Tooltip title="Description to be displayed in UI" arrow><HelpIcon className="mt-5" style={{color:yellow[900]}} fontSize="large"/></Tooltip></div>
				<div className="mb-4" id="users" style={{zIndex:1}}>
					<label className="label mb-5">Invite Users</label>
					<Grid container>
					<Grid item xs={9} >
						<ReactTags
							ref={reacttag}
							placeholderText="Comma separated list of emails for users to invite"
							tags={tags}
							onDelete={onDelete}
							onAddition={onAddition}
							addOnBlur={true}
							allowNew={props.onboarding?false:true}
							delimiters={['Enter', 'Tab', ',', ' ']}
						/>
					</Grid>
					<Grid item xs={3}>
						<Tooltip title="Users you want to invite" arrow><HelpIcon className="mt-2" style={{color:yellow[900]}} fontSize="large"/></Tooltip>
					</Grid>
					</Grid>
				</div>
				<div id="public"><label className="label">Public</label>
				<TextField
					className="column is-three-quarters"
					select
					margin="normal"
					SelectProps={{
						native: true
					}}
					variant="outlined"
					value={isPublic}
					onChange={(event) => setIsPublic(event.target.value)}
				>
					<option value={false}>False</option>
					<option value={true}>True</option>
				</TextField>
				<Tooltip title="Options to make public or private Intel Group" arrow><HelpIcon className="mt-5" style={{color:yellow[900]}} fontSize="large"/></Tooltip></div>
				<div className="field is-grouped">
					<div className="control">
					<button className="button is-primary" id="button" onClick={() => saveIntelgroup()}>
						<span>Create intel group</span>
					</button>
					</div>
					<div className="control">
						<button className="button is-text" onClick={()=>{setIsRefuse(true); saveIntelgroup();}}>
							<span>Cancel</span>
						</button>
					</div>
				</div>
			</section>
		</Container>
	);
}

const HomePage = (props) =>{
	if(props.mygroups.length == 0 || props.onboarding){
		return <AddIntelgroup users={props.users} client={props.client} intelgroupSave={props.intelgroupSave} onboarding={props.onboarding} />

	}
	else
		return <Welcome mygroups={props.mygroups} currentgroup={props.currentgroup} />
}
export default HomePage;