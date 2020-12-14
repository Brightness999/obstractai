import React, {useState} from "react";
import {Link, useHistory} from "react-router-dom";
import {getAction} from "../../api";
import {API_ROOT} from "../const";


const UpdateIntelGroup = function(props) {
  console.log(props);
  const client = props.client;
  const [id, setId] = useState(props.id || null);
  const [name, setName] = useState(props.name || '');
  const [description, setDescription] = useState(props.description || '');
  const [planid, setPlanid] = useState(props.plan_id || '');
  const [errors, setErrors] = useState({});
  const editMode = Boolean(id);
  const history = useHistory();


  const saveIntelgroup = function() {
    let params = {
      name: name,
      description: description,
      plan_id: planid,
    };
    let action;
    if (editMode) {
      params['id'] = id;
      action = getAction(API_ROOT, ["intelgroups", "partial_update"]);
    } else {
      action = getAction(API_ROOT, ["intelgroups", "create"]);
    }
    client.action(window.schema, action, params).then((result) => {
      // find the appropriate item in the list and update in place
      props.intelgroupSaved(result);
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
      <h2 className="subtitle">Intel Group Details</h2>
      <div className="field">
        <label className="label">Name</label>
        <div className="control">
          <input className="input" type="text" placeholder="Name"
                onChange={(event) => setName(event.target.value)} value={name}>
          </input>
        </div>
        {renderErrors(errors.name)}
      </div>
      <div className="field">
        <div className="control">
          <label className="label">Description</label>
          <input className="input" type="text" placeholder="Description"
                onChange={(event) => setDescription(event.target.value)} value={description}>
          </input>
        </div>
        {renderErrors(errors.description)}
      </div>
      <div className="field">
        <div className="control">
          <label className="label">Plan</label>
          <input className="input" type="number" min="0" placeholder="1"
                 onChange={(event) => setPlanid(event.target.value)} value={planid}>
          </input>
        </div>
        {renderErrors(errors.planid)}
      </div>
      <div className="field is-grouped">
        <div className="control">
          <button type='button' className={`button is-primary ${editMode ? 'is-outlined' : ''}`}
                  onClick={() => saveIntelgroup()}>
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

export default UpdateIntelGroup;
