import React, {useEffect, useState} from "react";
import {Link, useHistory} from "react-router-dom";

import { Dropdown } from "semantic-ui-react";
import {getAction} from "../../api";
import {API_ROOT} from "../const";


const UpdateUser = function(props) {
  const client = props.client;
  const [id, setId] = useState(null);
  const [userids, setUserIds] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [allusers, setAllUsers] = useState([]);
  const [errors, setErrors] = useState({});
  const editMode = Boolean(id);
  const history = useHistory();
  const userOptions = allusers.map((user, index) => ({
    key: index,
    value: user.id,
    text: user.email
  }))
  useEffect(() => {
    const customer_action = getAction(API_ROOT, ["customers", "list"]);
    client.action(window.schema, customer_action).then((result) => {
      setAllUsers(result.results);
      setIsLoading(false);
    });
  },[]);
  
  const Loading = function() {
    return (
      <div className='app-card has-text-centered'>
        <div className="lds-ripple"><div></div><div></div></div>
        <p className="heading has-text-primary">Loading...</p>
      </div>
    )
  }

  
  const inviteUser = function() {
    let params = {
      group_id: props.group_id,
      userids: userids
    };
    if(userids.length > 0){
      const action = getAction(API_ROOT, ["user", "invitation"]);
      client.action(window.schema, action, params).then((result) => {
        if(result.role != 'success')
          props.userSaved(result);
        history.push('/'+props.group_id);
      }).catch((error) => {
        console.log("Error: ", error);
        setErrors(error.content);
      });
    }
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
  if(isLoading){
    return <Loading/>
  }
  return (
    <section className="section app-card">
      <h2 className="subtitle">User Details</h2>
      <div className="field">
        <label className="label">Email</label>
        <Dropdown
          placeholder='Select Users'
          fluid
          multiple
          search
          selection
          options={userOptions}
          onChange={(e, {value}) => {
            setUserIds(value);
          }}
        />
        {renderErrors(errors.email)}
      </div>
      
      <div className="field is-grouped">
        <div className="control">
          <button type='button' className={`button is-primary ${editMode ? 'is-outlined' : ''}`}
                  onClick={() => inviteUser()}>
              <span className="icon is-small">
                <i className="fa fa-plus"></i>
              </span>
            <span>Invite</span>
          </button>
        </div>
        <div className="control">
            <button className="button is-text" onClick={()=>{props.group_id == 'new' ? history.goBack() : history.push(`/${props.group_id}`)}}>
              <span>Cancel</span>
            </button>
        </div>
      </div>
    </section>
  );
};

export default UpdateUser;
