import React, { useState, useEffect } from 'react';
import { Link, useHistory } from "react-router-dom";
import { Dropdown } from "semantic-ui-react";
import ReactTags from 'react-tag-autocomplete';

import { getAction } from "../api";
import { API_ROOT } from "./const";

const Welcome = (props) => {
	return (
		<div style={{paddingTop:100+'px'}}>
			<h1 className="title is-size-2 has-text-centered">Welcome to Cyobstract</h1>
			{props.mygroups.map(mygroup=>{
				if(mygroup.role == 0)
					return <div className="section app-card has-text-centered" key={mygroup.id}>
						<p className="subtitle is-4">! You have an invitation to <span className="title is-3 has-text-primary">{mygroup.intelgroup.name}</span> pending. <Link className="muted-link subtitle is-4 has-text-danger" to="/intelgroups" >Click here to accept.</Link></p>
					</div> 
			})}
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
		var temp = [].concat(tags, tag)
		setTags(temp)
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
		const action = getAction(API_ROOT, ["intelgroup", "newgroup"]);
		if((name != '' && description != '' && userids != []) || isRefuse){
		  props.client.action(window.schema, action, params).then((result) => {
			props.intelgroupSave(result);
			history.push('/intelgroups');
		  })
		}
	};

	return (
		<section className="section app-card">
			<h2 className="subtitle">Intel Group Details</h2>
			<div className="field">
				<label className="label">Name</label>
				<div className="control">
				<input className="input" type="text" placeholder="Name"
						onChange={(event) => setName(event.target.value)} value={name} required={true}>
				</input>
				</div>
			</div>
			<div className="field">
				<div className="control">
				<label className="label">Description</label>
				<input className="input" type="text" placeholder="Description"
						onChange={(event) => setDescription(event.target.value)} value={description} required={true}>
				</input>
				</div>
			</div>
			<div className="field">
				<div className="control">
				<label className="label">Invite Users</label>
				<ReactTags
					ref={reacttag}
					tags={tags}
					suggestions={userOptions}
					onDelete={onDelete}
					onAddition={onAddition}
					allowNew={true}
				/>
				</div>
			</div>
			<div className="field is-grouped">
				<div className="control">
				<button type='button' className="button is-primary" onClick={() => saveIntelgroup()}>
					<span>Create intel group</span>
				</button>
				</div>
				<div className="control">
					<button className="button is-text" onClick={()=>{setIsRefuse(true); saveIntelgroup()}}>
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
		return <Welcome mygroups={props.mygroups} />
}
export default HomePage;