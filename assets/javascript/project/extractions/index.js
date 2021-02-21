import React, { useState, useEffect } from "react";
import { Switch, Route, Link, useHistory } from "react-router-dom";
import { 
	Container, Grid, TextField, Tooltip
} from "@material-ui/core";
import { Alert, AlertTitle } from '@material-ui/lab';
import { Table, Tbody, Thead, Th, Tr, Td } from "react-super-responsive-table";
import HelpIcon from '@material-ui/icons/Help';
import { yellow } from '@material-ui/core/colors';
import ExtractionTable from "./extraction-table";
import { Steps } from 'intro.js-react';

const Loading = () => {
	return (
		<div className='app-card has-text-centered'>
			<div className="lds-ripple"><div></div><div></div></div>
			<p className="heading has-text-primary">Loading...</p>
		</div>
	)
}


const Plan = (props) => {
	const [isAlert, setIsAlert] = useState(false);

	const ManagePlan = () => {
		if(props.currentrole.role == 2) location.href=`/subscriptions/intelgroup/${props.currentgroup}`;
		else setIsAlert(true);
	}

	return <div className="my-6">
			<h1 className="title is-size-3 has-text-centered py-6">You must upgrade a plan to perform that action. <a className="tag title is-3" onClick={ManagePlan}>Click here to manage your plan</a></h1>
			{isAlert&& <Grid container direction="row" justify="center" alignItems="center">
				<Grid item xs={6}>
					<Alert className="has-text-centered title is-size-4" severity="error" onClose={()=>setIsAlert(false)}>! Please contact the feed group administrator to manage intel group plan payment to reinstate access.</Alert>
				</Grid>
			</Grid>}
		</div>
}

