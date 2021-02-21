import React, {useEffect, useState} from "react";
import { useHistory } from "react-router-dom";
import ReactTags from 'react-tag-autocomplete';
import { Steps } from 'intro.js-react';
import { Alert, AlertTitle } from '@material-ui/lab';
import { Container, Dialog} from "@material-ui/core";

const UpdateUser = function(props) {
  const [allusers, setAllUsers] = useState(props.allusers);
  const [tags, setTags] = useState([]);
  const [isAlert, setIsAlert] = useState(false);
  const history = useHistory();
  const [stepsEnabled, setStepsEnabled] = useState(true);
	const steps = [{
		element: '.users',
		intro: 'Comma separated list of emails for users to invite'
	}]
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
        if(Boolean(res.message)){
          setIsAlert(true);
        }
        else{
          if(!Boolean(res.role)){
            props.userSaved(res);
          } 
          history.push('/users');
        }
      })
    }
  };

  return (
    <Container>
      <Dialog
				maxWidth="md"
				fullWidth
				open={isAlert}
				onClose={()=>setIsAlert(false)}
				aria-labelledby="alert-dialog-title"
				aria-describedby="alert-dialog-description"
			>
				<Alert severity="warning" className="my-5">
				<AlertTitle className="subtitle is-4 has-text-weight-bold">Fail</AlertTitle>
				<span className="subtitle is-5">! You must upgrade your Intel Group plan to perform that action.</span>
				</Alert>
			</Dialog>
      {props.mygroups.length == 0 &&
      <Steps
        enabled={stepsEnabled}
        steps={steps}
        initialStep={0}
        onExit={(index)=>{
          setStepsEnabled(false);
          if(index==0)
            window.location.href="/home/feeds/";
        }}
        options={{
          doneLabel: 'Next'
        }}
      />}
      <section className="section app-card">
        <h2 className="subtitle">User Details</h2>
        <div className="field users">
          <label className="label">Email</label>
          <ReactTags
            ref={reacttag}
            tags={tags}
            suggestions={userOptions}
            onDelete={onDelete}
            onAddition={onAddition}
            allowNew={true}
            placeholderText="Comma separated list of emails for users to invite"
            delimiters={['Enter', 'Tab', ',', ' ']}
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
    </Container>
  );
};

export default UpdateUser;
