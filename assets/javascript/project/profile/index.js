import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import {
    Dialog, DialogActions, DialogContent, DialogTitle,
    TextField, Image, Container
} from '@material-ui/core';
import { Table, Thead, Tbody, Tr, Th } from 'react-super-responsive-table';
// import { WithContext as ReactTags } from 'react-tag-input/dist-modules/components/ReactTags';

import Alert from '@material-ui/lab/Alert';
import { getAction } from "../../api";
import { API_ROOT } from "../const";
import IntelgroupTable from "./intelgroup-table";
import APIKeyTable from "./apikey-table";
import WebhookTable from "./webhook-table";

const Loading = function() {
	return (
		<div className='app-card has-text-centered'>
			<div className="lds-ripple"><div></div><div></div></div>
			<p className="heading has-text-primary">Loading...</p>
		</div>
	)
}

const Profile = (props) => {
    const [email, setEmail] = useState(props.profile.email);
    const [firstname, setFirstName] = useState('');
    const [lastname, setLastName] = useState('');
    

    return (
        <section className="semisection">
            
        
            <h1 className="title is-3">User account</h1>
            <span>
                <TextField id="outlined-basic1" size="small" label="Email" value={email} placeholder="Email(confirmed)" variant="outlined" onChange={(e)=>setEmail(e.target.value)} />
                <button className="button is-primary ml-5">Edit</button>
            </span>
            <p className="px-4 pt-4"><a className="muted-link" href ="/accounts/password/change"><span>Reset password</span></a></p>
            <p className="px-4"><Link className="muted-link" to ="password/change"><span>Enable 2FA</span></Link></p>
        </section>
    );

}

const Intelgroups = (props) => {
    const [intelgroups, setIntelgroups] = useState(props.intelgroups);
    const [isAlert, setIsAlert] = useState(false);
    const [message, setMessage] = useState('');
    const acceptInvite = (index) => {
        const action = getAction(API_ROOT, ['intelgroups', 'invitate']);
        const params = {'role': intelgroups[index].id};
        props.client.action(window.schema, action, params).then((result) => {
            setIntelgroups(result);
        });
    }
    
    const rejectInvite = (index) => {
        const action = getAction(API_ROOT, ['intelgroups', 'reject']);
        const params = {'role': intelgroups[index].id};
        props.client.action(window.schema, action, params).then((result) => {
            setIntelgroups(result);
        });
    }

    const leaveGroup = (index) => {
        const action = getAction(API_ROOT, ['intelgroups', 'leave']);
        const params = {'role': intelgroups[index].id};
        props.client.action(window.schema, action, params).then((result) => {
            if(result[0].message){
                setMessage("You can't leave the group. Before leaving group, you must make other people admin.")
                setIsAlert(true);
            }
            else
                setIntelgroups(result);
        });
    }

    return (
        <section className="semisection">
            <h1 className="title is-5 py-4">Intel groups you belong to</h1>
            {isAlert && <Alert severity="error" onClose={()=>setIsAlert(false)}>{message}</Alert>}
            <Table className="table is-striped is-fullwidth has-vcentered-cells">
                <Thead>
                    <Tr>
                        <Th>Name</Th>
                        <Th>Role</Th>
                        <Th>Action</Th>
                    </Tr>
                </Thead>
                <Tbody>
                    {intelgroups.map((intelgroup, index)=>{
                        return <IntelgroupTable index={index} key={intelgroup.id} intelgroup={intelgroup} 
                            acceptInvite={(index)=>acceptInvite(index)} rejectInvite={(index)=>rejectInvite(index)} leaveGroup={(index)=>leaveGroup(index)} />
                    })}
                </Tbody>
            </Table>
        </section>
    );
}

