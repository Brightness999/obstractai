import React, { useState } from "react";
import { Link } from "react-router-dom";
import { Grid } from "@material-ui/core";

import Styles from "../styles";

const Loading = () => {
	return (
		<div className='app-card has-text-centered'>
			<div className="lds-ripple"><div></div><div></div></div>
			<p className="heading has-text-primary">Loading...</p>
		</div>
	)
}

const FeedCard = function (props) {
  const [isLoading, setIsLoading] = useState(false);
  let tags = [];
  if(props.feed.feed){
    if(props.feed.feed.tags != ''){
      if(props.feed.feed.tags.indexOf(",") > -1)
        tags = props.feed.feed.tags.split(',');
      else tags.push(props.feed.feed.tags);
    }
  }
  else{
    if(props.feed.tags.indexOf(",") > -1)
      tags = props.feed.tags.split(',');
    else tags.push(props.feed.tags);
  }

  const enableFeed = () => {
    setIsLoading(true);
    let params = {
      id: props.feed.id,
      groupid: props.currentgroup
    };
    fetch('/api/feedenable', {
      method: 'put',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': props.client.transports[0].auth.csrfToken
      },
      credentials: 'same-origin',
      body: JSON.stringify(params)
    }).then(res=>{return res.json()})
    .then(res=>{
      setIsLoading(false);
      props.saveFeed(res);
    })
  }

  if(isLoading){
    return <Loading />
  }
  else{
    return (
      <section className="section app-card" id={props.index==0?"card":""} style={Styles.FeedStoreCard}>
        <div className="columns">
          <Grid container>
            <Grid item xs={12} md={10}>
              <div>
                <span> Name: </span>
                <span> {props.feed.feed? props.feed.feed.name : props.feed.name} </span>
              </div>
              <div>
                <span> Description: </span>
                <span> {props.feed.feed? props.feed.feed.description: props.feed.description} </span>
              </div>
              <div>
                <span> URL: </span>
                <span> {props.feed.feed? props.feed.feed.url : props.feed.url} </span>
              </div>
              <div>
                <span>
                  <button className="button is-primary is-rounded mx-1" >
                    <span>{props.feed.feed ? props.feed.feed.category.name : props.feed.category.name}</span>
                  </button>
                  {
                    tags.length > 0 && tags.map((tag, index) => {
                      return (
                        <button key={index} className="button is-info is-rounded mx-1" >
                          <span>{tag}</span>
                        </button>
                      );
                    })
                  }
                </span>
              </div>
            </Grid>
            <Grid item xs={12} md={2} className="has-text-centered" >
              <Link to="/feeds" >
                {Boolean(props.feed.feed)?
                <button className="button is-fullwidth is-static" id={props.index==0?"button":""}>
                  <span className="is-size-4">Enabled</span>
                </button>:
                <button className="button is-fullwidth is-success" id={props.index==0?"button":""} onClick={enableFeed}>
                  <span className="is-size-4">Enable</span>
                </button>}
              </Link>
              {props.feed.feed?
              <Link to="/feedlist" className="button is-text">
                <span>See in feed list</span>
              </Link>:
              <Link to={`/feeds/${props.feed.uniqueid}`} className="button is-text">
                <span>Custom settings and enable</span>
              </Link>}
            </Grid>
          </Grid>
        </div>
      </section>
    );
  }
}

export default FeedCard;
