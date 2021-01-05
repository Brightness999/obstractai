import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Grid, Paper } from "@material-ui/core";

import Styles from "../styles";

const Plan = (props) => {
    return (
        <Grid item xs={4}>
            <Paper elevation={5} >
                <div className="section">
                    <h1 className="has-text-centered">YOUR CURRENT PLAN</h1>
                    <Grid container className="section" style={Styles.SectionStyle}>
                        <Grid item xs={6}>
                            <span>Plan Name</span>
                        </Grid>
                        <Grid item xs={6} className="has-text-centered">
                            <span>{props.plan.name}</span>
                        </Grid>
                    </Grid>
                    <Grid container className="section" style={Styles.SectionStyle}>
                        <Grid item xs={6}>
                            <span>Maximum feeds allowed</span>
                        </Grid>
                        <Grid item xs={6} className="has-text-centered">
                            <span>{props.plan.max_feeds}</span>
                        </Grid>
                    </Grid>
                    <Grid container className="section" style={Styles.SectionStyle}>
                        <Grid item xs={6}>
                            <span>Maximum users in group</span>
                        </Grid>
                        <Grid item xs={6} className="has-text-centered">
                            <span>{props.plan.max_users}</span>
                        </Grid>
                    </Grid>
                    <Grid container className="section" style={Styles.SectionStyle}>
                        <Grid item xs={6}>
                            <span>Custom feeds allowed</span>
                        </Grid>
                        <Grid item xs={6} className="has-text-centered">
                            <span>{props.plan.enabled_custom_feeds}</span>
                        </Grid>
                    </Grid>
                    <Grid container className="section" style={Styles.SectionStyle}>
                        <Grid item xs={6}>
                            <span>Custom observable mapping allowed</span>
                        </Grid>
                        <Grid item xs={6} className="has-text-centered">
                            <span>{props.plan.enabled_custom_extraction}</span>
                        </Grid>
                    </Grid>
                    <Grid container className="section" style={Styles.SectionStyle}>
                        <Grid item xs={6}>
                            <span>API access</span>
                        </Grid>
                        <Grid item xs={6} className="has-text-centered">
                            <span>{props.plan.enabled_api}</span>
                        </Grid>
                    </Grid>
                    <Grid container className="section" style={Styles.SectionStyle}>
                        <Grid item xs={6}>
                            <span>Cost</span>
                        </Grid>
                        <Grid item xs={6} >
                            <p>${props.plan.annual_price/10}/mo {props.plan.annual_price != 0 && "(billed annually)"} </p>
                            <p>{props.plan.annual_price != 0 && '$'+props.plan.monthly_price+'(billed monthly)'} </p>
                        </Grid>
                    </Grid>
                    <div className="section columns is-centered">
                        <Link to="/manageplan/manage">
                            <button className="button is-success"><span>Upgrade to this plan</span></button>
                        </Link>
                    </div>
                </div>
            
            </Paper>

        </Grid>
					
    );
} 

export default Plan;