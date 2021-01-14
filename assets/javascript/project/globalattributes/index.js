import React, { useState, useEffect } from "react";
import { Switch, Route, Link, useHistory } from "react-router-dom";
import { Container, Grid, TextField, Dialog, DialogActions, DialogContent, DialogTitle } from "@material-ui/core";
import Alert from '@material-ui/lab/Alert';
import { Table, Tbody, Thead, Th, Tr, Td } from "react-super-responsive-table";
import AttributeTable from "./attribute-table";

const Loading = () => {
	return (
		<div className='app-card has-text-centered'>
			<div className="lds-ripple"><div></div><div></div></div>
			<p className="heading has-text-primary">Loading...</p>
		</div>
	)
}

const AttributeList = (props) => {
	const [isAdd, setIsAdd] = useState(false);
	const [attribute, setAttribute] = useState('');
	const [value, setValue] = useState('');
	const [words, setWords] = useState('');
    const [isAddAlert, setIsAddAlert] = useState(false);
    const [isEditAlert, setIsEditAlert] = useState(false);
    const [idEdit, setIsEdit] = useState(false);
	const [groupError, setGroupError] = useState(false);
	
	
	const saveAttribute = () => {
        console.log('dfd');
		let params = {
			attribute: attribute.trim(),
			value: value.trim(),
			words_matched: words.trim(),
			enabled: 'Enable',
			currentgroup: props.currentgroup
		}
        if(props.currentgroup == '') setGroupError(true);
        else setGroupError(false);
		if(attribute == '' || value == '' || words == '') setIsAddAlert(true);
		if(attribute != '' && value != '' && words != '' && props.currentgroup != ''){
			setIsAdd(false);
			setAttribute('');
			setValue('');
			setWords('');
			fetch('/api/globalattributes', {
				method: 'post',
				headers: {
					'Content-Type': 'application/json',
					'X-CSRFToken': props.client.transports[0].auth.csrfToken,
				},
				credentials: 'same-origin',
				body: JSON.stringify(params)
			}).then(res=>{return res.json()})
			.then(res=>{
				props.saveAttribute(res);
			})
		}
	}

	const Cancel = () => {
		setIsAdd(false);
		setAttribute('');
		setValue('');
		setWords('');
	}

	const changeStatus = (index) => {
		let params = {
            id: props.globalattributes[index].id,
            attribute: props.globalattributes[index].attribute,
			value: props.globalattributes[index].value,
			words_matched: props.globalattributes[index].words_matched,
			currentgroup: props.globalattributes[index].intelgroup.id,
			enabled: props.globalattributes[index].enabled == 'Enable' ? 'Disable' : 'Enable'
		}
		fetch('/api/globalattributes',{
			method: 'put',
			headers: {
				'Content-Type': 'application/json',
				'X-CSRFToken': props.client.transports[0].auth.csrfToken,
			},
			credentials: 'same-origin',
			body: JSON.stringify(params)
		}).then(res=>{return res.json()})
		.then(res=>{
			props.saveAttribute(res);
		})
    }
    
    const EditAttribute = (index, words, value, attribute, enabled) => {
        let params = {
            id: props.globalattributes[index].id,
            attribute: attribute,
			value: value,
			words_matched: words,
			currentgroup: props.globalattributes[index].intelgroup.id,
			enabled: enabled
		}
		fetch('/api/globalattributes',{
			method: 'put',
			headers: {
				'Content-Type': 'application/json',
				'X-CSRFToken': props.client.transports[0].auth.csrfToken,
			},
			credentials: 'same-origin',
			body: JSON.stringify(params)
		}).then(res=>{return res.json()})
		.then(res=>{
			props.saveAttribute(res);
		})
    }

	return (
		<Container>
			<section className="section">
				<h1 className="title is-3">Manage global attributes</h1>
				<Grid container>
                    <button className="button is-link is-rounded is-medium has-pulled-right" onClick={()=>setIsAdd(true)} >
                        Add attribute
                    </button>
				</Grid>
				{isAddAlert && <Alert severity="warning" onClose={()=>setIsAddAlert(false)}>Please input params exactly!!!</Alert>}
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
								<Td><TextField placeholder="Type" onChange={(event)=>setAttribute(event.target.value)}/></Td>
								<Td><TextField placeholder="Value" onChange={(event)=>setValue(event.target.value)}/></Td>
								<Td><TextField placeholder="Words to match on" onChange={(event)=>setWords(event.target.value)}/></Td>
								<Td><button className="button is-success" onClick={saveAttribute}>Save</button>
									<button className="button is-outlined mx-2" onClick={Cancel}>Cancel</button>
								</Td>
							</Tr>
						}
						{props.globalattributes.map((attribute, index)=>{
							return <AttributeTable index={index} key={attribute.id} attribute={attribute} changeStatus={(index)=>changeStatus(index)} EditAttribute={(index,words, value, attribute, enabled)=>EditAttribute(index, words, value, attribute, enabled)} />
						})}
					</Tbody>
				</Table>
			</section>
		</Container>
	);
}


const GlobalAttributes = (props) => {
	const [globalattributes, setGlobalAttributes] = useState([]);
	const [isLoading, setIsLoading] = useState(true);
	const history = useHistory();

	useEffect(() => {
        let params = {currentgroup:props.currentgroup};
        fetch('/api/globalattributes', {
            method: 'post',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': props.client.transports[0].auth.csrfToken
            },
            credentials: 'same-origin',
            body: JSON.stringify(params)
        }).then(res=>{return res.json()})
        .then(res=>{
            setGlobalAttributes(res.globalattributes);
            setIsLoading(false);
        })
	}, [props.currentgroup]);

	const saveAttribute = (new_attribute) => {
		let flag = false;
		const newGlobalAttrinutes = [];
		for(const attribute of globalattributes){
			if(attribute.id == new_attribute.id){
				newGlobalAttrinutes.push(new_attribute);
				flag = true;
			}
			else{
				newGlobalAttrinutes.push(attribute);
			}
		}
		if(!flag){
			newGlobalAttrinutes.push(new_attribute);
		}
		setGlobalAttributes(newGlobalAttrinutes);
	}

	const GlobalAttributesView = () => {
		if(isLoading){
			return <Loading/>
		}
		else {
            return <AttributeList client={props.client} globalattributes={globalattributes} saveAttribute={saveAttribute} currentgroup={props.currentgroup} />
		}
	}

	return (
		<Switch>
			<Route path="/globalattributes">
				{GlobalAttributesView()}
			</Route>
		</Switch>
	)
}

export default GlobalAttributes;