const APIKeys = (props) => {
    const [apikeys, setAPIKeys] = useState(props.apikeys);
    const [open, setOpen] = useState(false);
    const [name, setName] = useState('');
    const [intelgroup, setIntelgroup] = useState('0');
    const [isAlert, setIsAlert] = useState(false);
    const createAPIKey = () => {

        let params = {'name': name, intelgroup_id: intelgroup}
        if(intelgroup != '0' && name.trim() != '')
            fetch('/api/apikeys', {
                method: 'post',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': props.client.transports[0].auth.csrfToken,
                },
                credentials: 'same-origin',
                body: JSON.stringify(params),
            }).then((res)=>{return res.json()})
            .then((res)=>{
                setAPIKeys(res);
                setOpen(false);
            });
        else setIsAlert(true);
    }

    return (
        <section className="semisection">
            <h1 className="title is-5">Your API keys</h1>
            <button className="button is-success" onClick={()=>setOpen(true)}>
                <span className="icon is-small">
                    <i className="fa fa-plus"></i>
                </span>
                <span>Create new key</span>
            </button>
            <Dialog
                open={open}
                onClose={()=>setOpen(false)}
                aria-labelledby="alert-dialog-title"
                aria-describedby="alert-dialog-description"
            >
                <DialogTitle id="alert-dialog-title">Create new API key</DialogTitle>
                <DialogContent>
                    {isAlert && <Alert severity="error" onClose={()=>setIsAlert(false)}>Please input exactly!!!</Alert>}
                    <div className="semisection">
                        <TextField id="outlined-basic" size="small" placeholder="name" variant="outlined" onChange={(e)=>setName(e.target.value)} />
                    </div>
                    <div className="semisection">
                        <TextField
                            id="outlined-select-currency-native"
                            select
                            fullWidth
                            size="small"
                            value={intelgroup}
                            onChange={(e)=>setIntelgroup(e.target.value)}
                            SelectProps={{
                                native: true,
                            }}
                            variant="outlined"
                        >
                            <option value="0">Select Intel group</option>
                            {props.intelgroups.map((intelgroup) => (
                                <option key={intelgroup.id} value={intelgroup.intelgroup.id}>
                                {intelgroup.intelgroup.name}
                                </option>
                            ))}
                        </TextField>
                    </div>
                </DialogContent>
                <DialogActions>
                    <button onClick={()=>{createAPIKey();}} className="button is-success" autoFocus>
                        Confirm
                    </button>
                    <button onClick={()=>{setOpen(false); }} className="button is-danger" >
                        Cancel
                    </button>
                </DialogActions>
            </Dialog>
            <Table className="table is-striped is-fullwidth has-vcentered-cells">
                <Thead>
                    <Tr>
                        <Th>API Key</Th>
                        <Th>Name</Th>
                        <Th>Intel Group</Th>
                        <Th>Action</Th>
                    </Tr>
                </Thead>
                <Tbody>
                    {apikeys.map((apikey, index)=>{
                        return <APIKeyTable index={index} key={apikey.id} apikey={apikey} />
                            
                    })}
                </Tbody>
            </Table>
        </section>
    );
}

