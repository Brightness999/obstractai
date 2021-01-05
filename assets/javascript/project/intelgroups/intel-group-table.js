import React from "react";
import {Link} from "react-router-dom";
import { Tr, Td } from 'react-super-responsive-table';

const IntelGroupTable = function (props) {
  return (
    <Tr>
      <Td className="has-text-left">{props.intelgroup.name}</Td>
      <Td className="has-text-left">{props.intelgroup.description}</Td>
      <Td className="has-text-left">{ props.intelgroup.plan_id }</Td>
      <Td className="has-text-right">
        {(()=>{
          if(props.role ==2) return ( 
            <>
              <Link to={`/intelgroups/manage/${props.intelgroup_id}`} style={{'marginRight': '1em'}}>
                <div className="button is-primary is-outlined">
                  <span className="icon is-small"><i className="fa fa-eye" /></span>
                  <span>Manage</span>
                </div>
              </Link>
              <a style={{'marginLeft': '1em'}} onClick={() => props.deleteIntelGroup(props.index)}>
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
            <a style={{'marginLeft': '1em'}} onClick={() => props.invitation(props.index)}>
              <div className="button is-text">
                <span>Accept</span>
              </div>
            </a>
          );
        })()}
      
      </Td>
    </Tr>
  
  );
}

export default IntelGroupTable;
