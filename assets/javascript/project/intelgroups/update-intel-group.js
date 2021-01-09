import React, {useState} from "react";
import { Link, useHistory } from "react-router-dom";
import ReactTags from 'react-tag-autocomplete';

import {getAction} from "../../api";
import {API_ROOT} from "../const";


const UpdateIntelGroup = function(props) {
  const [id, setId] = useState(props.intelgroup_id || null);
  const [name, setName] = useState(props.intelgroup? props.intelgroup.name: '');
  const [description, setDescription] = useState(props.intelgroup? props.intelgroup.description : '');
  const [tags, setTags] = useState([]);
  const editMode = Boolean(id);
  const history = useHistory();  
  const userOptions = props.users.map((user)=>({
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
    var temp = [].concat(tags, tag)
    setTags(temp)
  }

  const saveIntelgroup = function() {
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
      name: name,
      description: description,
      userids: userids,
      emails: emails
    };
    let action;
    if (editMode) {
      params['id'] = id;
      action = getAction(API_ROOT, ["intelgroup", "partial_update"]);
    } else {
      action = getAction(API_ROOT, ["intelgroup", "newgroup"]);
    }
    if(name != '' && description != '' && userids != []){
      props.client.action(window.schema, action, params).then((result) => {
        props.intelgroupSaved(result);
        history.push('/intelgroups');
      })
    }
  };

  return (
    <section className="section app-card">
      <h2 className="subtitle">Intel Group Details</h2>
      <div className="field column is-two-thirds">
        <label className="label">Name</label>
        <div className="control">
          <input className="input" type="text" placeholder="Name"
                onChange={(event) => setName(event.target.value)} value={name} required={true}>
          </input>
        </div>
      </div>
      <div className="field column is-two-thirds">
        <div className="control">
          <label className="label">Description</label>
          <span>
          <input className="input" type="text" placeholder="Description"
                onChange={(event) => setDescription(event.target.value)} value={description} required={true}>
          </input>
          </span>
        </div>
      </div>
      {!editMode &&
      <div className="field column is-two-thirds">
        <div className="control" style={{zIndex:1}}>
          <label className="label">Invite Users</label>
          <ReactTags
            ref={reacttag}
            tags={tags}
            suggestions={userOptions}
            onDelete={onDelete}
            onAddition={onAddition}
            allowNew={true}
          />
        </div>
      </div>
      }
      <div className="field is-grouped">
        <div className="control">
          <button type='button' className={`button is-primary ${editMode ? 'is-outlined' : ''}`}
                  onClick={() => saveIntelgroup()} >
              <span className="icon is-small">
                <i className={`fa ${editMode ? 'fa-check' : 'fa-plus'}`}></i>
              </span>
            <span>{editMode ? 'Save intel group' : 'Create intel group'}</span>
          </button>
        </div>
        <div className="control">
          <Link to="/intelgroups">
            <button className="button is-text" >
              <span>Cancel</span>
            </button>
          </Link>
        </div>
      </div>
    </section>
  );
};

export default UpdateIntelGroup;
