import React, { useState, useEffect } from "react";
import { Switch, Route, Link, useHistory } from "react-router-dom";
import { Container, Grid, TextField, Tooltip } from "@material-ui/core";
import { Alert, AlertTitle } from '@material-ui/lab';
import { Table, Tbody, Thead, Th, Tr, Td } from "react-super-responsive-table";
import HelpIcon from '@material-ui/icons/Help';
import { yellow } from '@material-ui/core/colors';

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
			<h1 className="title is-size-3 has-text-centered py-6">No plan! You must select a plan to perform that action. <a className="tag title is-3" onClick={ManagePlan}>Click here to manage your plan</a></h1>
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
	const [isConfrim, setIsConfirm] = useState(false);
	const [isInvitation, setIsInvitation] = useState(false);
	const [groupError, setGroupError] = useState(false);
	
	const saveExtraction = () => {
		let params = {
			attribute: type.trim(),
			value: value.trim(),
			words_matched: words.trim(),
			enabled: 'Enable',
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
				props.saveExtraction(res);
			})
		}
	}

	const cancelExtraction = () => {
		setIsAdd(false);
		setType('');
		setValue('');
		setWords('');
	}

	const changeStatus = (index) => {
		let params = {
			extraction_id: props.extractionlist[index].id,
			enabled: props.extractionlist[index].enabled == 'Enable' ? 'Disable' : 'Enable'
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

	return (
		<Container>
			<section className="section" >
				{isConfrim && <Alert severity="info" onClose={()=>setIsConfirm(false)}>Please confirm your email. Click here to resend confirmation link.</Alert>}
				{isInvitation && <Alert severity="info" onClose={()=>setIsInvitation(false)}>You have an invitation to Intel Group XXX pending. <Link className="has-text-danger" to="#">Click here to accept.</Link></Alert>}
			</section>
			<section className="section">
				{props.isMessage&&
				<Alert severity="info" className="my-5">
					<AlertTitle className="subtitle is-4 has-text-weight-bold">Info</AlertTitle>
					<span className="subtitle is-5">{props.message}</span>
				</Alert>}
				<h1 className="title is-3">Manage Observable extractions</h1>
				<Grid container>
					<Grid item xs={9}>
						<label className="title is-5">Custom extractions</label>
					</Grid>
					<Grid item xs={3}>
						{props.customobservable&&<button className="button is-link is-rounded is-medium has-pulled-right" onClick={()=>setIsAdd(true)} >
							Add extraction
						</button>}
					</Grid>
				</Grid>
				{isAlert && <Alert severity="warning" onClose={()=>setIsAlert(false)}>Please input params exactly!!!</Alert>}
				{groupError && <Alert severity="warning" onClose={()=>setGroupError(false)}>Please select Intel Group.</Alert>}
				<Table className="table is-striped is-fullwidth has-vcentered-cells">
					<Thead>
						<Tr>
							<Th>Observable Type</Th>
							<Th>Observable Value</Th>
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
							return <Tr index={index} key={extraction.id}>
								<Td>{extraction.attribute+'('+extraction.api_attribute+')'}</Td>
								<Td>{extraction.value+'('+extraction.api_value+')'}</Td>
								<Td>{extraction.words_matched}</Td>
								<Td><a className="button is-text" onClick={()=>changeStatus(index)}>{extraction.enabled}</a></Td>
							</Tr>
						})}
					</Tbody>
				</Table>
			</section>
			<section className="section">
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
								<Td>{attribute.attribute+'('+attribute.api_attribute+')'}</Td>
								<Td>{attribute.value+'('+attribute.api_value+')'}</Td>
								<Td>{attribute.words_matched}</Td>
								<Td><a className="button is-text" onClick={()=>{}}>{attribute.enabled}</a></Td>
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
	const [currentrole, setCurrentRole] = useState({});
	const [isMessage, setIsMessage] = useState(false);
	const [message, setMessage] = useState('');
	const [isPlan, setIsPlan] = useState(true);
	const [customobservable, setCustomObservable] = useState(true);
	const history = useHistory();

	useEffect(() => {
		if(props.currentgroup == '') history.push('/');
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
				if(Boolean(res.isPlan)){
					setIsPlan(true);
					setIsMessage(res.message);
					setMessage(res.content);
					setExtractionList(res.attributes);
					setGlobalAttributes(res.globalattributes);
					setCurrentRole(res.currentrole);
					setCustomObservable(res.customobservable)
				}
				else setIsPlan(false);
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

	const ExtractionListView = () => {
		if(isLoading){
			return <Loading/>
		}
		else {
			if(isPlan){
				if(currentrole.role ==0)
					return (
						<div className='app-card has-text-centered'>
							<div className="lds-ripple"><div></div><div></div></div>
							<p className="subtitle is-3">! You have an invitation to <span className="title is-3 has-text-primary">{currentrole.intelgroup.name}</span> pending. <Link className="muted-link subtitle is-3 has-text-danger" to="/intelgroups" >Click here to accept.</Link></p>
						</div>
					)
				if(currentrole.role == 1)
					return(
						<div className='section has-text-centered'>
							<p className="subtitle is-3">! You are now a member of <span className="title is-3 has-text-primary">{currentrole.intelgroup.name}</span>.</p>
						</div>
					)
				if(currentrole.role ==2)
					return <ExtractionList client={props.client} extractionlist={extractionlist} saveExtraction={saveExtraction} customobservable={customobservable}
						currentgroup={props.currentgroup} globalattributes={globalattributes} isMessage={isMessage} message={message} />
			}
			else{
				return <Plan currentgroup={props.currentgroup} currentrole={currentrole} />
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
