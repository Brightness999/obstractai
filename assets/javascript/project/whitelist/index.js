import React, { useState, useEffect } from "react";
import { Switch, Route, Link, useHistory } from "react-router-dom";
import { Container, Grid } from "@material-ui/core";
import { Table, Thead, Tbody, Tr, Th } from "react-super-responsive-table";
import { Alert, AlertTitle } from "@material-ui/lab";
import { Steps } from 'intro.js-react';

import ListTable from "./list-table";
import AddWhitelist from "./add-whitelist";
import IndicatorTable from "./indicator-table";


const Loading = () => {
    return (
        <div className='app-card has-text-centered'>
            <div className="lds-ripple"><div></div><div></div></div>
            <p className="heading has-text-primary">Loading...</p>
        </div>
    );
}

const Plan = (props) => {
    const [isAlert, setIsAlert] = useState(false);

    const ManagePlan = () => {
        if (props.currentrole.role == 2) location.href = `/subscriptions/intelgroup/${props.currentgroup}`;
        else setIsAlert(true);
    }

    return <div className="my-6">
        <h1 className="title is-size-3 has-text-centered py-6">No plan! You must select a plan to perform that action. <a className="tag title is-3" onClick={ManagePlan}>Click here to manage your plan</a></h1>
        {isAlert && <Grid container direction="row" justify="center" alignItems="center">
            <Grid item xs={6}>
                <Alert className="has-text-centered title is-size-4" severity="error" onClose={() => setIsAlert(false)}>! Please contact the feed group administrator to manage intel group plan payment to reinstate access.</Alert>
            </Grid>
        </Grid>}
    </div>
}

