import React, { useState, useEffect } from "react";
import { Switch, Route, useHistory, Link } from "react-router-dom";
import { TextField } from "@material-ui/core";
import { Table, Thead, Tbody, Tr, Th, Td } from "react-super-responsive-table";
import Alert from '@material-ui/lab/Alert';

import IndicatorTable from "./indicator-table";
import { getAction } from "../../api";
import { API_ROOT } from "../const";

const Loading = () => {
	return (
		<div className='app-card has-text-centered'>
			<div className="lds-ripple"><div></div><div></div></div>
			<p className="heading has-text-primary">Loading...</p>
		</div>
	);
}

const IndicatorList = (props) => {
    const [isAdd, setIsAdd] = useState(false);
    const [type, setType] = useState('');
    const [typeApi, setTypeApi] = useState('');
    const [value, setValue] = useState('');
    const [valueApi, setValueApi] = useState('');
    const [isAlert, setIsAlert] = useState(false);

    const saveIndicator = () => {
        let params ={
            type: type.trim(),
            type_api: typeApi.trim(),
            value: value.trim(),
            value_api: valueApi.trim(),
            enabled: 'Enable'
        }
        const action = getAction(API_ROOT, ['globalindicators', 'create']);
        if(type.trim() != '' && typeApi.trim() != '' && value.trim() != '' && valueApi.trim() != '')
            props.client.action(window.schema, action, params).then((result)=>{
                props.saveIndicator(result);
                setIsAdd(false);
                setType('');
                setValue('');
                setTypeApi('');
                setValueApi('');
            });
        else setIsAlert(true);
    }

    const Enable = (index) =>{
        let params;
        if(props.indicators[index].enabled === 'Enable')
            params = {id:props.indicators[index].id, enabled: 'Disable'};
        else if(props.indicators[index].enabled === 'Disable')
            params = {id:props.indicators[index].id, enabled: 'Enable'};
        const action = getAction(API_ROOT, ['globalindicators', 'partial_update']);
        props.client.action(window.schema, action, params).then((result)=>{
            props.saveIndicator(result);
        })
    }

    return (
        <section className="section">
            <h1 className="title is-3">All Indicators</h1>
            <div className="section">
                <button className="button is-link is-large" onClick={()=>setIsAdd(true)} >
                    <span>Add Indicator</span>
                </button>
            </div>
            {isAlert && <Alert severity="error" onClose={()=>setIsAlert(false)}>Please input exactly!!!</Alert>}
            <Table className="table is-striped is-fullwidth has-vcentered-cells">
                <Thead>
                    <Tr>
                        <Th>Type</Th>
                        <Th>Type API</Th>
                        <Th>Value</Th>
                        <Th>Value API</Th>
                        <Th>Action</Th>
                    </Tr>
                </Thead>
                <Tbody>
                    {isAdd && <Tr>
                            <Td><TextField placeholder="Type" value={type} onChange={(event)=>setType(event.target.value)}/></Td>
                            <Td><TextField placeholder="Type API" value={typeApi} onChange={(event)=>setTypeApi(event.target.value)}/></Td>
                            <Td><TextField placeholder="Value" value={value} onChange={(event)=>setValue(event.target.value)}/></Td>
                            <Td><TextField placeholder="Value API" value={valueApi} onChange={(event)=>setValueApi(event.target.value)}/></Td>
                            <Td><button className="button is-outlined" onClick={saveIndicator}>Save</button>
                                <button className="button is-outlined" onClick={()=>setIsAdd(false)}>Cancel</button>
                            </Td>
                        </Tr>
                    }
                    {
                        props.indicators.map((indicator, index) => {
                            return <IndicatorTable index={index} key={indicator.id} indicator={indicator} Enable={(index) => Enable(index)} />
                        })
                    }
                </Tbody>
            </Table>
        </section>
	);

}

const GlobalIndicators = (props) => {
    const [isLoading, setIsLoading] = useState(true);
    const [indicators, setIndicators] = useState([]);
    const [currentrole, setCurrentRole] = useState({});
    const history = useHistory();

    useEffect(() => {
        if(props.currentgroup == '') history.push('/');
		else{
			let params = {currentgroup:props.currentgroup};
			fetch('/api/globalindicators', {
				method: 'post',
				headers: {
					'Content-Type': 'application/json',
					'X-CSRFToken': props.client.transports[0].auth.csrfToken
				},
				credentials: 'same-origin',
				body: JSON.stringify(params)
			}).then(res=>{return res.json()})
			.then(res=>{
				setIndicators(res.globalindicators);
				setCurrentRole(res.currentrole);
				setIsLoading(false);
			})
		}
    },[props.currentgroup]);

    const saveIndicator = (newIndicator) =>{
        let flag = false;
        const newIndicators = [];
        for(const indicator of indicators){
            if(indicator.id === newIndicator.id){
                newIndicators.push(newIndicator);
                flag = true;
            }
            else newIndicators.push(indicator);
        }
        if(!flag)
            newIndicators.push(newIndicator);
        setIndicators(newIndicators);
    }

    const IndicatorListView = () => {
        if(isLoading)
            return <Loading/>
        else{
            if(currentrole.role ==0)
				return (
					<div className='app-card has-text-centered'>
						<div className="lds-ripple"><div></div><div></div></div>
						<p className="subtitle is-3">! You have an invitation to {currentrole.intelgroup.name} pending. <Link className="muted-link subtitle is-3" to="/intelgroups" >Click here to accept.</Link></p>
					</div>
				)
			if(currentrole.role == 1)
				return(
					<div className='section has-text-centered'>
						<p className="subtitle is-3">! You are now a member of {currentrole.intelgroup.name}.</p>
					</div>
				)
			if(currentrole.role ==2)
                return <IndicatorList client={props.client} indicators={indicators} saveIndicator={saveIndicator} />
        }
    }

    return(
        <Switch>
            <Route path="/globalindicators">
                {IndicatorListView()}
            </Route>
        </Switch>
    );
}

export default GlobalIndicators