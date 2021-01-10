import React from "react";
import {Link} from "react-router-dom";

const PlanTable = function (props) {
  return (
    <tr>
      <td>{props.name}</td>
      <td>{props.types}</td>
      <td>{ props.annual_price }</td>
      <td>{ props.monthly_price }</td>
      <td>{ props.max_feeds }</td>
      <td>{ props.max_users }</td>
      <td>{ props.enabled_custom_feeds }</td>
      <td>{ props.enabled_api }</td>
      <td>{ props.enabled_custom_extraction }</td>
      <td className="has-text-right">
        <Link to={`/plans/edit/${props.id}`}>
          <div className="button is-primary is-outlined">
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
