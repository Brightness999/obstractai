import React from "react";
import {Link} from "react-router-dom";
import { Grid } from "@material-ui/core";

const ReportCard = function (props) {
	let tags = [];
	if(props.feed[0]){
		if(props.feed[0].tags.indexOf(",") > -1)
		tags = props.feed[0].tags.split(',');
		else tags.push(props.feed[0].tags);
	}
	return (
		<section className="section app-card" >
			<div className="columns">
				<div className="column is-one-thirds">
					<Grid container>
						<Grid item xs={12} md={8} className="container">
							<Grid container>
								<Grid item xs={12} md={6}>
									<div>
										<span> Name: </span>
										<span> {props.feed[0]? props.feed[0].name : ""} </span>
									</div>
									<div>
										<span> Description: </span>
										<span> {props.feed[0]? props.feed[0].description: ""} </span>
									</div>
									<div className="">
										<span> URL: </span>
										<span> {props.feed[0]? props.feeditem.link : ""} </span>
									</div>

								</Grid>
								<Grid item xs={12} md={6}>
									<div>
										<span> Publish Date: </span>
										<span> {props.feed[0]? props.feed[0].updated_at.split('.')[0].split('T')[0]+" "+props.feed[0].updated_at.split('.')[0].split('T')[1] : ""} </span>
									</div>
								</Grid>
							</Grid>
							<div>
								<span>
									<button className="button is-info is-rounded mx-2" >
									<span>{props.feed[0].category ? props.feed[0].category.name : ""}</span>
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
									<Link to={`/intelreports/${props.feeditem.id}`}>
										<button className="button is-link is-rounded is-text mx-2">
											<span>{props.feed[0] ? props.feed[0].name : ""}</span>
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
										<span>{props.feed[0].confidence}</span>
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