const WebHooks = (props) => {
    const [webhooks, setWebHooks] = useState(props.webhooks);
    const [isAlert, setIsAlert] = useState(false);
    const [description, setDescription] = useState('');
    const [endpoint, setEndpoint] = useState('');
    const [intelgroup, setIntelgroup] = useState('0');
    const [open, setOpen] = useState(false);

    const createWebhook = () => {
        let params = {'endpoint': endpoint, intelgroup_id: intelgroup, description:description}
        if(intelgroup != '0' && endpoint.trim() != '' && description != '')
            fetch('/api/webhooks', {
                method: 'post',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': props.client.transports[0].auth.csrfToken,
                },
                credentials: 'same-origin',
                body: JSON.stringify(params),
            }).then((res)=>{return res.json()})
            .then((res)=>{
                setWebHooks(res);
                setOpen(false);
            });
        else setIsAlert(true);
    }

    const saveWebhooks = (newWebhooks) => {
        setWebHooks(newWebhooks);
    }

    return (
        <section className="semisection">
            <h1 className="title is-5">Your webhooks</h1>
            <button className="button is-success" onClick={()=>setOpen(true)}>
                <span className="icon is-small">
                    <i className="fa fa-plus"></i>
                </span>
                <span>Create new webhook</span>
            </button>
            <Dialog
                open={open}
                onClose={()=>setOpen(false)}
                aria-labelledby="alert-dialog-title"
                aria-describedby="alert-dialog-description"
            >
                <DialogTitle id="alert-dialog-title">Add a webhook endpoint</DialogTitle>
                <DialogContent>
                    {isAlert && <Alert severity="error" onClose={()=>setIsAlert(false)}>Please input exactly!!!</Alert>}
                    <div className="semisection">
                        <TextField id="outlined-basic1" size="small" placeholder="https://..." variant="outlined" onChange={(e)=>setEndpoint(e.target.value)} />
                    </div>
                    <div className="semisection">
                        <TextField id="outlined-basic2" size="small" placeholder="Description" variant="outlined" onChange={(e)=>setDescription(e.target.value)} />
                    </div>
                    <div className="semisection">
                        <TextField
                            id="outlined-select-currency-native"
                            select
                            fullWidth
                            size="small"
                            value={intelgroup}
                            onChange={(e)=>setIntelgroup(e.target.value)}
                            SelectProps={{
                                native: true,
                            }}
                            variant="outlined"
                        >
                            <option value="0">Select Intel group</option>
                            {props.intelgroups.map((intelgroup) => (
                                <option key={intelgroup.id} value={intelgroup.intelgroup.id}>
                                {intelgroup.intelgroup.name}
                                </option>
                            ))}
                        </TextField>
                    </div>
                </DialogContent>
                <DialogActions>
                    <button onClick={()=>{createWebhook(); setOpen(false);}} className="button is-success" autoFocus>
                        Confirm
                    </button>
                    <button onClick={()=>{setOpen(false);}} className="button is-danger" >
                        Cancel
                    </button>
                </DialogActions>
            </Dialog>
            <Table className="table is-striped is-fullwidth has-vcentered-cells">
                <Thead>
                    <Tr>
                        <Th>Endpoint</Th>
                        <Th>Description</Th>
                        <Th>Intel Group</Th>
                        <Th>Action</Th>
                    </Tr>
                </Thead>
                <Tbody>
                    {webhooks.map((webhook, index)=>{
                        return <WebhookTable index={index} key={webhook.id} webhook={webhook} intelgroups={props.intelgroups} client={props.client} saveWebhooks={(newWebhooks)=>saveWebhooks(newWebhooks)} />
                            
                    })}
                </Tbody>
            </Table>
        </section>
    );
}

const Account = () => {
    let auth = new coreapi.auth.SessionAuthentication({
		csrfCookieName: 'csrftoken',
		csrfHeaderName: 'X-CSRFToken'
	});
	const client = new coreapi.Client({auth: auth});
    const [isLoading, setIsLoading] = useState(true);
    const [profile, setProfile] = useState([]);
    const [intelgroups, setIntelGroups] = useState([]);
    const [apikeys, setAPIKeys] = useState([]);
    const [webhooks, setWebHooks] = useState([]);

    useEffect(() => {
        fetch('../../api/account', {
            method: 'get',
            headers: {
              'Content-Type': 'application/json',
              'accept': 'application/json',
            //   'X-CSRFToken': client.transports[0].auth.csrfToken,
            },
            credentials: 'same-origin',
        }).then((response)=> { return response.json();})
        .then((res)=>{
            console.log(res);
            setProfile(res.profile);
            setWebHooks(res.webhooks);
            setAPIKeys(res.apikeys);
            setIntelGroups(res.intelgroups);
            setIsLoading(false);
        });
    },[]);

    const AccountView = () => {
        if(isLoading)
            return <Loading/>
        else
            return (
                <Container>
                    <Profile profile={profile} client={client} />
                    <Intelgroups intelgroups={intelgroups} client={client} />
                    <APIKeys apikeys={apikeys} client={client} intelgroups={intelgroups} />
                    <WebHooks webhooks={webhooks} client={client} intelgroups={intelgroups} />
                </Container>
            )
    }

    return AccountView();
}

export default Account;
