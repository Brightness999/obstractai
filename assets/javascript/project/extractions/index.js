import React, { useState, useEffect } from "react";
import { Switch, Route, Link } from "react-router-dom";
import { Container, Grid, TextField, Tooltip } from "@material-ui/core";
import Alert from '@material-ui/lab/Alert';
import { Table, Tbody, Thead, Th, Tr, Td } from "react-super-responsive-table";
import { Dropdown } from "semantic-ui-react";

import { getAction } from "../../api";
import { API_ROOT } from "../const";
import Styles from "../styles";

const Loading = () => {
	return (
		<div className='app-card has-text-centered'>
			<div className="lds-ripple"><div></div><div></div></div>
			<p className="heading has-text-primary">Loading...</p>
		</div>
	)
}

const ExtractionList = (props) => {
	console.log(props);
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
			types: type,
			value: value,
			words_matched: words,
			enabled: 'Enable',
			currentgroup: props.currentgroup
		}
		const action = getAction(API_ROOT, ['extractions', 'create']);
		if(props.currentgroup == '') setGroupError(true);
		if(type == '' || value == '' || words == '') setIsAlert(true);
		if(type != '' && value != '' && words != '' && props.currentgroup != ''){
			setIsAdd(false);
			setType('');
			setValue('');
			setWords('');
			fetch('/api/extractions', {
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
		console.log(index);
		let params = {
			extraction_id: props.extractionlist[index].id,
			enabled: props.extractionlist[index].enabled == 'Enable' ? 'Disable' : 'Enable'
		}
		fetch('/api/extractions',{
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
			<section className="section" style={Styles.SectionStyle}>
				{isConfrim && <Alert severity="info" onClose={()=>setIsConfirm(false)}>Please confirm your email. Click here to resend confirmation link.</Alert>}
				{isInvitation && <Alert severity="info" onClose={()=>setIsInvitation(false)}>You have an invitation to Intel Group XXX pending. <Link to="#" style={Styles.LinkStyle}>Click here to accept.</Link></Alert>}
			</section>
			<section className="section" style={Styles.SectionStyle}>
				<h1 className="title is-3">Manage Observable extractions</h1>
				<Grid container>
					<Grid item xs={9}>
						<label className="title is-5">Custom extractions</label>
					</Grid>
					<Grid item xs={3}>
						<button className="button is-outlined" onClick={()=>setIsAdd(true)} style={Styles.ExtractionAddButton}>
							Add extraction
						</button>
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
							<Th></Th>
						</Tr>
					</Thead>
					<Tbody>
						{isAdd && <Tr>
								<Td><TextField placeholder="Type" onChange={(event)=>setType(event.target.value)}/></Td>
								<Td><TextField placeholder="Value" onChange={(event)=>setValue(event.target.value)}/></Td>
								<Td><TextField placeholder="Words to match on" onChange={(event)=>setWords(event.target.value)}/></Td>
								<Td><button className="button is-outlined" onClick={saveExtraction}>Save</button>
									<button className="button is-outlined" onClick={cancelExtraction}>Cancel</button>
								</Td>
							</Tr>
						}
						{props.extractionlist.map((extraction, index)=>{
							return <Tr index={index} key={extraction.id}>
								<Td>{extraction.types}</Td>
								<Td>{extraction.value}</Td>
								<Td>{extraction.words_matched}</Td>
								<Td><a className="button is-text" onClick={()=>changeStatus(index)}>{extraction.enabled}</a></Td>
							</Tr>
						})}
					</Tbody>
				</Table>
			</section>
			<section className="section" style={Styles.SectionStyle}>
				<label className="title is-5">Global extractions</label>
				<Table className="table is-striped is-fullwidth has-vcentered-cells">
					<Thead>
						<Tr>
							<Th>Observable Types<Tooltip title="Observable type" arrow ><button className="button is-outlined" style={Styles.HelpButton}>?</button></Tooltip></Th>
							<Th>Observable Value<button className="button is-outlined" style={Styles.HelpButton}>?</button></Th>
							<Th>Words to match on<button className="button is-outlined" style={Styles.HelpButton}>?</button></Th>
							<Th></Th>
						</Tr>
					</Thead>
					<Tbody>
						<Tr>
							<Td>Threat type (threat_type)</Td>
							<Td>Malware (malware)</Td>
							<Td>malware</Td>
							<Td><Link to="#">Disable</Link></Td>
						</Tr>
						<Tr>
							<Td>Country (country)</Td>
							<Td>United Kingdom (united_kingdom)</Td>
							<Td>United Kingdom, UK</Td>
							<Td><Link to="#">Disable</Link></Td>
						</Tr>
					</Tbody>
				</Table>
			</section>
		</Container>
	);
}


const Extractions = (props) => {
	const [extractionlist, setExtractionList] = useState([]);
	const [isLoading, setIsLoading] = useState(true);

	useEffect(() => {
		const extraction_action = getAction(API_ROOT, ['extractions', 'list']);
		props.client.action(window.schema, extraction_action).then((result) => {
			setExtractionList(result.results);
			setIsLoading(false);
		});
	}, []);

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
		} else {
			return <ExtractionList client={props.client} extractionlist={extractionlist} saveExtraction={saveExtraction} currentgroup={props.currentgroup} />
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
