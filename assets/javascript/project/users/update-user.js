import React, {useEffect, useState} from "react";
import {Link, useHistory} from "react-router-dom";
import ReactTags from 'react-tag-autocomplete';

import {getAction} from "../../api";
import {API_ROOT} from "../const";


const UpdateUser = function(props) {
  const [isLoading, setIsLoading] = useState(true);
  const [allusers, setAllUsers] = useState([]);
  const [tags, setTags] = useState([]);
  const history = useHistory();
  const userOptions = allusers.map((user)=>({
    id: user.id,
    name: user.email
  }));
  const reacttag= React.createRef();
  const onDelete= (i)=> {
      var temp = tags.slice(0)
      temp.splice(i, 1)
      setTags(temp)
    }
  
  const onAddition = (tag)=> {
    let mailformat = /^([A-Za-z0-9_\-\.])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$/;
    if(tag.name.match(mailformat)){
      var temp = [].concat(tags, tag)
      setTags(temp)
    }
  }
  useEffect(() => {
    fetch('/api/users', {
      method: 'get',
      headers: {
        'Content-Type': 'application/json'
      },
      credentials: 'same-origin',
    }).then(res=>{return res.json()})
    .then(res=>{
      setAllUsers(res);
      setIsLoading(false);
    })
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
    const userids = [];
    const emails = [];
    tags.forEach(tag => {
      if(Boolean(tag.id)) {
        userids.push(tag.id)
      }
      else {
        emails.push(tag.name)
      }
    });
    let params = {
      group_id: props.group_id,
      userids: userids,
      emails: emails
    };
    if(userids.length > 0 || emails.length>0){
      fetch('/api/invite', {
        method: 'post',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': props.client.transports[0].auth.csrfToken
        },
        credentials: 'same-origin',
        body: JSON.stringify(params)
      }).then(res=> {return res.json()})
      .then(res=>{
        if(!Boolean(res[0].role)){
          props.userSaved(res);
        } 
        history.push(`/${props.group_id}`);
      })
    }
  };

  if(isLoading){
    return <Loading/>
  }
  return (
    <section className="section app-card">
      <h2 className="subtitle">User Details</h2>
      <div className="field">
        <label className="label">Email</label>
        <ReactTags
          ref={reacttag}
          tags={tags}
          suggestions={userOptions}
          onDelete={onDelete}
          onAddition={onAddition}
          allowNew={true}
        />
      </div>
      
      <div className="field is-grouped">
        <div className="control">
          <button type='button' className="button is-primary"
                  onClick={() => inviteUser()}>
            <span>Invite</span>
          </button>
        </div>
        <div className="control">
            <button className="button is-text" onClick={()=>history.goBack()}>
              <span>Cancel</span>
            </button>
        </div>
      </div>
    </section>
  );
};

export default UpdateUser;
