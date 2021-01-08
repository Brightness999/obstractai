import React from "react";
import {Link} from "react-router-dom";
import { Tr, Td } from 'react-super-responsive-table';
import { Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle } from "@material-ui/core";

const IntelGroupTable = function (props) {
  const [invite, setInvite] = React.useState(false);
  
  return (
    <Tr>
      <Td className="has-text-left">{props.intelgroup.name}</Td>
      <Td className="has-text-left">{props.intelgroup.description}</Td>
      <Td className="has-text-left">{ props.intelgroup.plan_id }</Td>
      <Td className="has-text-right">
        {(()=>{
          if(props.role ==2) return ( 
            <>
              <Link to={`/intelgroups/manage/${props.intelgroup_id}`} >
                <div className="button is-primary is-outlined">
                  <span className="icon is-small"><i className="fa fa-eye" /></span>
                  <span>Manage</span>
                </div>
              </Link>
              <Link to={`/intelgroups/${props.intelgroup_id}`} className="mx-4" >
                <div className="button is-primary is-outlined">
                  <span className="icon is-small"><i className="fa fa-edit" /></span>
                  <span>Edit</span>
                </div>
              </Link>
              
              <a onClick={() => props.deleteIntelGroup(props.index)}>
                <div className="button is-text">
                  <span>Delete</span>
                </div>
              </a>
            </>
          );
          if(props.role == 1) return(
            <Link to={`/intelgroups/manage/${props.intelgroup_id}`} style={{'marginRight': '1em'}}>
              <div className="button is-primary is-outlined">
                <span className="icon is-small"><i className="fa fa-eye" /></span>
                <span>View</span>
              </div>
            </Link>
          );
          if(props.role == 0) return(
            <a onClick={() => setInvite(true)}>
              <div className="button is-text">
                <span>Accept</span>
              </div>
            </a>

          );
        })()}
        <Dialog
          open={invite}
          onClose={()=>setInvite(false)}
          aria-labelledby="alert-dialog-title"
          aria-describedby="alert-dialog-description"
        >
          <DialogTitle id="alert-dialog-title">Confrim invite</DialogTitle>
          <DialogContent>
          <DialogContentText id="alert-dialog-description1">
            Confirm you would like to join Intel
          </DialogContentText>
          <DialogContentText id="alert-dialog-description2">
            Group: {props.intelgroup.name}
          </DialogContentText>
          </DialogContent>
          <DialogActions>
            <button onClick={()=>{setInvite(false); props.invitation(props.index);}} className="button is-success" autoFocus>
              Confirm
            </button>
            <button onClick={()=>{setInvite(false); props.rejectInvite(props.index);}} className="button is-danger" >
              Reject
            </button>
          </DialogActions>
        </Dialog>
      </Td>
    </Tr>
  
  );
}

export default IntelGroupTable;
