import React from "react";
import {Link} from "react-router-dom";

const PlanTable = function (props) {
 
  return (
    <tr>
      <td>{props.name}</td>
      <td>{props.type}</td>
      <td>{ props.annual_price }</td>
      <td>{ props.monthly_price }</td>
      <td>{ props.max_feeds }</td>
      <td>{ props.max_users }</td>
      <td>{ props.enable_custom_feeds }</td>
      <td>{ props.enable_api }</td>
      <td>{ props.enable_custom_extraction }</td>
      <td className="has-text-right">
        <Link to={`/edit/${props.id}`}>
          <div className="button is-primary is-outlined">
            <span className="icon is-small"><i className="fa fa-edit" /></span>
            <span>Edit</span>
          </div>
        </Link>
        <a style={{'marginLeft': '1em'}} onClick={() => props.delete(props.index)}>
          <div className="button is-text">
            <span>Delete</span>
          </div>
        </a>
      </td>
    </tr>
  );
}

export default PlanTable;
