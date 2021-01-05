import React from "react";
import {Link} from "react-router-dom";
import {
  Grid
} from "@material-ui/core";

import Styles from "../styles";

const FeedCard = function (props) {
  let tags = [];
  if(props.feed){
    if(props.feed.tags.indexOf(",") > -1)
      tags = props.feed.tags.split(',');
    else tags.push(props.feed.tags);
  }
  return (
    <section className="section app-card" style={Styles.FeedStoreCard}>
      <div className="columns">
        <div className="column is-one-thirds">
          <Grid container>
            <Grid item xs={10}>
              <div>
                <span> Name: </span>
                <span> {props.feed? props.feed.name : ""} </span>
              </div>
              <div>
                <span> Description: </span>
                <span> {props.feed? props.feed.description: ""} </span>
              </div>
              <div>
                <span> URL: </span>
                <span> {props.feed? props.feed.url : ""} </span>
              </div>
              <div>
                <span>
                  <button className="button is-outlined" style={Styles.FeedStoreCategoryButton}>
                    <span>{props.feed.category ? props.feed.category.name : ""}</span>
                  </button>
                  {
                    tags.map((tag, index) => {
                      return (
                        <button key={index} className="button is-outlined" style={Styles.FeedStoreTagButton}>
                          <span>{tag}</span>
                        </button>
                      );
                    })
                  }
                </span>
              </div>
            </Grid>
            <Grid item xs={2}>
              <Link to="/feeds" >
                <button className="button is-outlined" style={props.feed.manage_enabled == 'true'? Styles.FeedStoreEnableButton: Styles.FeedStoreDisableButton}>
                <span>{props.feed.manage_enabled == 'true'? "Enable": "Disable"}</span>
                </button>
              </Link>
              <Link to={`/feeds/edit/${props.feed.id}`} style={Styles.FeedStoreLink}>
                <span>{props.feed.manage_enabled == 'true'? "Custom settings and enable" : "See in feed list"}</span>
              </Link>
            </Grid>
          </Grid>
        </div>
      </div>
      {/* <Button variant="contained" style={Styles.FeedAddButton} onClick={() => updateFeed()}>
        { props.id ? 'Enable' : 'Add New Feed'}
      </Button> */}
    </section>
  );
}

export default FeedCard;