const ExtractionList = (props) => {
	const [isAdd, setIsAdd] = useState(false);
	const [type, setType] = useState('');
	const [value, setValue] = useState('');
	const [words, setWords] = useState('');
	const [isAlert, setIsAlert] = useState(false);
	const [groupError, setGroupError] = useState(false);
	const [bannerCustom, setBannerCustom] = useState(false);
	const [bannerAdd, setBannerAdd] = useState(false);
	const [stepsEnabled, setStepsEnabled] = useState(true);
	const steps = [{
		element: '#attribute',
		intro: 'Custom attributes  by matching text in each Intel Report'
	},{
		element: '#globalattribute',
		intro: 'Global attributes  by matching text in each Intel Report'
	}]
	
	const saveExtraction = () => {

		if(props.customobservable){
			let params = {
				attribute: type.trim(),
				value: value.trim(),
				words_matched: words.trim(),
				isenable: true,
				currentgroup: props.currentgroup
			}
			if(props.currentgroup == '') setGroupError(true);
			if(type == '' || value == '' || words == '') setIsAlert(true);
			if(type != '' && value != '' && words != '' && props.currentgroup != ''){
				setIsAdd(false);
				setType('');
				setValue('');
				setWords('');
				fetch('/api/attributes', {
					method: 'post',
					headers: {
						'Content-Type': 'application/json',
						'X-CSRFToken': props.client.transports[0].auth.csrfToken,
					},
					credentials: 'same-origin',
					body: JSON.stringify(params)
				}).then(res=>{return res.json()})
				.then(res=>{
					if(Boolean(res.message)){
						setBannerAdd(true);
					}
					else{
						props.saveExtraction(res);
					}
				})
			}
		}
		if(props.isAutoDown || !props.customobservable){
			setBannerCustom(true);
		}
	}

	const cancelExtraction = () => {
		setIsAdd(false);
		setType('');
		setValue('');
		setWords('');
	}

	const changeStatus = (index) => {
		if(props.customobservable){
			let params = {
				id: props.extractionlist[index].id,
				attribute: props.extractionlist[index].attribute,
				value: props.extractionlist[index].value,
				words_matched: props.extractionlist[index].words_matched,
				currentgroup: props.extractionlist[index].intelgroup.id,
				isenable: props.extractionlist[index].isenable?false:true
			}
			fetch('/api/attributes',{
				method: 'put',
				headers: {
					'Content-Type': 'application/json',
					'X-CSRFToken': props.client.transports[0].auth.csrfToken,
				},
				credentials: 'same-origin',
				body: JSON.stringify(params)
			}).then(res=>{return res.json()})
			.then(res=>{
				console.log(res);
				props.saveExtraction(res);
			})
		}
		if(props.isAutoDown || !props.customobservable){
			setBannerCustom(true);
		}
	}

	const editAttribute = (index, words, value, type, isenable) => {
		if(props.customobservable){
			let params = {
				id: props.extractionlist[index].id,
				attribute: type.trim(),
				value: value.trim(),
				words_matched: words.trim(),
				currentgroup: props.extractionlist[index].intelgroup.id,
				isenable: isenable=='Enable'?true:false
			}
			fetch('/api/attributes',{
				method: 'put',
				headers: {
					'Content-Type': 'application/json',
					'X-CSRFToken': props.client.transports[0].auth.csrfToken,
				},
				credentials: 'same-origin',
				body: JSON.stringify(params)
			}).then(res=>{return res.json()})
			.then(res=>{
				props.saveExtraction(res);
			})
		}
		if(props.isAutoDown || !props.customobservable){
			setBannerCustom(true);
		}
	}
	
	const enableGlobal = (index) => {
		if(props.customobservable){
			let params = {id:props.globalattributes[index].id, isenable:props.globalattributes[index].isenable?false:true}
			fetch('/api/enableglobal', {
				method: 'post',
				headers: {
					'Content-Type': 'application/json',
					'X-CSRFToken': props.client.transports[0].auth.csrfToken
				},
				credentials: 'same-origin',
				body: JSON.stringify(params)
			}).then(res=>{return res.json()})
			.then(res=>{
				props.saveGlobal(res)
			})
		}
		if(props.isAutoDown || !props.customobservable){
			setBannerCustom(true);
		}
	}

	return (
		<Container>
			{props.mygroups.length == 0 &&
			<Steps
				enabled={stepsEnabled}
				steps={steps}
				initialStep={0}
				onStart={()=>setIsAdd(true)}
				onExit={(index)=>{
					setStepsEnabled(false);
					if(index==1)
						window.location.href="/home/whitelist";
				}}
				options={{
					doneLabel: 'Next'
				}}
			/>}
			<section className="section" id="attribute">
				{props.isInit&&
				<Alert severity="info" className="my-5">
					<AlertTitle className="subtitle is-4 has-text-weight-bold">Info</AlertTitle>
					<span className="subtitle is-5">{props.message}</span>
				</Alert>}
				{bannerCustom && <Alert severity="error" className="title is-size-4" onClose={()=>setBannerCustom(false)}>Sorry, your plan does not currently cover custom attribute abstractions. You can upgrade now to enable this feature here.</Alert>}
				{bannerAdd && <Alert severity="error" className="title is-size-4" onClose={()=>setBannerAdd(false)}>The attribute already exists! Please find out it and edit.</Alert>}
				<h1 className="title is-3">Manage Observable extractions</h1>
				<Grid container>
					<Grid item xs={9}>
						<label className="title is-5">Custom extractions</label>
					</Grid>
					<Grid item xs={3}>
						<button className="button is-link is-rounded is-medium has-pulled-right" onClick={()=>setIsAdd(true)} >
							Add extraction
						</button>
					</Grid>
				</Grid>
				{isAlert && <Alert severity="warning" className="title is-size-4" onClose={()=>setIsAlert(false)}>Please input params exactly!!!</Alert>}
				{groupError && <Alert severity="warning" className="title is-size-4" onClose={()=>setGroupError(false)}>Please select Intel Group.</Alert>}
				<Table className="table is-striped is-fullwidth has-vcentered-cells">
					<Thead>
						<Tr>
							<Th>Observable Type(API)</Th>
							<Th>Observable Value(API)</Th>
							<Th>Words to match on</Th>
							<Th>Actions</Th>
						</Tr>
					</Thead>
					<Tbody>
						{isAdd && <Tr>
								<Td><TextField placeholder="Type" onChange={(event)=>setType(event.target.value)}/></Td>
								<Td><TextField placeholder="Value" onChange={(event)=>setValue(event.target.value)}/></Td>
								<Td><TextField placeholder="Words to match on" onChange={(event)=>setWords(event.target.value)}/></Td>
								<Td><button className="button is-outlined mx-2" onClick={saveExtraction}>Save</button>
									<button className="button is-outlined" onClick={cancelExtraction}>Cancel</button>
								</Td>
							</Tr>
						}
						{props.extractionlist.map((extraction, index)=>{
							return <ExtractionTable index={index} key={extraction.id} extraction={extraction} 
								changeStatus={(index)=>changeStatus(index)} editAttribute={(index, words, value, type, isenable)=>editAttribute(index, words, value, type, isenable)} />
						})}
					</Tbody>
				</Table>
			</section>
			<section className="section"  id="globalattribute">
				<label className="title is-5">Global extractions</label>
				<Table className="table is-striped is-fullwidth has-vcentered-cells">
					<Thead>
						<Tr>
							<Th>Observable Type<Tooltip title="Observable Type" arrow><HelpIcon  style={{color:yellow[900]}} fontSize="default"/></Tooltip></Th>
							<Th>Observable Value<Tooltip title="Observable Value" arrow><HelpIcon  style={{color:yellow[900]}} fontSize="default"/></Tooltip></Th>
							<Th>Words to match on<Tooltip title="Words to match on" arrow><HelpIcon  style={{color:yellow[900]}} fontSize="default"/></Tooltip></Th>
							<Th>Actions</Th>
						</Tr>
					</Thead>
					<Tbody>
						{props.globalattributes.map((attribute, index)=>{
							return <Tr index={index} key={attribute.id}>
								<Td>{attribute.globalattribute.attribute+'('+attribute.globalattribute.api_attribute+')'}</Td>
								<Td>{attribute.globalattribute.value+'('+attribute.globalattribute.api_value+')'}</Td>
								<Td>{attribute.globalattribute.words_matched}</Td>
								<Td><a className={attribute.isenable?"button is-text":"button is-success"} onClick={()=>{enableGlobal(index)}}>{attribute.isenable?"Disable":"Enable"}</a></Td>
							</Tr>
						})}
					</Tbody>
				</Table>
			</section>
		</Container>
	);
}


