import React, {useState} from "react";
import {Link, useHistory} from "react-router-dom";
import {getAction} from "../../api";
import {API_ROOT} from "../const";


const UpdatePlan = function(props) {
  const client = props.client;
  const [id, setId] = useState(props.id || null);
  const [name, setName] = useState(props.name || '');
  const [type, setType] = useState(props.types || '');
  const [annualprice, setAnnualPrice] = useState(props.annual_price || 0);
  const [monthlyprice, setMonthlyPrice] = useState(props.monthly_price || 0);
  const [maxfeeds, setMaxFeeds] = useState(props.max_feeds || '');
  const [maxusers, setMaxUsers] = useState(props.max_users || '');
  const [enablecustomfeeds, setEnableCustomFeeds] = useState(props.enabled_custom_feeds || '');
  const [enableapi, setEnableApi] = useState(props.enabled_api || '');
  const [enablecustomextraction, setEnableCustomExtraction] = useState(props.enabled_custom_extraction || '');
  const [errors, setErrors] = useState({});
  const editMode = Boolean(id);
  const history = useHistory();


  const savePlan = function() {
    let params = {
      name: name,
      types: type,
      annual_price: annualprice,
      monthly_price: monthlyprice,
      max_feeds: maxfeeds,
      max_users: maxusers,
      enabled_custom_feeds: enablecustomfeeds,
      enabled_api: enableapi,
      enabled_custom_extraction: enablecustomextraction,
    };
    let action;
    if (editMode) {
      params['id'] = id;
      action = getAction(API_ROOT, ["plans", "partial_update"]);
    } else {
      action = getAction(API_ROOT, ["plans", "create"]);
    }
    client.action(window.schema, action, params).then((result) => {
      // find the appropriate item in the list and update in place
      props.planSaved(result);
      history.push('/plans');
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
      <h2 className="subtitle">Plan Details</h2>
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
          <label className="label">Type</label>
          <input className="input" type="text" placeholder="Type"
                onChange={(event) => setType(event.target.value)} value={type}>
          </input>
        </div>
        {renderErrors(errors.type)}
      </div>
      <div className="field">
        <div className="control">
          <label className="label">Annual Price</label>
          <input className="input" type="number" placeholder="0"
                 onChange={(event) => setAnnualPrice(event.target.value)} value={annualprice}>
          </input>
        </div>
        {renderErrors(errors.annualprice)}
      </div>
      <div className="field">
        <div className="control">
          <label className="label">Monthly Price</label>
          <input className="input" type="number" placeholder="0"
                 onChange={(event) => setMonthlyPrice(event.target.value)} value={monthlyprice}>
          </input>
        </div>
        {renderErrors(errors.monthlyprice)}
      </div>
      <div className="field">
        <div className="control">
          <label className="label">Max Feeds</label>
          <input className="input" type="text" 
                 onChange={(event) => setMaxFeeds(event.target.value)} value={maxfeeds}>
          </input>
        </div>
        {renderErrors(errors.maxfeeds)}
      </div>
      <div className="field">
        <div className="control">
          <label className="label">Max Users</label>
          <input className="input" type="number" placeholder="0"
                 onChange={(event) => setMaxUsers(event.target.value)} value={maxusers}>
          </input>
        </div>
        {renderErrors(errors.maxusers)}
      </div>
      <div className="field">
        <div className="control">
          <label className="label">Enable Customize Feeds</label>
          <input className="input" type="text" placeholder="True"
                 onChange={(event) => setEnableCustomFeeds(event.target.value)} value={enablecustomfeeds}>
          </input>
        </div>
        {renderErrors(errors.enablecustomfeeds)}
      </div>
      <div className="field">
        <div className="control">
          <label className="label">Enabel API</label>
          <input className="input" type="text" placeholder="True"
                 onChange={(event) => setEnableApi(event.target.value)} value={enableapi}>
          </input>
        </div>
        {renderErrors(errors.enableapi)}
      </div>
      <div className="field">
        <div className="control">
          <label className="label">Enable Custom Extraction</label>
          <input className="input" type="text" placeholder="True"
                 onChange={(event) => setEnableCustomExtraction(event.target.value)} value={enablecustomextraction}>
          </input>
        </div>
        {renderErrors(errors.enablecustomextraction)}
      </div>
      <div className="field is-grouped">
        <div className="control">
          <button type='button' className={`button is-primary ${editMode ? 'is-outlined' : ''}`}
                  onClick={() => savePlan()}>
            <span>{editMode ? 'Save Employee' : 'Add Employee'}</span>
          </button>
        </div>
        <div className="control">
          <Link to="/plans">
            <button className="button is-text">
              <span>Cancel</span>
            </button>
          </Link>
        </div>
      </div>
    </section>
  );
};

export default UpdatePlan;