const WhiteList = (props) => {
    const [stepsEnabled, setStepsEnabled] = useState(true);
    const steps = [{
        element: '#indicator',
        intro: 'Indicators extracted from fulltext'
    }, {
        title: '',
        intro: 'Congratulation!!! 👋'
    }]

    const ListEnable = (index) => {
        let params;
        if (props.whitelist[index].enabled === 'Enable')
            params = { id: props.whitelist[index].id, enabled: 'Disable' };
        else if (props.whitelist[index].enabled === 'Disable')
            params = { id: props.whitelist[index].id, enabled: 'Enable' };
        fetch('/api/whitelist', {
            method: 'put',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': props.client.transports[0].auth.csrfToken
            },
            credentials: 'same-origin',
            body: JSON.stringify(params)
        }).then(res => { return res.json() })
            .then(res => props.saveWhitelist(res))
    }

    const IndicatorEnable = (index) => {
        let params = { id: props.groupindicators[index].id };
        fetch('/api/indicators', {
            method: 'put',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': props.client.transports[0].auth.csrfToken
            },
            credentials: 'same-origin',
            body: JSON.stringify(params)
        }).then(res => { return res.json() })
            .then(res => {
                props.saveIndicator(res);
            })
    }

    const setOnboarding = () => {
        fetch('/api/onboarding', {
            method: 'get',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': props.client.transports[0].auth.csrfToken,
            },
            credentials: 'same-origin',
        }).then(res => { return res.json(); })
            .then(res => {
                setStepsEnabled(false);
                window.location.href = '/app';
            })
    }

    return (
        <Container>
            {props.onboarding &&
                <Steps
                    enabled={stepsEnabled}
                    steps={steps}
                    initialStep={0}
                    options={{ doneLabel: 'Done' }}
                    onBeforeExit={(index) => {
                        if (index == 1) {
                            setOnboarding();
                        }
                        return false;
                    }}
                    onExit={() => { }}
                />}
            <section className="section">
                {props.isInit &&
                    <Alert severity="info" className="my-5">
                        <AlertTitle className="subtitle is-4 has-text-weight-bold">Info</AlertTitle>
                        <span className="subtitle is-5">{props.message}</span>
                    </Alert>}
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
                        {props.groupindicators.map((indicator, index) => {
                            return <IndicatorTable index={index} key={indicator.id} indicator={indicator} IndicatorEnable={(index) => IndicatorEnable(index)} isAutoDown={props.isAutoDown} />
                        })}
                    </Tbody>
                </Table>
            </section>
            <section className="section">
                <span className="title is-5">Manage by whitelist</span>
                <Link to="/whitelist/new">
                    <button className={props.isAutoDown ? "button is-static is-pulled-right" : "button is-info is-pulled-right"}  >
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
                                return <ListTable index={index} key={list.id} list={list} ListEnable={(index) => ListEnable(index)} isAutoDown={props.isAutoDown} />
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
    const [groupindicators, setGroupIndicators] = useState([]);
    const [globalindicators, setGlobalIndicators] = useState([]);
    const [currentgroup, setCurrentGroup] = useState('');
    const history = useHistory();

    useEffect(() => {
        if (props.currentgroup == '' && !props.onboarding) {
            history.push('/');
        }
        else {
            setCurrentGroup(props.currentgroup);
            if (currentgroup != '' && currentgroup != props.currentgroup) {
                history.push('/intelreports');
            }
            else {
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
                }).then(res => { return res.json() })
                    .then(res => {
                        console.log(res);
                        setWhitelist(res.whitelist);
                        setGroupIndicators(res.groupindicators);
                        setGlobalIndicators(res.globalindicators);
                        setIsLoading(false);
                    });
            }
        }
    }, [props.currentgroup]);

    const saveWhitelist = (newList) => {
        let flag = false;
        const newWhitelist = [];
        for (const list of whitelist) {
            if (list.id === newList.id) {
                newWhitelist.push(newList);
                flag = true;
            }
            else newWhitelist.push(list);
        }
        if (!flag)
            newWhitelist.push(newList);
        setWhitelist(newWhitelist);
    }

    const saveIndicator = (newIndicator) => {
        let flag = false;
        const newIndicators = [];
        for (const indicator of groupindicators) {
            if (indicator.id === newIndicator.id) {
                newIndicators.push(newIndicator);
                flag = true;
            }
            else newIndicators.push(indicator);
        }
        if (!flag)
            newIndicators.push(newIndicator);
        setGroupIndicators(newIndicators);
    }

    const WhiteListView = () => {
        if (isLoading)
            return <Loading />
        else {
            if (props.currentrole.role == 0)
                return (
                    <div className='app-card has-text-centered'>
                        <div className="lds-ripple"><div></div><div></div></div>
                        <p className="subtitle is-3">! You have an invitation to <span className="title is-3 has-text-primary">{props.currentrole.intelgroup.name}</span> pending. <Link className="muted-link subtitle is-3" to="/account" >Click here to accept.</Link></p>
                    </div>
                )
            if (props.currentrole.role == 1)
                return (
                    <div className='section has-text-centered'>
                        <p className="subtitle is-3">! You are now a member of <span className="title is-3 has-text-primary">{props.currentrole.intelgroup.name}</span>.</p>
                    </div>
                )
            if (props.currentrole.role == 2 || props.onboarding) {
                if (props.isPlan)
                    return <WhiteList client={props.client} whitelist={whitelist} saveWhitelist={saveWhitelist} saveIndicator={saveIndicator} onboarding={props.onboarding}
                        groupindicators={groupindicators} isInit={props.isInit} isAutoDown={props.isAutoDown} message={props.message} mygroups={props.mygroups} />
                else return <Plan currentgroup={props.currentgroup} currentrole={props.currentrole} />
            }
        }
    }

    return (
        <Switch>
            <Route path="/whitelist/new">
                <AddWhitelist client={props.client} globalindicators={globalindicators} saveWhitelist={saveWhitelist} />
            </Route>
            <Route path="/whitelist">
                {WhiteListView()}
            </Route>
        </Switch>
    );
}

export default WhiteLists;