import React, { useState } from "react";
import { Tr, Td } from 'react-super-responsive-table';
import {
    Dialog, DialogActions, DialogContent, DialogTitle, TextField
} from '@material-ui/core';
import Alert from '@material-ui/lab/Alert';

const WebhookTable = (props) => {
    const [open, setOpen] = useState(false);
    const [intelgroup, setIntelgroup] = useState(props.webhook.intelgroup.id);
    const [endpoint, setEndpoint] = useState(props.webhook.endpoint);
    const [description, setDescription] = useState(props.webhook.description);
    const [words, setWords] = useState(props.webhook.words);
    const [isAlert, setIsAlert] = useState(false);

    const editEndpoint = () => {
        let params = {id:props.webhook.id, endpoint: endpoint, intelgroup_id: intelgroup, description:description, isenable:props.webhook.isenable, words:words}
        if(intelgroup != '0' && endpoint.trim() != '' && description != '')
            fetch('/api/webhooks', {
                method: 'put',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': props.client.transports[0].auth.csrfToken,
                },
                credentials: 'same-origin',
                body: JSON.stringify(params),
            }).then((res)=>{return res.json()})
            .then((res)=>{
                props.saveWebhooks(res);
                setOpen(false);
            });
        else setIsAlert(true);
    }

    const enableWebhook = () => {
        let params ={id:props.webhook.id, isenable:props.webhook.isenable?false:true, endpoint: endpoint.trim(), intelgroup_id: intelgroup, description:description.trim(), words:words.trim()}
        if(intelgroup != '0' && endpoint.trim() != '' && description.trim() != '')
            fetch('/api/webhooks', {
                method: 'put',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': props.client.transports[0].auth.csrfToken,
                },
                credentials: 'same-origin',
                body: JSON.stringify(params),
            }).then((res)=>{return res.json()})
            .then((res)=>{
                props.saveWebhooks(res);
                setOpen(false);
            });
        else setIsAlert(true);
    }

    const deleteWebhook = () => {
        let params = {id:props.webhook.id}
        if(confirm('Are you sure to delete?'))
            fetch('/api/webhooks', {
                method: 'delete',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': props.client.transports[0].auth.csrfToken,
                },
                credentials: 'same-origin',
                body: JSON.stringify(params),
            }).then((res)=>{return res.json()})
            .then((res)=>{
                props.saveWebhooks(res);
                setOpen(false);
            });
    }

    return (
        <Tr>
            <Td>{props.webhook.endpoint}</Td>
            <Td>{props.webhook.description}</Td>
            <Td>{props.webhook.intelgroup.name}</Td>
            <Td>{props.webhook.words}</Td>
            <Td>
                <button className="button is-info" onClick={()=>setOpen(true)} >Edit</button>
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
                            <TextField id="outlined-basic1" label="Endpoint" InputLabelProps={{shrink: true,}} size="small" placeholder="https://..." variant="outlined" value={endpoint} onChange={(e)=>setEndpoint(e.target.value)} />
                        </div>
                        <div className="semisection">
                            <TextField id="outlined-basic2" label="Description" InputLabelProps={{shrink: true,}} size="small" placeholder="Description" variant="outlined" value={description} onChange={(e)=>setDescription(e.target.value)} />
                        </div>
                        <div className="semisection">
                            <TextField
                                id="outlined-select-currency-native"
                                label="Words to listen on"
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
                                <option value="0"></option>
                                {props.intelgroups.map((intelgroup) => (
                                    <option key={intelgroup.id} value={intelgroup.intelgroup.id}>
                                    {intelgroup.intelgroup.name}
                                    </option>
                                ))}
                            </TextField>
                        </div>
                        <div className="semisection">
                        <TextField id="outlined-basic3" label="Words to listen on" InputLabelProps={{shrink: true,}} size="small" placeholder="words to listen on" variant="outlined" value={words} onChange={(e)=>setWords(e.target.value)} />
                        </div>
                    </DialogContent>
                    <DialogActions>
                        <button onClick={()=>{editEndpoint();}} className="button is-success" autoFocus>
                            Confirm
                        </button>
                        <button onClick={()=>{setOpen(false);}} className="button is-danger" >
                            Cancel
                        </button>
                    </DialogActions>
                </Dialog>
                <button className="button is-text mx-4" onClick={()=>deleteWebhook()} >Delete</button>
                <button className={props.webhook.isenable?"button is-light":"button is-success"} onClick={()=>enableWebhook()} >{props.webhook.isenable?"Disable":"Enable"}</button>
            </Td>
        </Tr>
    );
}

export default WebhookTable;