const Extractions = (props) => {
	const [extractionlist, setExtractionList] = useState([]);
	const [globalattributes, setGlobalAttributes] = useState([]);
	const [isLoading, setIsLoading] = useState(true);
	const [customobservable, setCustomObservable] = useState(true);
	const history = useHistory();

	useEffect(() => {
		if(props.currentgroup == '' && props.mygroups.length != 0) history.push('/');
		else{
			let params = {currentgroup:props.currentgroup};
			fetch('/api/attributes', {
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
				setExtractionList(res.attributes);
				setGlobalAttributes(res.globalattributes);
				setCustomObservable(res.customobservable)
				setIsLoading(false);
			})
		}
	}, [props.currentgroup]);

	const saveExtraction = (new_extraction) => {
		let flag = false;
		const newExtractions = [];
		for(const extraction of extractionlist){
			if(extraction.id == new_extraction.id){
				newExtractions.push(new_extraction);
				flag = true;
			}
			else{
				newExtractions.push(extraction);
			}
		}
		if(!flag){
			newExtractions.push(new_extraction);
		}
		setExtractionList(newExtractions);
	}

	const saveGlobal = (new_global) => {
		let flag = false;
		const newGlobals = [];
		for(const global of globalattributes){
			if(global.id == new_global.id){
				newGlobals.push(new_global);
				flag = true;
			}
			else{
				newGlobals.push(global);
			}
		}
		if(!flag){
			newGlobals.push(new_global);
		}
		setGlobalAttributes(newGlobals);
	}

	const ExtractionListView = () => {
		if(isLoading){
			return <Loading/>
		}
		else {
			if(props.currentrole.role ==0)
				return (
					<div className='app-card has-text-centered'>
						<div className="lds-ripple"><div></div><div></div></div>
						<p className="subtitle is-3">! You have an invitation to <span className="title is-3 has-text-primary">{props.currentrole.intelgroup.name}</span> pending. <Link className="muted-link subtitle is-3 has-text-danger" to="/account" >Click here to accept.</Link></p>
					</div>
				)
			if(props.currentrole.role == 1)
				return(
					<div className='section has-text-centered'>
						<p className="subtitle is-3">! You are now a member of <span className="title is-3 has-text-primary">{props.currentrole.intelgroup.name}</span>.</p>
					</div>
				)
			if(props.currentrole.role ==2 || props.mygroups.length == 0){
				if(props.isPlan)
					return <ExtractionList client={props.client} extractionlist={extractionlist} saveExtraction={saveExtraction} customobservable={customobservable} saveGlobal={saveGlobal} mygroups={props.mygroups}
								currentgroup={props.currentgroup} globalattributes={globalattributes} isInit={props.isInit} message={props.message} isAutoDown={props.isAutoDown} />
				else return <Plan currentgroup={props.currentgroup} currentrole={props.currentrole} />
			}
		}
	}

	return (
		<Switch>
			<Route path="/extractions">
				{ExtractionListView()}
			</Route>
		</Switch>
	)
}

export default Extractions;
