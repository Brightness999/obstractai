import React, { useState, useEffect } from 'react';
import { Link, useHistory } from "react-router-dom";
import ReactTags from 'react-tag-autocomplete';
import { Tooltip, TextField, Grid, Paper } from "@material-ui/core";
import HelpIcon from '@material-ui/icons/Help';
import { yellow } from '@material-ui/core/colors';


const Welcome = (props) => {
	return (
		<div className="my-6">
			<h1 className="title is-size-2 has-text-centered py-6">Welcome to Cyobstract</h1>
			{props.mygroups.map(mygroup=>{
				if(mygroup.role == 0)
					return <div className="section app-card has-text-centered" key={mygroup.id}>
						<p className="subtitle is-4">! You have an invitation to <span className="title is-3 has-text-primary">{mygroup.intelgroup.name}</span> pending. <Link className="muted-link subtitle is-4 has-text-danger" to="/account" >Click here to accept.</Link></p>
					</div> 
			})}
			{/* <div><pre>{JSON.stringify(props.re, null, 2) }</pre></div> */}
		</div>
	);
}

const AddIntelgroup = (props) => {

	const [name, setName] = useState('');
  	const [description, setDescription] = useState('');
	const [isRefuse, setIsRefuse] = useState(false);
	const [tags, setTags] = useState([]);
	const history = useHistory();

	const userOptions = props.users.map((user)=>({
		id: user.id,
		name: user.email
	}));

	const reacttag= React.createRef();
	const onDelete= (i)=> {
		var temp = tags.slice(0)
		temp.splice(i, 1)
		setTags(temp)
	}
	  
	const onAddition = (tag)=> {
		let mailformat = /^([A-Za-z0-9_\-\.])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$/;
		if(tag.name.match(mailformat)){
			var temp = [].concat(tags, tag)
			setTags(temp)
		}
	}

	const saveIntelgroup = function() {
		const userids = [];
		const emails = [];
		tags.forEach(tag => {
			if(Boolean(tag.id)) {
				userids.push(tag.id)
			}
			else {
				emails.push(tag.name)
			}
		});
		let params = {
		  name: name,
		  description: description,
		  userids: userids,
		  emails: emails
		};
		if((name != '' && description != '' && (userids != [] || emails != [])) || isRefuse){
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
				history.push('/intelgroup')
			})
		}
	};

	return (
		<section className="section app-card">
			<h2 className="subtitle">Intel Group Details</h2>
			<label className="label">Name</label>
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
			/><Tooltip title="Name to be displayed in UI" arrow><HelpIcon className="mt-5" style={{color:yellow[900]}} fontSize="large"/></Tooltip>
			<label className="label">Description</label>
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
			/><Tooltip title="Description to be displayed in UI" arrow><HelpIcon className="mt-5" style={{color:yellow[900]}} fontSize="large"/></Tooltip>
			<div className="mb-4" style={{zIndex:1}}>
				<label className="label mb-5">Invite Users</label>
				<Grid container>
				<Grid item xs={9}>
					<ReactTags
					ref={reacttag}
					placeholderText="Comma separated list of emails for users to invite"
					tags={tags}
					suggestions={userOptions}
					onDelete={onDelete}
					onAddition={onAddition}
					allowNew={true}
					delimiters={['Enter', 'Tab', ',', ' ']}
					/>
				</Grid>
				<Grid item xs={3}>
					<Tooltip title="Users you want to invite" arrow><HelpIcon className="mt-2" style={{color:yellow[900]}} fontSize="large"/></Tooltip>
				</Grid>
				</Grid>
			</div>
			<div className="field is-grouped">
				<div className="control">
				<button type='button' className="button is-primary" onClick={() => saveIntelgroup()}>
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
	);
}

const HomePage = (props) =>{
	if(props.mygroups.length == 0)
		return <AddIntelgroup users={props.users} client={props.client} intelgroupSave={props.intelgroupSave} />
	else
		return <Welcome mygroups={props.mygroups} re={props.re} />
}
export default HomePage;