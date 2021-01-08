import React, { useState, useEffect } from "react";
import { Switch, Route, Link, useHistory } from "react-router-dom";
import { Container, TextField, Grid } from "@material-ui/core";
import { Table, Thead, Tbody, Tr, Th, Td } from "react-super-responsive-table";

import ListTable from "./list-table";
import AddWhitelist from "./add-whitelist";
import { getAction } from "../../api";
import { API_ROOT } from "../const";
import Styles from "../styles";
import IndicatorTable from "./indicator-table";


const Loading = () => {
	return (
		<div className='app-card has-text-centered'>
			<div className="lds-ripple"><div></div><div></div></div>
			<p className="heading has-text-primary">Loading...</p>
		</div>
	);
}

const WhiteList = (props) => {
    const ListEnable = (index) =>{
        let params;
        if(props.whitelist[index].enabled === 'Enable')
            params = {id:props.whitelist[index].id, enabled: 'Disable'};
        else if(props.whitelist[index].enabled === 'Disable')
            params = {id:props.whitelist[index].id, enabled: 'Enable'};
        const action = getAction(API_ROOT, ['whitelist', 'partial_update']);
        props.client.action(window.schema, action, params).then((result)=>{
            props.saveWhitelist(result);
        })
    }

    const IndicatorEnable = (index) => {
        let params;
        if(props.indicators[index].enabled === 'Enable')
            params = {id:props.indicators[index].id, enabled: 'Disable'};
        else if(props.indicators[index].enabled === 'Disable')
            params = {id:props.indicators[index].id, enabled: 'Enable'};
        fetch('/api/indicators', {
            method: 'post',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': props.client.transports[0].auth.csrfToken
            },
            credentials: 'same-origin',
            body: JSON.stringify(params)
        }).then(res=>{return res.json()})
        .then(res=> {
            props.saveIndicator(res);
        })
    }

    return (
		<Container>
			<section className="section">
                <h1 className="title is-3">Manage Indicator visibility</h1>
                <h1 className="title is-5">Manage by type</h1>
                <Table className="table is-striped is-fullwidth has-vcentered-cells">
                    <Thead>
                        <Tr>
                            <Th>Type</Th>
                            <Th>Value</Th>
                            <Th>Enabled</Th>
                        </Tr>
                    </Thead>
                    <Tbody>
                        {props.indicators.map((indicator, index)=>{
                            return <IndicatorTable index={index} key={indicator.id} indicator={indicator} IndicatorEnable={(index)=>IndicatorEnable(index)} />
                        })}
                    </Tbody>
                </Table>
            </section>
            <section className="section">
                <span className="title is-5">Manage by whitelist</span>
                <Link to="/whitelist/new">
                    <button className="button is-info is-pulled-right"  >
                        <span>Add whitelist</span>
                    </button>

                </Link>
				<Table className="table is-striped is-fullwidth has-vcentered-cells">
					<Thead>
						<Tr>
							<Th>Type</Th>
							<Th>Value</Th>
                            <Th>Value to whitelist</Th>
							<Th>Enabled</Th>
						</Tr>
					</Thead>
					<Tbody>
						{
							props.whitelist.map((list, index) => {
								return <ListTable index={index} key={list.id} list={list} ListEnable={(index) => ListEnable(index)} />
							})
						}
					</Tbody>
				</Table>
			</section>
		</Container>
	);

}

const WhiteLists = (props) => {
    const [isLoading, setIsLoading] = useState(true);
    const [whitelist, setWhitelist] = useState([]);
    const [indicators, setIndicators] = useState([]);
    const [globalindicators, setGlobalIndicators] = useState([]);
    const history = useHistory();

    useEffect(() => {
        if(props.currentgroup == '') history.push('/');
        else{
            let params = {
                currentgroup: props.currentgroup
            }
            fetch('/api/whitelist', {
                method: 'post',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': props.client.transports[0].auth.csrfToken
                },
                credentials: 'same-origin',
                body: JSON.stringify(params)
            }).then(res=>{return res.json()})
            .then(res=>{
                setWhitelist(res.whitelist);
                setIndicators(res.indicators);
                setGlobalIndicators(res.globalindicators);
                setIsLoading(false);
            })
        }
    },[props.currentgroup]);

    const saveWhitelist = (newList) =>{
        let flag = false;
        const newWhitelist = [];
        for(const list of whitelist){
            if(list.id === newList.id){
                newWhitelist.push(newList);
                flag = true;
            }
            else newWhitelist.push(list);
        }
        if(!flag)
            newWhitelist.push(newList);
        setWhitelist(newWhitelist);
    }

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
    
    const WhiteListView = () => {
        if(isLoading)
            return <Loading/>
        else{
            return <WhiteList client={props.client} whitelist={whitelist} saveWhitelist={saveWhitelist} saveIndicator={saveIndicator} indicators={indicators} />
        }
    }

    return(
        <Switch>
            <Route path="/whitelist/new">
                <AddWhitelist client={props.client} indicators={indicators} saveWhitelist={saveWhitelist} />
            </Route>
            <Route path="/whitelist">
                {WhiteListView()}
            </Route>
        </Switch>
    );
}

export default WhiteLists