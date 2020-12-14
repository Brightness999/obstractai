import React, {useState} from "react";
import {Link, useHistory} from "react-router-dom";
import {getAction} from "../../../api";
import {API_ROOT} from "../const";


const EditAddEmployeeWidget = function(props) {
  const client = props.client;
  console.log(props);
  const [id, setId] = useState(props.id || null);
  const [name, setName] = useState(props.name || '');
  const [department, setDepartment] = useState(props.department || EMPLOYEE_DEPARTMENT_CHOICES[0].id);
  const [salary, setSalary] = useState(props.salary || '');
  const [errors, setErrors] = useState({});
  const editMode = Boolean(id);
  const history = useHistory();


  const saveEmployee = function() {
    let params = {
      name: name,
      department: department,
      salary: salary,
    };
    let action;
    if (editMode) {
      params['id'] = id;
      action = getAction(API_ROOT, ["employees", "partial_update"]);
    } else {
      action = getAction(API_ROOT, ["employees", "create"]);
    }
    client.action(window.schema, action, params).then((result) => {
      // find the appropriate item in the list and update in place
      props.employeeSaved(result);
      history.push('/');
    }).catch((error) => {
      console.log("Error: ", error);
      setErrors(error.content);
    });
  };

  const renderErrors = function(errors) {
    if (errors) {
      return (
        <p className="help is-danger">
          { errors.map((error, i) => {
            return <span key={i}>{error}</span>
          })}
        </p>
      );
    }
    return '';
  };

  return (
    <section className="section app-card">
      <h2 className="subtitle">Employee Details</h2>
      <div className="field">
        <label className="label">Name</label>
        <div className="control">
          <input className="input" type="text" placeholder="Michael Scott"
                 onChange={(event) => setName(event.target.value)} value={name}>
          </input>
        </div>
        <p className="help">Your employee's name.</p>
        {renderErrors(errors.name)}
      </div>
      <div className="field">
        <div className="control">
          <label className="label">Department</label>
          <div className="select">
            <select onChange={(event) => setDepartment(event.target.value)} value={department}>
              {EMPLOYEE_DEPARTMENT_CHOICES.map(
                (department, index) => <option key={department.id}
                                               value={department.id}>{department.name}</option>
              )}
            </select>
          </div>
        </div>
        <p className="help">What department your employee belongs to.</p>
        {renderErrors(errors.departnment)}
      </div>
      <div className="field">
        <div className="control">
          <label className="label">Salary</label>
          <input className="input" type="number" min="0" placeholder="50000"
                 onChange={(event) => setSalary(event.target.value)} value={salary}>
          </input>
        </div>
        <p className="help">Your employee's annual salary.</p>
        {renderErrors(errors.salary)}
      </div>
      <div className="field is-grouped">
        <div className="control">
          <button type='button' className={`button is-primary ${editMode ? 'is-outlined' : ''}`}
                  onClick={() => saveEmployee()}>
              <span className="icon is-small">
                <i className={`fa ${editMode ? 'fa-check' : 'fa-plus'}`}></i>
              </span>
            <span>{editMode ? 'Save Employee' : 'Add Employee'}</span>
          </button>
        </div>
        <div className="control">
          <Link to="/">
            <button className="button is-text">
              <span>Cancel</span>
            </button>
          </Link>
        </div>
      </div>
    </section>
  );
};

export default EditAddEmployeeWidget;
