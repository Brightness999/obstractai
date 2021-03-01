import React, {useEffect, useState} from "react";
import { useHistory } from "react-router-dom";
import ReactTags from 'react-tag-autocomplete';
import { Steps } from 'intro.js-react';
import { Alert, AlertTitle } from '@material-ui/lab';
import { Container, Dialog} from "@material-ui/core";

const UpdateUser = function(props) {
  const [tags, setTags] = useState([]);
  const [isAlert, setIsAlert] = useState(false);
  const history = useHistory();
  const [stepsEnabled, setStepsEnabled] = useState(true);
	const steps = [{
		element: '#users',
		intro: 'Comma separated list of emails for users to invite'
	},{
		element: '#button',
		intro: 'Click button to invite users.'
	}]
  const reacttag= React.createRef();
  const onDelete= (i)=> {
      var temp = tags.slice(0)
      temp.splice(i, 1)
      setTags(temp)
  }
  const onAddition = (tag)=> {
    let mailformat = /^([A-Za-z0-9_\-\.\+])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$/;
    if(tag.name.match(mailformat)){
      var temp = [].concat(tags, tag)
      setTags(temp)
    }
  }
  
  const inviteUser = function() {
    const emails = [];
    tags.forEach(tag => {
      emails.push(tag.name);
    });
    let params = {
      group_id: props.group_id,
      emails: emails
    };
    if(emails.length > 0){
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
      {props.onboarding &&
      <Steps
        enabled={stepsEnabled}
        steps={steps}
        initialStep={0}
        onBeforeExit={(index)=>{
          if(index==1){
            document.querySelector('#button').addEventListener('click', function(){
              setStepsEnabled(false);
              window.location.href="/home/feeds";    
              return true;
            })
            return false;
          }
          else{
            return false;
          }
        }}
        onBeforeChange={(nextindex)=>{
          if((nextindex==0 || nextindex==1) && tags.length > 0){
            return true;
          }
          else{
            return false;
          }
        }}
        onExit={()=>{
          setStepsEnabled(false);
        }}
      />}
      <section className="section app-card">
        <h2 className="subtitle">User Details</h2>
        <div className="field" id="users">
          <label className="label">Email</label>
          <ReactTags
            ref={reacttag}
            tags={tags}
            onDelete={onDelete}
            onAddition={onAddition}
            allowNew={true}
            addOnBlur={true}
            placeholderText="Comma separated list of emails for users to invite"
            delimiters={['Tab', ',', ' ']}
          />
        </div>
        
        <div className="field is-grouped">
          <div className="control">
            <button type='button' className="button is-primary" id="button" onClick={() => inviteUser()}>
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
