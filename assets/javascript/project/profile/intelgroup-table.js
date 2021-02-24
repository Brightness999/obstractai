import React, { useState } from "react";
import { Tr, Td } from 'react-super-responsive-table';
import {
    Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle
} from '@material-ui/core';

const IntelgroupTable = (props) => {

    const [open, setOpen] = useState(false);

    return (
        <Tr>
            <Td>{props.intelgroup.intelgroup.name}</Td>
            {props.intelgroup.role == 2 && <Td>Admin</Td>}
            {props.intelgroup.role == 1 && <Td>Member</Td>}
            {props.intelgroup.role == 0 && <Td>Pending</Td>}
            {props.intelgroup.role == 4 && <Td>Request</Td>}
            {props.intelgroup.role == 0 && <Td>
                <button className="button is-success" onClick={()=>setOpen(true)}>Accept invite</button>
                <Dialog
                    open={open}
                    onClose={()=>setOpen(false)}
                    aria-labelledby="alert-dialog-title"
                    aria-describedby="alert-dialog-description"
                >
                    <DialogTitle id="alert-dialog-title">{"Confrim invite"}</DialogTitle>
                    <DialogContent>
                    <DialogContentText id="alert-dialog-description1">
                        Confirm you would like to join Intel
                    </DialogContentText>
                    <DialogContentText id="alert-dialog-description2">
                        Group: {props.intelgroup.intelgroup.name}
                    </DialogContentText>
                    </DialogContent>
                    <DialogActions>
                        <button onClick={()=>{setOpen(false); props.acceptInvite(props.index);}} className="button is-success" autoFocus>
                            Confirm
                        </button>
                        <button onClick={()=>{setOpen(false); props.rejectInvite(props.index);}} className="button is-danger" >
                            Reject
                        </button>
                    </DialogActions>
                </Dialog>
            </Td>}
            {(props.intelgroup.role == 1 || props.intelgroup.role == 2) && <Td><button className="button is-primary" onClick={()=>props.leaveGroup(props.index)}>Leave group</button></Td>}
            {props.intelgroup.role == 4 && <Td><button className="button is-primary" onClick={()=>props.leaveGroup(props.index)}>Cancel Request</button></Td>}
        </Tr>
    );
}

export default IntelgroupTable;