import React from "react";
import {Link} from "react-router-dom";

const EmployeeTableRow = function (props) {
  const formatter = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  });
  return (
    <tr>
      <td>{props.name}</td>
      <td>{props.department}</td>
      <td className="has-text-right">{ formatter.format(props.salary) }</td>
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

export default EmployeeTableRow;
