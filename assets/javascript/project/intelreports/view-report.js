import React, { useState, useEffect } from "react";
import { Link, useHistory } from "react-router-dom";
import { Container, Grid, Tooltip } from "@material-ui/core";

import Styles from "../styles";

const ViewReport = (props) => {
	console.log(props);
	const history = useHistory();
	let tags = [];
	if(props.feed.tags){
		if(props.feed.tags.indexOf(",") > -1)
		tags = props.feed.tags.split(',');
		else tags.push(props.feed.tags);
	}
	const itemfeed = [];
	props.feeds.forEach(feed => {
		if(feed.uniqueid == props.feed.uniqueid){
			itemfeed.push(feed);
		}
	});
	const classifications = [];
	props.classifications.forEach(classification => {
		if(classification.intelgroup_id == itemfeed[0].intelgroup_id){
			classifications.push(classification);
		}
	});
	const indicators = [];
	props.indicators.forEach(indicator => {
		if(props.id == indicator.feeditem_id){
			indicators.push(indicator)
		}
	});
	const currentitem = [];
	props.feeditems.forEach(feeditem => {
		if(feeditem.id == props.id){
			currentitem.push(feeditem);
		}
	});
	
	useEffect(()=>{
		let str=currentitem[0].description;
		indicators.forEach(indicator => {
			if(indicator.globalindicator.value == 'URL' || indicator.globalindicator.value == 'Email Address'){
				let items = indicator.value.split(',');
				items.forEach(item => {
					let astartreg = /<a/gi, alastreg = /a>/gi, result, astart = [], alast = [];
					while ( (result = astartreg.exec(str)) ) {
						astart.push(result.index);
					}
					while ( (result = alastreg.exec(str)) ) {
						alast.push(result.index);
					}
					let url = item.replace("(", "").replace(/'/gi, "").replace(")", "").replace(/\\/gi, "").trim();
					let re = new RegExp(url);
					let index = str.search(re);
					for(let i=0;i<astart.length;i++){
						let target = '';
						if(index>astart[i] && index<alast[i]){
							target = str.substring(astart[i], alast[i]+2);
							let target1 = target.substring(0,2) + " style='background:#faeb42;'" + target.substr(2);
							str = str.replace(target, `<Tooltip title="${indicator.globalindicator.value_api}=${url}" arrow>${target1}</Tooltip>`)
						}
					}
				});
			}
		});
		let words = [];
		classifications.forEach(classification => {
			if(classification.words_matched.indexOf(",")>-1){
				let temp = classification.words_matched.split(",");
				words = words.concat(temp);
			}
			else words.push(classification.words_matched);
		});
		words.forEach(word => {
			let reg = new RegExp(word.trim(), 'g');
			str = str.replace(reg, `<span style="background:#00e7ff;">${word.trim()}</span>`)
		});
		document.querySelector("#extraction").innerHTML=str;

	},[]);
	return (
		<Container>
			<section className="section">
				<Grid container>
					<Grid item xs={3}>
						<h1 className="title is-2">Report Name</h1>
						<label>Item short description</label>
					</Grid>
					<Grid item xs={9}>
						<span>
							<button className="button is-outlined" style={Styles.FeedStoreCategoryButton}>
								<span>{props.feed.category.name}</span>
							</button>
							{tags.map((tag, index)=>{
								return <button key={index} className="button is-outlined" style={Styles.FeedStoreTagButton}>
									<span>{tag}</span>
								</button>
							})}
							<button className="button is-outlined" style={Styles.ReportFeedNameButton}>
								<span>{props.feed.name}</span>
							</button>
							<button className="button is-outlined ml-4" style={Styles.ReportConfidenceButton}>
								<span>{props.feed.confidence}</span>
							</button>
						</span>
					</Grid>
				</Grid>
			</section>
			<section className="section">
				<button className="button is-light is-pulled-left" onClick={()=>history.goBack()}>Back</button>
			</section>
			<section>
				<Grid container>
					<Grid item xs={12} id="extraction">
						
					</Grid>
					<Grid item xs={12} className="section">
						<section className="section app-card">
							<Grid container>
								<Grid item xs={3} className="pt-4">
									<span>Confidence:</span>
								</Grid>
								<Grid item xs={9} className="py-2">
									<button className="button is-outlined" style={Styles.ReportConfidenceButton}>
										<span>{props.feed.confidence}</span>
									</button>
								</Grid>
							</Grid>
							<Grid container>
								<Grid item xs={3} className="pt-4">
									<span>Observables:</span>
								</Grid>
								<Grid item xs={9}>
									{classifications.map((classification, index)=>{
										return <button key={index} className="button is-outlined" style={Styles.ReportObservableButton}>
											<span>{classification.words_matched}</span>
										</button>
									})}
								</Grid>
							</Grid>
							<Grid container>
								<Grid item xs={3} className="pt-4">
									<span>Indicators:</span>
								</Grid>
								<Grid item xs={9} className="py-2">
									{indicators.map((indicator, index)=>{
										return <button key={index} className="button is-outlined" style={Styles.ReportIndicatorButton}>
											<span>{indicator.globalindicator.value}</span>
										</button>
									})}
								</Grid>
							</Grid>
							<p>JSON object: </p>
							<p>API call</p>
							<div>
								<span>Feed: </span>
								<span>https://www.cyobstract.com/api/v1/report</span>
							</div>
							<div>
								<span>Object: </span>
								<span>https://www.cyobstract.com/api/v1/report</span>
							</div>
							<a href="/docs" className="muted-link">API docs</a>
						</section>
					</Grid>
				</Grid>
			</section>
		</Container>
	);
}

export default ViewReport;