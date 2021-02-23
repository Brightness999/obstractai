import React, { useEffect } from "react";
import { Link } from "react-router-dom";
import { Grid } from "@material-ui/core";

const ReportCard = function (props) {
	let tags = [];
	if(props.report.groupfeed){
		if(props.report.groupfeed.tags != ''){
			if(props.report.groupfeed.tags.indexOf(",") > -1)
				tags = props.report.groupfeed.tags.split(',');
			else{
				if(props.report.groupfeed.tags != '')
					tags.push(props.report.groupfeed.tags);
			}
		}
	}
	useEffect(()=>{
		// document.querySelector('#description'+props.index).innerHTML=props.report.feeditem.description;
	},[]);
	return (
		<section className="section app-card" id={props.index==0?"card":""} >
			<div className="columns">
				<div className="column is-one-thirds">
					<Grid container>
						<Grid item xs={12} md={8} className="container" style={{position:'relative'}}>
							<Grid container>
								<Grid item xs={12} md={6}>
									<div>
										<span className="title has-text-weight-bold is-4"> Name: </span>
										<span> {props.report? props.report.feeditem.title : ""} </span>
									</div>
									<div id={`description${props.index}`}>
										<span> Description: </span>
										{/* <span> {props.report? props.report.feeditem.description: ""} </span> */}
									</div>
									<div>
										<span className="title has-text-weight-bold is-4"> URL: </span>
										<span> {props.report.feeditem? props.report.feeditem.link : ""} </span>
									</div>

								</Grid>
								<Grid item xs={12} md={6}>
									<div>
										<span className="title has-text-weight-bold is-4"> Publish Date: </span>
										<span>{ props.report.feeditem.pubdate && new Date(props.report.feeditem.pubdate).toLocaleString()}</span>
									</div>
								</Grid>
							</Grid>
							<div>
								<span>
									<button className="button is-info is-rounded mx-2" >
									<span>{props.report.groupfeed.category ? props.report.groupfeed.category.name : ""}</span>
									</button>
									{tags!=[] && tags.map((tag, index) => {
										return (
										<button key={index} className="button is-warning is-rounded mx-2" >
											<span>{tag}</span>
										</button>
										);
									})}
									<button className="button is-link is-rounded mx-2">
										<span>{props.report.groupfeed ? props.report.groupfeed.name : ""}</span>
									</button>
								</span>
							</div>
							<div>
								<Link to={`/intelreports/${props.report.uniqueid}`}>
									<button className="button is-danger is-medium is-rounded mx-2 my-4">
										<span>View intel</span>
									</button>
								</Link>
							</div>
						</Grid>
						<Grid item xs={12} md={4}>
							<Grid container>
								<Grid item xs={3} className="pt-4">
									<span>Confidence:</span>
								</Grid>
								<Grid item xs={9} className="py-2">
									<button className="button is-primary is-rounded">
										<span>{props.report.groupfeed.confidence}</span>
									</button>
								</Grid>
							</Grid>
							<Grid container>
								<Grid item xs={3} className="pt-4">
									<span>Observables:</span>
								</Grid>
								<Grid item xs={9} className="py-2">
									{props.classifications.map((classification, index)=>{
										return <button key={index} className="button is-warning is-rounded mx-1 my-1">
											<span>{classification.words_matched}</span>
										</button>
									})}
									{props.globalattributes.map((classification, index)=>{
										return <button key={index} className="button is-warning is-rounded mx-1 my-1">
											<span>{classification.globalattribute.words_matched}</span>
										</button>
									})}
								</Grid>
							</Grid>
							<Grid container>
								<Grid item xs={3} className="pt-4">
									<span>Indicators:</span>
								</Grid>
								<Grid item xs={9} className="py-2">
									{props.indicators.map((indicator, index)=>{
										return <button key={index} className="button is-success is-rounded mx-1	my-1" >
											<span>{indicator.globalindicator.value}</span>
										</button>
									})}
								</Grid>
							</Grid>
						</Grid>
				</Grid>
				</div>
			</div>
		</section>
	);
}

export default ReportCard;
