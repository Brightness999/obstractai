import React from "react";
import { Link } from "react-router-dom";
import { Grid } from "@material-ui/core";

const ReportCard = function (props) {
	let tags = [];
	if(props.report.feed){
		if(props.report.feed.tags.indexOf(",") > -1)
		tags = props.report.feed.tags.split(',');
		else tags.push(props.report.feed.tags);
	}
	return (
		<section className="section app-card" >
			<div className="columns">
				<div className="column is-one-thirds">
					<Grid container>
						<Grid item xs={12} md={8} className="container" style={{position:'relative'}}>
							<Grid container>
								<Grid item xs={12} md={6}>
									<div>
										<span> Name: </span>
										<span> {props.report? props.report.feeditem.title : ""} </span>
									</div>
									<div>
										<span> Description: </span>
										<span> {props.report? props.report.feed.description: ""} </span>
									</div>
									<div className="">
										<span> URL: </span>
										<span> {props.report.feeditem? props.report.feeditem.link : ""} </span>
									</div>

								</Grid>
								<Grid item xs={12} md={6}>
									<div>
										<span> Publish Date: </span>
										<span>{ props.report.feeditem.pubdate && new Date(props.report.feeditem.pubdate).toLocaleString()}</span>
									</div>
								</Grid>
							</Grid>
							<div style={{position:'absolute', bottom:0}}>
								<span>
									<button className="button is-info is-rounded mx-2" >
									<span>{props.report.feed.category ? props.report.feed.category.name : ""}</span>
									</button>
									{
									tags.map((tag, index) => {
										return (
										<button key={index} className="button is-warning is-rounded mx-2" >
											<span>{tag}</span>
										</button>
										);
									})
									}
									<Link to={`/intelreports/${props.report.id}`}>
										<button className="button is-link is-rounded is-text mx-2">
											<span>{props.report.feed ? props.report.feed.name : ""}</span>
										</button>
									</Link>
								</span>
							</div>
						</Grid>
						<Grid item xs={12} md={4}>
							<Grid container>
								<Grid item xs={3} className="pt-4">
									<span>Confidence:</span>
								</Grid>
								<Grid item xs={9} className="py-2">
									<button className="button is-primary is-rounded">
										<span>{props.report.feed.confidence}</span>
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
